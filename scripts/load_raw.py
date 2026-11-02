"""Pretend to be the ingestion tool (the "E" and "L" of ELT).
dbt does not load data. Something else copies raw data into the warehouse,
and dbt then transforms it inside the warehouse. Here, this script plays that part.

  python scripts/load_raw.py          load batch 1 (first 6 months) - deletes shop.duckdb and starts fresh
  python scripts/load_raw.py 2        load batch 2 (next 2 weeks) on top of batch 1
"""
import os
import sys
import duckdb

DB = "shop.duckdb"
TABLES = {"customers": "customer_id", "orders": "order_id", "order_items": None, "payments": None}

batch = sys.argv[1] if len(sys.argv) > 1 else "1"
if batch == "1":  # start again from nothing, so the demo can be repeated
    for f in (DB, DB + ".wal"):
        if os.path.exists(f):
            os.remove(f)
con = duckdb.connect(DB)
con.execute("create schema if not exists raw")
for table, key in TABLES.items():
    csv_file = f"data/raw/batch{batch}/{table}.csv"
    read = f"read_csv('{csv_file}', header = true)"
    if batch == "1":
        con.execute(f"create or replace table raw.{table} as select * from {read}")
    else:
        if key:  # a row that changed replaces the old row, like a real source system
            con.execute(f"delete from raw.{table} where {key} in (select {key} from {read})")
        con.execute(f"insert into raw.{table} select * from {read}")
    n = con.execute(f"select count(*) from raw.{table}").fetchone()[0]
    print(f"raw.{table:<12} {n:>5} rows")
con.close()
print(f"Batch {batch} loaded into {DB}")
