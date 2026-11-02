-- Staging: one clean row per order.
select
    order_id,
    customer_id,
    order_date,
    lower(status)   as status,
    updated_at
from {{ source('shop', 'orders') }}
