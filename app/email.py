from threading import Thread
from flask import current_app
from flask_mail import Message
from app import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)
        print(
            f'Email sent from: {msg.sender} to: {msg.recipients} subject: {msg.subject}')


def send_email(subject, sender, recipients, text_body, html_body):
    srv = current_app.config['MAIL_SERVER']
    port = current_app.config['MAIL_PORT']
    print(f'mail srv: {srv} port: {port}')
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    if current_app.config['MAIL_ENABLED']:
        Thread(target=send_async_email,
               args=(current_app._get_current_object(), msg)).start()
    else:
        print("email sending is disbled")
