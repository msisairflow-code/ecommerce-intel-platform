select
    o.customer_id,
    count(*) as total_orders,
    sum(oi.quantity * oi.price_at_purchase) as total_spent
from {{ ref('stg_orders') }} o
join {{ source('raw', 'order_items') }} oi on o.order_id = oi.order_id
group by o.customer_id