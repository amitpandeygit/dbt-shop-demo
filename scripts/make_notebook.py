"""Writes dbt_demo.ipynb (the Colab notebook used for the live demo)."""
import nbformat as nbf
nb = nbf.v4.new_notebook()
C = []
def md(s): C.append(nbf.v4.new_markdown_cell(s.strip()))
def code(s):
    s = s.strip()
    if "{{" in s and not s.startswith("%%"):
        # In Colab, a line starting with ! treats {x} as a Python variable and breaks Jinja.
        # A %%bash cell passes the text to the shell unchanged.
        s = "%%bash\n" + "\n".join(l[1:] if l.startswith("!") else l for l in s.split("\n"))
    C.append(nbf.v4.new_code_cell(s))

md("""
# dbt demo: from raw shop data to analytics tables

Run the cells from top to bottom (Shift + Enter). Each section matches one part of the session.

The business: a small online shop in India. Raw data: 300 customers, 2,000 orders (Jan to Jun 2026), product lines and payments.
The warehouse: DuckDB, a small database that lives in one file (`shop.duckdb`). The same dbt project works on BigQuery or Snowflake by changing only `profiles.yml`.
""")
md("## Setup (about 1 minute)")
code("""
# Get the project, install dbt, and load the raw data (the "E" and "L" of ELT)
# Running this cell again starts the whole demo from a clean copy.
%cd /content
!rm -rf dbt-shop-demo
!git clone -q https://github.com/amitpandeygit/dbt-shop-demo.git
%cd /content/dbt-shop-demo
!pip install -q -r requirements.txt
!apt-get -qq install -y tree > /dev/null
!python scripts/load_raw.py
""")
md("""
## Section 1 - dbt and modern ELT

ETL transforms data before loading it. ELT loads raw data into the warehouse first and transforms it there. dbt is the "T": it runs SQL `select` statements inside the warehouse and saves the results as views or tables.

**raw data -> sources -> staging -> intermediate -> marts -> tests -> docs**

Here is the raw data, exactly as the shop's app stored it. Look at the messy parts: upper and lower case status, spaces in emails and cities, money in paise.
""")
code("""!dbt show --inline "select * from {{ source('shop', 'orders') }}" --limit 5""")
code("""!dbt show --inline "select customer_id, email, city from {{ source('shop', 'customers') }} where customer_id in (7, 14, 3)" """)
md("## Section 2 - the dbt project, sources and models")
code("""!tree -I 'target|logs|data|scripts|*.ipynb' --dirsfirst""")
code("""!cat dbt_project.yml""")
code("""
!cat profiles.yml
!dbt debug
""")
md("**Sources** - the raw tables, declared once. Models then use `source('shop', 'orders')` instead of a hard-coded table name.")
code("""!cat models/staging/_sources.yml""")
md("**A staging model** - one clean row per raw row. Only light cleaning: rename, fix case, trim spaces, paise to rupees.")
code("""
!cat models/staging/stg_orders.sql
# Build the four staging models (everything in the staging folder)
!dbt run -s staging
!dbt show -s stg_orders --limit 5
""")
md("**A downstream model with `ref()`** - `ref('stg_order_items')` points to another model. dbt reads every `ref()` and builds the dependency graph (the DAG) from them.")
code("""!cat models/intermediate/int_order_items_summed.sql""")
code("""
# Everything fct_orders depends on (the + in front means "and its parents")
!dbt ls -s +fct_orders
""")
code("""
# Build everything. dbt works out the order from the DAG: seeds and staging first, marts last.
!dbt seed
!dbt run
""")
md("**The lineage graph.** Generate the documentation site and open it. Click the round button at the bottom right to see the DAG.")
code("""
!dbt docs generate -q
!nohup dbt docs serve --port 8080 --no-browser > docs.log 2>&1 &
from google.colab import output
output.serve_kernel_port_as_window(8080)
""")
md("## Section 3 - transformations, dependencies and materialisations")
code("""!cat models/marts/fct_orders.sql""")
code("""!cat models/marts/dim_customers.sql""")
code("""
!cat models/marts/rpt_monthly_sales_by_region.sql
!dbt show -s rpt_monthly_sales_by_region --limit 8
""")
md("""
**Materialisations** - how dbt saves a model in the warehouse.

| Materialisation | What dbt creates | Used here for |
|---|---|---|
| view | a saved query; runs every time someone reads it | staging |
| table | the data itself, rebuilt on every run | marts |
| incremental | a table that only adds new or changed rows | fct_orders |
| ephemeral | nothing; pasted into other models as a CTE | intermediate |
""")
code("""!dbt show --inline "select table_schema, table_name, table_type from information_schema.tables where table_schema like 'dev%' order by 1, 2" --limit 20""")
md("Ephemeral models are not in the list above. They are pasted into `fct_orders` as CTEs. See the compiled SQL:")
code("""!dbt compile -s fct_orders | head -40""")
md("**Change a materialisation.** Add one line at the top of `stg_orders.sql` and run it again. The view becomes a table.")
code("""
%%writefile models/staging/stg_orders.sql
{{ config(materialized='table') }}
-- Staging: one clean row per order.
select
    order_id,
    customer_id,
    order_date,
    lower(status)   as status,
    updated_at
from {{ source('shop', 'orders') }}
""")
code("""
!dbt run -s stg_orders
!dbt show --inline "select table_name, table_type from information_schema.tables where table_name = 'stg_orders'"
""")
code("""
# Put it back to a view (the folder default from dbt_project.yml)
!git checkout models/staging/stg_orders.sql
!dbt run -s stg_orders
""")
md("""
**Incremental models.** Before new data arrives, take a first snapshot of customers (we use it in Section 4).
Then load batch 2: 150 new orders, 40 old orders that changed from shipped to delivered, and one customer who moved city.
""")
code("""
!dbt snapshot
!dbt show --inline "select count(*) as orders, max(updated_at) as newest from {{ ref('fct_orders') }}"
!python scripts/load_raw.py 2
""")
code("""
# Only rows changed after the newest updated_at already in the table are processed
!dbt run -s fct_orders
!dbt show --inline "select count(*) as orders, max(updated_at) as newest from {{ ref('fct_orders') }}"
""")
md("2,000 + 150 new = 2,150 rows. The 40 changed orders replaced their old rows (because of `unique_key='order_id'`), so they were not added twice. The SQL that ran had the extra `where`:")
code("""!grep -B2 "where o.updated_at" target/compiled/shop/models/marts/fct_orders.sql""")
code("""
# To rebuild the whole table from scratch:
!dbt run -s fct_orders --full-refresh
""")
md("## Section 4 - tests, documentation and advanced dbt")
code("""!cat models/staging/_staging.yml""")
code("""!dbt test""")
md("One test failed. Look at what is in the status column now:")
code("""!dbt show --inline "select status, count(*) as orders from {{ ref('stg_orders') }} group by 1 order by 2 desc" """)
md("A new status, `refunded`, came in with batch 2. `dbt build` runs models and tests together, in DAG order, and skips everything downstream of a failed test, so bad data does not reach the reports:")
code("""!dbt build""")
md("**The fix:** tell the test that `refunded` is allowed, and count refunded orders as zero revenue.")
code("""
!sed -i "s/'cancelled', 'returned'\\]/'cancelled', 'returned', 'refunded']/" models/staging/_staging.yml
!sed -i "s/when o.status in ('cancelled', 'returned') then 0/when o.status in ('cancelled', 'returned', 'refunded') then 0/" models/marts/fct_orders.sql
!grep -n "refunded" models/staging/_staging.yml models/marts/fct_orders.sql
!dbt build
""")
md("**A singular test** is just a query that should return no rows:")
code("""!cat tests/assert_paid_equals_items.sql""")
md("**Documentation.** Descriptions live in the YAML files next to the models. `docs.md` holds longer text blocks.")
code("""
!cat models/marts/_marts.yml
!cat models/docs.md
""")
code("""
!dbt docs generate -q
output.serve_kernel_port_as_window(8080)
""")
md("**Jinja** - `{% ... %}` runs logic, `{{ ... }}` prints a value. This for-loop writes four columns:")
code("""!cat models/intermediate/int_order_payments_pivoted.sql""")
code("""!dbt compile -s int_order_payments_pivoted""")
md("**A macro** - a reusable piece of SQL, like a function:")
code("""
!cat macros/paise_to_rupees.sql
!cat models/staging/stg_payments.sql
!dbt compile -s stg_payments
""")
md("**Seeds** - a small fixed CSV kept in the repo. `dim_customers` joins it with `ref('city_region')`.")
code("""
!cat seeds/city_region.csv
!dbt show -s dim_customers --limit 5
""")
md("**Snapshots** - keep history. Customer 5 moved from Chennai to Bengaluru in batch 2.")
code("""
!cat snapshots/snap_customers.yml
!dbt snapshot
!dbt show --inline "select customer_id, city, dbt_valid_from, dbt_valid_to from {{ ref('snap_customers') }} where customer_id = 5"
""")
md("""
## Section 5 - conclusion

| If your question sounds like... | Use |
|---|---|
| How do I turn raw warehouse data into analytics-ready tables? | dbt models |
| How do I say where my raw data comes from? | sources |
| How do I connect one transformation to another? | `ref()` and the DAG |
| How do I check the quality of the data? | tests |
| How do I reuse SQL logic? | Jinja and macros |
| How do I explain my transformations to others? | docs and lineage |
| How do I process only new data in a big table? | incremental models |
| Where is the data stored? | the data warehouse |
| How does data get into the warehouse? | ingestion tools (here: `load_raw.py`) |
| How do I run this every night? | an orchestrator (Airflow, Dagster, dbt Cloud jobs) |

**raw data -> sources -> staging -> intermediate -> marts -> tests -> docs -> production**

To start again from the beginning, run the Setup cell's last line: `!python scripts/load_raw.py`.
""")
nb["cells"] = C
nb.metadata["colab"] = {"provenance": [], "name": "dbt_demo.ipynb"}
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3"}
nbf.write(nb, "dbt_demo.ipynb")
print(len(C), "cells")
