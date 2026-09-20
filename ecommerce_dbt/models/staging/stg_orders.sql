select orders.order_id,
       orders.customer_id,
       orders.order_date,
       orders.status
       from {{source('raw','orders')}}
       where status != 'cancelled'