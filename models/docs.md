{% docs __overview__ %}
# Shop analytics - dbt demo

A small online shop in India sells groceries and home goods.
Its app database is copied into the warehouse every day (the `raw` schema).
This dbt project turns those raw tables into clean tables for analysis.

**Flow:** raw tables (sources) -> staging (views) -> intermediate (ephemeral) -> marts (tables) -> tests and docs.

Click **View Lineage Graph** (the round button at the bottom right) to see how the models depend on each other.
{% enddocs %}

{% docs order_status %}
Where the order is now. One of:

| status | meaning |
|---|---|
| placed | the customer has ordered; not shipped yet |
| shipped | on the way |
| delivered | reached the customer |
| cancelled | stopped before delivery |
| returned | the customer sent it back |
{% enddocs %}
