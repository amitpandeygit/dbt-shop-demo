-- A singular test: a plain query that should return no rows.
-- Each order's payments should add up to the value of its products.
select
    order_id,
    items_amount,
    total_paid
from {{ ref('fct_orders') }}
where abs(items_amount - total_paid) > 0.01
