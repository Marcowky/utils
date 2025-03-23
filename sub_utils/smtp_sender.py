import smtplib
import json
import logging

from email.mime.text import MIMEText
from email.header import Header

class SMTPSender():
    def __init__(self, config_path='config/config.json'):
        self.load_config(config_path)

    def load_config(self, config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)

        self.SMTP_SERVER = config['smtp']['smtp_server']
        self.SMTP_PORT = config['smtp']['smtp_port']
        self.SENDER_EMAIL = config['smtp']['sender_email']
        self.SENDER_PASSWORD = config['smtp']['smtp_passward'] 


    def send_email(self, subject, body, receiver_email):
        try:
            msg = MIMEText(body, 'plain', 'utf-8')
            msg['Subject'] = Header(subject, 'utf-8')
            msg['From'] = self.SENDER_EMAIL
            msg['To'] = receiver_email

            with smtplib.SMTP_SSL(self.SMTP_SERVER, self.SMTP_PORT) as server:
                server.connect(self.SMTP_SERVER, self.SMTP_PORT)
                server.login(self.SENDER_EMAIL, self.SENDER_PASSWORD)
                server.send_message(msg)
                server.quit()
            
            logging.info("邮件发送成功")
        except Exception as e:
            logging.error(f"发送邮件时出错: {str(e)}")