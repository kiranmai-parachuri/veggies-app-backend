import razorpay

from veggies_service.constants import razorpay_constants
from veggies_service.utils.exceptions import GenericCustomException

client = razorpay.Client(auth=(razorpay_constants.KEY_ID, razorpay_constants.KEY_SECRET))


def convert_rs_to_paise(rupees):
    return 100
    # return rupees * 100


def create_order(amount, receipt):
    req_data = {'currency': razorpay_constants.INDIAN_CURRENCY, 'receipt': receipt,
                'amount': convert_rs_to_paise(amount)}
    try:
        return client.order.create(data=req_data)
    except Exception as e:
        raise GenericCustomException(message='Payment service error: ' + str(e))


def fetch_order(order_id):
    return client.order.fetch(order_id)


def fetch_all_order():
    return client.order.all()

def webhook():
    client.utility.verify_webhook_signature(webhook_body, webhook_signature, webhook_secret)
    # webhook_body should be raw webhook request body

if __name__ == '__main__':
    data = {'amount': 500, "currency": 'INR', 'receipt': '100'}
    res = create_order(5, data)
    print 'done', res
    # orderid = 'order_Fh6sZRQ0LIsYHb'
    # print fetch_all_order()
