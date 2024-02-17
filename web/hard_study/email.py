from flask import render_template
from flask_mail import Message
from threading import Thread

from web import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(app, to, subject, template, **kwargs):
    msg = Message(app.config['MAIL_SUBJECT_PREFIX']+subject, sender=app.config['MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template+'.txt', **kwargs)
    msg.html = render_template(template+'.html', **kwargs)
    mail.send(msg)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.run()
    return thr

