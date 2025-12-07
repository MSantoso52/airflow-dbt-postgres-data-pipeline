{{ config(materialized='table') }}
with customerrevenue as(
  select
    c.customer_id,
    c.full_name as customername,
    count(distinct o.order_id) as ordercount,
    sum(oi.item_quantity * oi.item_unit_price) as revenue
  from customers c
  join orders o on c.customer_id = o.customer_id
  join orderitems oi on o.order_id = oi.order_id
  group by
    c.customer_id,
    c.full_name
  order by
    ordercount,
    revenue
    desc
)

select customer_id, customername, ordercount, revenue
from customerrevenue
