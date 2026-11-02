-- Mart: one row per customer, with region (from the seed) and order totals.
with order_totals as (
    select
        customer_id,
        min(order_date)    as first_order_date,
        max(order_date)    as last_order_date,
        count(*)           as number_of_orders,
        sum(net_revenue)   as lifetime_value
    from {{ ref('fct_orders') }}
    group by customer_id
)

select
    c.customer_id,
    c.customer_name,
    c.email,
    r.city_name,
    r.state,
    r.region,
    c.signup_date,
    t.first_order_date,
    t.last_order_date,
    coalesce(t.number_of_orders, 0)   as number_of_orders,
    coalesce(t.lifetime_value, 0)     as lifetime_value
from {{ ref('stg_customers') }} as c
left join {{ ref('city_region') }} as r on c.city = r.city
left join order_totals as t on c.customer_id = t.customer_id
