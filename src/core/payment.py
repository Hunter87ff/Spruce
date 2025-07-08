"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2022-present hunter87.dev@gmail.com
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.
 """




import random, string
import datetime
import traceback
import config
from cashfree_pg.models.create_order_request import CreateOrderRequest
from cashfree_pg.api_client import Cashfree
from cashfree_pg.models.customer_details import CustomerDetails
from cashfree_pg.models.order_meta import OrderMeta
Cashfree.XClientId = config.X_CLIENT_ID
Cashfree.XClientSecret = config.X_CLIENT_SECRET
Cashfree.XEnvironment = Cashfree.PRODUCTION
x_api_version = "2023-08-01"

def create_token(range:int=10):
    return ''.join(random.choices(string.ascii_letters.join(string.digits), k=range))


class PaymentOrder:
    """A class to handle the payment order data, currently only configured for Cashfree payloads"""
    def __init__(self, obj:dict):
        self.cf_order_id = obj.get("cf_order_id")
        self.order_id = obj.get("order_id")
        self.order_currency = obj.get("order_currency")
        self.order_amount = obj.get("order_amount")
        self.order_status = obj.get("order_status")
        self.payment_session_id = obj.get("payment_session_id")
        self.order_expiry_time = obj.get("order_expiry_time")
        self.order_note = obj.get("order_note")
        self.created_at = obj.get("created_at")
        self.customer_details = obj.get("customer_details")
        self.order_meta = obj.get("order_meta")
        self.order_tags = obj.get("order_tags")

    @property
    def to_dict(self):
        """Returns the payment details in dict format"""
        return {
            "order_id": self.order_id,
            "order_currency": self.order_currency,
            "order_amount": self.order_amount,
            "order_status": self.order_status,
            "payment_session_id": self.payment_session_id,
            "order_expiry_time": self.order_expiry_time,
            "order_note": self.order_note,
            "created_at": self.created_at,
            "customer_details": self.customer_details,
            "order_meta": self.order_meta,
            "order_tags": self.order_tags
        }


class PaymentHook:
    """A class to handle the payment webhook data, currently only configured for Cashfree payloads

    Parameters
    ----------
    data : dict
        The webhook data

    """
    def __init__(self, data:dict):
        data = data['data']
        self.data = data
        self.guild_id = int(data['customer_details']['customer_id'])
        self.customer_name = str(data['customer_details']['customer_name'])
        self.order_id:str = data['order']['order_id']
        self.payment_id = data['payment']['cf_payment_id']
        self.payment_status:str = data['payment']['payment_status']
        self.payment_amount:float = data['payment']['payment_amount']
        self.payment_currency:str = data['payment']['payment_currency']
        self.payment_time:str = data['payment']['payment_time']
        self.payment_method = data['payment']['payment_method']
        self.payment_group = data['payment']['payment_group']
        self.payment_gateway_details = data['payment_gateway_details']
        self.payment_offers = data['payment_offers']
        self.created_at = datetime.datetime.strptime(self.payment_time, "%Y-%m-%dT%H:%M:%S%z")
        self.end_time = self.created_at + datetime.timedelta(days=30)


    @property
    def to_dict(self):
        """Returns the payment details in dict format"""
        return {
            "guild_id": self.guild_id,
            "customer_name":self.customer_name,
            "order_id": self.order_id,
            "payment_id": self.payment_id,
            "payment_status": self.payment_status,
            "payment_amount": self.payment_amount,
            "payment_currency": self.payment_currency,
            "payment_time": self.payment_time,
            "payment_method": self.payment_method,
            "payment_group": self.payment_group,
            "created_at": self.created_at,
            "end_time": self.end_time
        }



def create_order(customer_id:str, customer_name:str, customer_ph:str="8474090589", order_id:str=None, amount:int=1, currency:str="INR") -> PaymentOrder|None:
    order_id = order_id or str(customer_id) + create_token(10)
    customer_details = CustomerDetails(
        customer_id=str(customer_id), 
        customer_phone=str(customer_ph), 
        customer_name=customer_name
    )
    create_order = CreateOrderRequest(
        order_id=order_id, 
        order_amount=amount, 
        order_currency=currency, 
        customer_details=customer_details
    )
    order_meta = OrderMeta()
    order_meta.return_url =  config.SUPPORT_SERVER
    create_order.order_meta = order_meta
    try:
        api_response = Cashfree().PGCreateOrder(x_api_version, create_order, None, None)
        with open ("data.txt", "w") as f:
            f.write(str(dict(api_response.data)))
        return  PaymentOrder(dict(api_response.data))

    except Exception:
        traceback.print_exc()
        return None



import warnings
from urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter("ignore", InsecureRequestWarning)