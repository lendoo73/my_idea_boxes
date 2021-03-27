# SMTPAuthenticationError: (534, b'5.7.14) solution:
# https://joequery.me/guides/python-smtp-authenticationerror/
from app import app
import os
from flask_mail import Mail, Message
from helper import get_extension

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

def send_email(to, subject, message_txt = None, message_HTML = None, img = None):
    msg = Message(
        subject,
        recipients = [to]
    )

    if message_txt:
        msg.body = message_txt
    if message_HTML:
        msg.html = message_HTML
    
    if img:
        path = "static/logo/"
        if get_extension(img) == "svg":
            img = "idea-box.png"
        
        with open(f'{path}{img}', 'rb') as fp:
            msg.attach(
                img, 
                get_MIME_type(img), 
                fp.read(), 
                'inline', 
                headers = [['Content-ID', '<logo>']])

    mail.send(msg)
    

def get_MIME_type(file_name):
    # http://www.iana.org/assignments/media-types/media-types.xhtml
    extension = get_extension(file_name)
    media_types = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png"
    }

    return media_types[extension]