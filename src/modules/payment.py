import random
from modules import config
from cashfree_pg.models.create_order_request import CreateOrderRequest
from cashfree_pg.api_client import Cashfree
from cashfree_pg.models.customer_details import CustomerDetails
from cashfree_pg.models.order_meta import OrderMeta

Cashfree.XClientId = config.XClientId
Cashfree.XClientSecret = config.XClientSecret
Cashfree.XEnvironment = Cashfree.PRODUCTION
x_api_version = "2023-08-01"

def create_token(range:int=10):
    return ''.join(random.choices('0123456789ABCDEFGHIJKDL', k=range))

def create_order(customer_id:str, customer_name:str, customer_ph:str="8474090589", order_id:str=None, amount:int=1, currency:str="INR"):
    order_id = order_id or str(customer_id) + create_token(10)
    customerDetails = CustomerDetails(customer_id=str(customer_id), customer_phone=str(customer_ph), customer_name=customer_name)
    createOrderRequest = CreateOrderRequest(order_id=order_id, order_amount=amount, order_currency=currency, customer_details=customerDetails)
    orderMeta = OrderMeta()
    orderMeta.return_url = f"https://{config.DOMAIN}/payment_checkout"
    orderMeta.notify_url = f"https://{config.DOMAIN}/api/payment/webhook"
    createOrderRequest.order_meta = orderMeta
    try:
        api_response = Cashfree().PGCreateOrder(x_api_version, createOrderRequest, None, None)
        # print(dict(api_response.data)["payment_session_id"])
        with open ("data.txt", "w") as f:
            f.write(str(dict(api_response.data)))
        return dict(api_response.data)

    except Exception as e:
        print(e)
        return None

