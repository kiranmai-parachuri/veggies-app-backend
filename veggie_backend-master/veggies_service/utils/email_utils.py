import logging
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import django;

django.setup()

from veggies_service.constants import email_constants, order_constants
# Allow less secure app : https://www.google.com/settings/security/lesssecureapps
from veggies_service.utils.order import get_delivery_date_for_order


def send_email(message, receivers, sender_email=email_constants.SENDER_EMAIL, sender_pass=email_constants.SENDER_PASS):
    for dest in receivers:
        try:
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login(sender_email, sender_pass)
            message = message
            s.sendmail(sender_email, dest, message)
            s.quit()
        except Exception as e:
            logging.error('Error while sending email to: %s ', dest)


def send_email_with_attachments(receiver, subject, message=None, sender_email=email_constants.SENDER_EMAIL, html=None,
                                attachment_path=None):
    # instance of MIMEMultipart
    msg = MIMEMultipart()

    # storing the senders email address
    msg['From'] = sender_email

    # storing the receivers email address
    msg['To'] = receiver

    # storing the subject
    msg['Subject'] = subject
    if message:
        # attach the body with the msg instance
        msg.attach(MIMEText(message, 'plain'))
    if html:
        msg.attach(MIMEText(html, 'html'))

    if attachment_path:
        # open the file to be sent
        filename = attachment_path.split('/')[-1]
        attachment = open(attachment_path, "rb")

        # instance of MIMEBase and named as p
        p = MIMEBase('application', 'octet-stream')

        # To change the payload into encoded form
        p.set_payload((attachment).read())

        # encode into base64
        encoders.encode_base64(p)

        p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

        # attach the instance 'p' to instance 'msg'
        msg.attach(p)

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()

    # Authentication
    s.login(email_constants.SENDER_EMAIL, email_constants.SENDER_PASS)

    # Converts the Multipart msg into a string
    text = msg.as_string()

    # sending the mail
    s.sendmail(email_constants.SENDER_EMAIL, receiver, text)

    # terminating the session
    s.quit()


def get_order_items_table(items):
    items_table = '<table> <tr><th>Item Name</th> <th>Quantity</th> <th>Price/Points</th><tr>'
    for item in items:
        row = '<tr> <td>' + item.product.name + '</td> <td>' + str(item.quantity.quantity)+' '+str(item.quantity.unit) + '*' + str(
            item.order_quantity) + '</td><td>' + str(item.quantity.price * item.order_quantity) + '</td></tr>'
        items_table += row
    items_table += '</table>'
    return items_table


def send_order_placed_email(order):
    email = order.created_by.email
    if email:
        user = order.created_by
        delivery_date = get_delivery_date_for_order(order)
        html_table = get_order_items_table(order.items.all())
        print 'html: ' + html_table
        if order.order_type in [order_constants.BASKET, order_constants.ONE_TIME_BASKET]:
            email_text = '<p> Hi ' + user.first_name + ' ' + user.last_name + ',<p> Your order worth <strong>' + str(
                order.total_amount) + ' INR </strong> is successfully placed. It will get delivered by ' + delivery_date.strftime(
                '%d/%m/%Y') + '<p> Thanks for shopping with us.'
        else:
            email_text = '<p> Hi ' + user.first_name + ' ' + user.last_name + ',<p> Your order worth <strong>' + str(
                order.total_amount) + ' INR </strong> is successfully placed. It will get delivered by ' + delivery_date.strftime(
                '%d/%m/%Y') + '<p> Bellow are item details: <br>' + html_table + '<p> Thanks for shopping with us.'
        send_email_with_attachments(email, 'Order placed successfully', html=email_text)
    else:
        print 'Email not configure for user'


def send_order_delivered_email(order):
    email = order.created_by.email
    if email:
        user = order.created_by
        html_table = get_order_items_table(order.items.all())
        print 'html: ', html_table
        email_text = '<p> Hi ' + user.first_name + ' ' + user.last_name + ',<p> Your order worth <strong>' + str(
            order.total_amount) + ' INR </strong> is successfully delivered. <p> Bellow are item details: <br>' + html_table + '<p> Thanks for shopping with us.'
        send_email_with_attachments(email, 'Order delivered successfully', html=email_text)
    else:
        print 'Email not configure for user'


def send_delivery_customised_email_to_users(users, delivery):
    for user in users:
        if user.email:
            html_items_table = get_order_items_table(delivery.products.all())
            print html_items_table
            email_text = '<p> Hi ' + user.first_name + ' ' + user.last_name + ',<p> You basket delivery is customised by seller as you did not customized it within given time. Below are the items you will be getting with it. <br>' + html_items_table + '<p>Thanks for shopping with us.'
            send_email_with_attachments(user.email, 'Basket delivery customized', html=email_text)
        else:
            print 'User dont have email: ' + user.first_name + ' ' + user.last_name
            pass


# https://stackoverflow.com/questions/54657006/smtpauthenticationerror-5-7-14-please-log-n5-7-14-in-via-your-web-browser
# Try the unlock captcha link: https://accounts.google.com/DisplayUnlockCaptcha (no effect on its own but may be related to the full solution)

if __name__ == '__main__':
    # send_email('<h1>Welcome to email</h1>', ['vitthal.sarode1@gmail.com'], )
    from veggies_service.db.veggies_models.models import User, Delivery

    u = User.objects.get(mobile=312312123)
    d = Delivery.objects.last()
    send_delivery_customised_email_to_users([u], d)

    # send_email_with_attachments("vitthal.sarode1@gmail.com", "Test email", "this is message body",
    #                             html="<html><body><p> <h1>This is html body of email</h1></p></body></html>",
    #                             attachment_path="/Users/vitthalsarode/Downloads/slider1.jpg")
    # print 'done'
