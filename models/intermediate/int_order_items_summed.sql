-- Intermediate: add up the product lines of each order.
select
    order_id,
    count(*)           as item_lines,
    sum(quantity)      as units,
    sum(line_amount)   as items_amount
from {{ ref('stg_order_items') }}
group by order_id
