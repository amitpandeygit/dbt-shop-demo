-- Staging: one clean row per customer. Only light cleaning: rename, trim, fix case.
select
    customer_id,
    first_name || ' ' || last_name   as customer_name,
    {{ clean_text('email') }}        as email,
    {{ clean_text('city') }}         as city,
    signup_date,
    updated_at
from {{ source('shop', 'customers') }}
