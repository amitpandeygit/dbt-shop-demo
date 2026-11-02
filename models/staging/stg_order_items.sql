-- Staging: one row per product line, with money in rupees.
select
    order_item_id,
    order_id,
    product_id,
    product_name,
    category,
    quantity,
    {{ paise_to_rupees('unit_price_paise') }}              as unit_price,
    {{ paise_to_rupees('quantity * unit_price_paise') }}   as line_amount
from {{ source('shop', 'order_items') }}
