-- Mart: one row per order with its items and payments. Built incrementally:
-- the first run builds every order; later runs only process orders that are new or changed.
{{ config(materialized='incremental', unique_key='order_id') }}

select
    o.order_id,
    o.customer_id,
    o.order_date,
    o.status,
    i.item_lines,
    i.units,
    i.items_amount,
    p.upi_amount,
    p.card_amount,
    p.cod_amount,
    p.wallet_amount,
    p.total_paid,
    case when o.status in ('cancelled', 'returned') then 0
         else i.items_amount end                        as net_revenue,
    o.updated_at
from {{ ref('stg_orders') }} as o
left join {{ ref('int_order_items_summed') }} as i on o.order_id = i.order_id
left join {{ ref('int_order_payments_pivoted') }} as p on o.order_id = p.order_id

{% if is_incremental() %}
-- Only on later runs: take orders changed after the newest one already in this table
where o.updated_at > (select max(updated_at) from {{ this }})
{% endif %}
