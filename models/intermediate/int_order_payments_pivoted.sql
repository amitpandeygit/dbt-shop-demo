-- Intermediate: one row per order, one column per payment method.
-- The Jinja for-loop writes the four "sum(case ...)" lines for us.
{% set payment_methods = ['upi', 'card', 'cod', 'wallet'] %}

select
    order_id,
    {% for method in payment_methods %}
    sum(case when payment_method = '{{ method }}' then amount else 0 end) as {{ method }}_amount,
    {% endfor %}
    sum(amount) as total_paid
from {{ ref('stg_payments') }}
group by order_id
