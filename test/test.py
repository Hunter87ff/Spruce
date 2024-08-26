
import datetime
from cashfree_pg.models.customer_details import CustomerDetails
from cashfree_pg.models.order_meta import OrderMeta


class PaymentHook:
    """A class to handle the payment webhook data, currently only configured for Cashfree payloads

    Parameters
    ----------
    data : dict
        The webhook data

    """
    def __init__(self, data:dict):
        self.data = data
        self.__guild_id = data['customer_details']['customer_id']
        self.__customer_name = data['customer_details']['customer_name']
        self.__order_id = data['order']['order_id']
        self.__payment_id = data['payment']['cf_payment_id']
        self.__payment_status = data['payment']['payment_status']
        self.__payment_amount = data['payment']['payment_amount']
        self.__payment_currency = data['payment']['payment_currency']
        self.__payment_time = data['payment']['payment_time']
        self.__payment_method = data['payment']['payment_method']
        self.__payment_group = data['payment']['payment_group']
        self.__payment_gateway_details = data['payment_gateway_details']
        self.__payment_offers = data['payment_offers']
        self.__created_at = datetime.datetime.strptime(self.payment_time, "%Y-%m-%dT%H:%M:%S%z")
        self.__end_time = self.__created_at + datetime.timedelta(days=30)

    @property
    def guild_id(self):
        """Returns the guild_id of the payment"""
        return self.__guild_id
    
    @property
    def customer_name(self):
        """Returns the customer_name of the payment"""
        return self.__customer_name
    
    @property
    def order_id(self):
        """Returns the order_id of the payment"""
        return self.__order_id
    
    @property
    def payment_id(self):
        """Returns the payment_id of the payment"""
        return self.__payment_id
    
    @property
    def payment_status(self):
        """Returns the payment_status of the payment"""
        return self.__payment_status
    
    @property
    def payment_amount(self):
        """Returns the payment_amount of the payment"""
        return self.__payment_amount
    
    @property
    def payment_currency(self):
        """Returns the payment_currency of the payment"""
        return self.__payment_currency
    
    @property
    def payment_time(self):
        """Returns the payment_time of the payment"""
        return self.__payment_time
    
    @property
    def payment_method(self):
        """Returns the payment_method of the payment"""
        return self.__payment_method
    
    @property
    def payment_group(self):
        """Returns the payment_group of the payment"""
        return self.__payment_group
    

    @property
    def created_at(self):
        """Returns the created_at time of the payment"""
        return self.__created_at
    
    @property
    def gateway_details(self):
        """Returns the gateway_details of the payment"""
        return self.__payment_gateway_details
    
    @property
    def payment_offers(self):
        """Returns the payment_offers of the payment"""
        return self.__payment_offers
    
    @property
    def end_time(self):
        """Returns the end_time of the payment"""
        return self.__end_time

    @property
    def to_dict(self):
        """Returns the payment details in dict format"""
        return {
            "guild_id": self.guild_id,
            "customer_name": self.customer_name,
            "order_id": self.order_id,
            "payment_id": self.payment_id,
            "payment_status": self.payment_status,
            "payment_amount": self.payment_amount,
            "payment_currency": self.payment_currency,
            "payment_time": self.payment_time,
            "payment_method": self.payment_method,
            "payment_group": self.payment_group,
            "created_at": self.__created_at,
            "end_time": self.__end_time
        }


data = {
        'cf_order_id': '3245910202', 
        'order_id': '9474437900530156235GBG6L88LJ', 
        'entity': 'order', 
        'order_currency': 'INR', 
        'order_amount': 1.0, 
        'order_status': 'ACTIVE', 
        'payment_session_id': 'session_I5ABIJZaEBHQ3mjJ4uGNBeWI7NlKWv7bDy8HZiv-qw69sy7Y52NDfDqmp1B3x0pvvUxQlIQA_n3pd8sMe1x0NJVFYLs7FFkQC22WPFZdSQrx', 
        'order_expiry_time': datetime.datetime(2024, 9, 25, 20, 31, 24, tzinfo=datetime.timezone(datetime.timedelta(seconds=19800))), 
        'order_note': None, 
        'created_at': datetime.datetime(2024, 8, 26, 20, 31, 24, tzinfo=datetime.timezone(datetime.timedelta(seconds=19800))), 
        'order_splits': [], 
        'customer_details': CustomerDetails(customer_id='947443790053015623', customer_email=None, customer_phone='8474090589', customer_name='hunter87', customer_bank_account_number=None, customer_bank_ifsc=None, customer_bank_code=None, customer_uid=None), 
        'order_meta': OrderMeta(return_url='https://discord.gg/vMnhpAyFZm', notify_url=None, payment_methods=None), 
        'order_tags': None
    }

class PaymentOrder:
    def __init__(self, obj:dict):
        self.__cf_order_id = obj.get("cf_order_id")
        self.__order_id = obj.get("order_id")
        self.__order_currency = obj.get("order_currency")
        self.__order_amount = obj.get("order_amount")
        self.__order_status = obj.get("order_status")
        self.__payment_session_id = obj.get("payment_session_id")
        self.__order_expiry_time = obj.get("order_expiry_time")
        self.__order_note = obj.get("order_note")
        self.__created_at = obj.get("created_at")
        self.__customer_details = obj.get("customer_details")
        self.__order_meta = obj.get("order_meta")
        self.__order_tags = obj.get("order_tags")

    @property
    def cf_order_id(self) -> str:
        """Returns the cf_order_id of the payment"""
        return self.__cf_order_id

    @property
    def order_id(self) -> str:
        """Returns the order_id of the payment"""
        return self.__order_id
    
    @property
    def order_currency(self) -> str:
        """Returns the order_currency of the payment"""
        return self.__order_currency
    
    @property
    def order_amount(self) -> float:
        """Returns the order_amount of the payment"""
        return self.__order_amount
    
    @property
    def order_status(self) -> str:
        """Returns the order_status of the payment"""
        return self.__order_status
    
    # also add return type to the below property such as -> datetime.datetime

    @property
    def payment_session_id(self) -> str:
        """Returns the payment_session_id of the payment"""
        return self.__payment_session_id
    
    @property
    def order_expiry_time(self) -> datetime.datetime:
        """Returns the order_expiry_time of the payment"""
        return self.__order_expiry_time
    
    @property
    def order_note(self) -> str:
        """Returns the order_note of the payment"""
        return self.__order_note
    
    @property
    def created_at(self) -> datetime.datetime:
        """Returns the created_at of the payment"""
        return self.__created_at
    
    @property
    def customer_details(self) -> CustomerDetails:
        """Returns the customer_details of the payment"""
        return self.__customer_details
    
    @property
    def order_meta(self) -> OrderMeta:
        """Returns the order_meta of the payment"""
        return self.__order_meta
    
    @property
    def order_tags(self) -> str:
        """Returns the order_tags of the payment"""
        return self.__order_tags
    
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
    



