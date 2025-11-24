import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
load_dotenv()

MAIL:str = os.environ.get("SENDER_MAIL")
PASSWORD:str = os.environ.get("SENDER_PASSWORD")
SMTP_NAME:str = os.environ.get("SMTP_NAME")
PORT:int = os.environ.get("SMTP_PORT")


def sendMail(recieverEmailAddress, subject, textMail, htmlMail): 
    # messageConstruct = EmailMessage()
    messageConstruct = MIMEMultipart('alternative')
    messageConstruct['Subject'] = subject
    messageConstruct['To'] = recieverEmailAddress
    messageConstruct['From'] = MAIL
    nonhtmlMsg = MIMEText(textMail, 'plain')
    htmlMsg = MIMEText(htmlMail, 'html')
    messageConstruct.attach(nonhtmlMsg)
    messageConstruct.attach(htmlMsg)
    # messageConstruct.set_content(mail)
    message = str(messageConstruct)
    # print(message)
    # return
    s = smtplib.SMTP(SMTP_NAME, PORT)
    s.starttls()
    s.login(MAIL, PASSWORD)
    s.sendmail(MAIL,recieverEmailAddress,message)
    s.quit()
