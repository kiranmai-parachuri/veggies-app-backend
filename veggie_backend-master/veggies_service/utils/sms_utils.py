import json
import math
import random

import requests

from veggies_service.constants import sms_service_constans
# auth_key = sms_service_constans.MSG91_AUTH_KEY
# otp_client = OTPClient(auth_key)
from veggies_service.utils.exceptions import GenericCustomException


def generate_otp():
    return 123456
    digits = [i for i in range(0, 10)]
    random_str = ""
    for i in range(6):
        index = int(math.floor(random.random() * 10))
        random_str += str(digits[index])
    return int(random_str)


def send_otp(mobile, otp):
    url = sms_service_constans.URL
    url = url + "username=" + sms_service_constans.USERNAME + "&password=" + sms_service_constans.PASSWORD + "&type=TEXT&sender=" + sms_service_constans.SENDER + "&mobile=" + str(
        mobile) + "&message=" + str(
        otp) + " is your one time password for login."
    print url
    response = requests.get(url)
    print response.content
    if (response.content.split('|')[0]).strip() == 'SUBMIT_SUCCESS':
        return response.content.split('|')[1]
    else:
        raise GenericCustomException("SMS not working")
    return 322424


def send_otp_msg91(mobile_no, otp):
    msg = "Welcome to KMNaturals. Your otp for login is " + str(otp)
    url = sms_service_constans.MSG91_URL_FOR_OTP + 'authkey=' + sms_service_constans.MSG91_AUTH_KEY + '&message=' + msg + '&sender=KMNaturals&mobile=91' + str(
        mobile_no) + '&otp=' + str(otp)
    res = requests.get(url=url)
    if res.status_code == 200:
        print(res.content)
        return json.loads(res.content)['message']
    else:
        print(res.content)
        return False


def send_sms(mobile_no, msg):
    url = sms_service_constans.MSG91_URL_FOR_SMS + 'route=4' + '&authkey=' + sms_service_constans.MSG91_AUTH_KEY + '&message=' + msg + '&sender=YASHDA&mobiles=91' + str(
        mobile_no) + '&country=91'
    res = requests.get(url=url)
    # print res.content
    if res.status_code == 200:
        return res.content
    else:
        return False


def resend_otp_msg_91():
    pass


def send_msg1():
    # importing the module
    import httplib as ht

    # establishing connection
    conn = ht.HTTPSConnection("api.msg91.com")

    # determining the payload
    payload = {"sender": "MSGAPI",
               "route": "4",
               "country": "91",
               "sms": [
                   {
                       "message": "Welcome GeeksForGeeks, Today you have PC class",
                       "to": [
                           "9322113489"
                       ]
                   },
               ]
               }

    # creating the header
    headers = {
        'authkey': "343852A2YEfTu4S5f7d8b26P1",
        'content-type': "application/json"
    }

    # sending the connection request
    conn.request("POST", "/api/v2/sendsms", json.dumps(payload), headers)

    res = conn.getresponse()
    data = res.read()

    # printing the acknowledgement
    print(data.decode("utf-8"))


# from sendotp import sendotp

# if __name__ == '__main__':

# print generate_otp()
# print send_otp('9637552245', 12345)
# print send_otp_msg91('9322113489', generate_otp())
# print(send_sms('9637552245', "Your training is schedule refdsfdsdsfssfsfs"))

# otpobj = sendotp.sendotp(sms_service_constans.MSG91_AUTH_KEY, 'my message is {{otp}} keep otp with you.')
# send_otp_msg91_default('9637552245')
def send_sms2():
    import urllib  # Python URL functions
    import urllib2  # Python URL functions

    authkey = "343852A2YEfTu4S5f7d8b26P1"  # Your authentication key.

    mobiles = "919637552245"  # Multiple mobiles numbers separated by comma.

    message = "Test message"  # Your message to send.

    sender = "112233"  # Sender ID,While using route4 sender id should be 6 characters long.

    route = "default"  # Define route

    # Prepare you post parameters
    values = {
        'authkey': authkey,
        'mobiles': mobiles,
        'message': message,
        'sender': sender,
        'route': route
    }

    url = "http://api.msg91.com/api/sendhttp.php"  # API URL

    postdata = urllib.urlencode(values)  # URL encoding the data here.

    req = urllib2.Request(url, postdata)

    response = urllib2.urlopen(req)

    output = response.read()  # Get Response

    print output  # Print Response


if __name__ == '__main__':
    # send_sms2()
    otp = generate_otp()
    send_otp_msg91(9637552245, otp)
