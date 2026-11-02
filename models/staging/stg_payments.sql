-- Staging: one row per payment, with money in rupees.
select
    payment_id,
    order_id,
    lower(payment_method)                    as payment_method,
    {{ paise_to_rupees('amount_paise') }}    as amount
from {{ source('shop', 'payments') }}
