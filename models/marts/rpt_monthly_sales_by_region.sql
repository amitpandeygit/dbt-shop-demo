-- Report: sales per month per region. Orders that earned nothing (cancelled, returned) are left out.
select
    cast(date_trunc('month', o.order_date) as date)  as order_month,
    c.region,
    count(*)                                        as orders,
    sum(o.net_revenue)                              as revenue,
    round(sum(o.net_revenue) / count(*), 2)         as avg_order_value
from {{ ref('fct_orders') }} as o
join {{ ref('dim_customers') }} as c on o.customer_id = c.customer_id
where o.net_revenue > 0
group by 1, 2
order by 1, 2
