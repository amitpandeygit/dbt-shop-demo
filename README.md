# dbt demo - shop analytics

A small dbt project for learning how dbt turns raw warehouse data into clean tables for analysis.
It uses DuckDB as the warehouse, so it runs in the browser in Google Colab or GitHub Codespaces. Nothing to install, no cloud account, no keys.

The business: a small online shop in India that sells groceries and home goods.
Raw data: 300 customers, 2,000 orders (January to June 2026), their product lines and payments.

## Open it

**Google Colab (easiest):** open [dbt_demo.ipynb in Colab](https://colab.research.google.com/github/amitpandeygit/dbt-shop-demo/blob/main/dbt_demo.ipynb) and run the cells from top to bottom. The notebook follows the session section by section.

**GitHub Codespaces:** click the green **Code** button, then the **Codespaces** tab, then **Create codespace on main**. Wait 2 to 3 minutes while it installs dbt and loads the raw data, then run `dbt build` in the terminal.

## The flow

```
raw tables  ->  staging  ->  intermediate  ->  marts          ->  tests and docs
(sources)       (views)      (ephemeral)       (tables)
```

| Folder | What is in it |
|---|---|
| `data/raw/` | The raw CSV files. `batch1` = first 6 months. `batch2` = the next 2 weeks. |
| `scripts/load_raw.py` | Plays the ingestion tool: loads the CSVs into the `raw` schema. dbt itself does not load data. |
| `models/staging/` | One clean view per raw table. `_sources.yml` declares the raw tables. |
| `models/intermediate/` | Ephemeral helper models (they become CTEs, not tables). One uses a Jinja for-loop. |
| `models/marts/` | Final tables: `fct_orders` (incremental), `dim_customers`, `rpt_monthly_sales_by_region`. |
| `seeds/city_region.csv` | Small fixed list: city to state and region. |
| `snapshots/snap_customers.yml` | Keeps the history of customer changes. |
| `macros/` | Reusable SQL: `paise_to_rupees`, `clean_text`. |
| `tests/` | A singular test: payments must equal the order value. |
| `dbt_project.yml` | Project settings and default materialisations per folder. |
| `profiles.yml` | The connection: one DuckDB file. |

## Commands used in the demo

```bash
python scripts/load_raw.py        # load batch 1 (starts fresh every time)
dbt debug                         # check the connection
dbt seed                          # load seeds/city_region.csv
dbt run                           # build all models
dbt test                          # run all tests
dbt build                         # seed + run + snapshot + test, in DAG order
dbt show -s dim_customers         # look at the data in a model
dbt ls -s +fct_orders             # what fct_orders depends on
python scripts/load_raw.py 2      # load batch 2 (new orders, changes, a new status)
dbt run -s fct_orders             # incremental run: only new and changed orders
dbt snapshot                      # record customer changes
dbt docs generate && dbt docs serve --port 8080   # documentation site with lineage graph
```

Batch 2 brings a new order status, `refunded`, that the tests do not know about yet. `dbt test` fails on purpose, to show how tests catch data problems.

## Run on your own computer (optional)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/load_raw.py
dbt build
```
