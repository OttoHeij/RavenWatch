#!/usr/bin/env python
__author__ = "James Burnett"
__copyright__ = "Copyright (C) James Burnett (https://jamesburnett.io)"
__license__ = "GNU AGPLv3"
__maintainer__ = "James Burnett"
__email__ = "james@jamesburnett.io"
__status__ = "Development"

import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

import sys
import os

class Email:

    def __init__(self,email_server,email_user, email_password):
        self.email_server = email_server
        self.email_user = email_user
        self.email_password = email_password
        self.server = smtplib.SMTP(self.email_server)
        self.attachments = []
        
    
    def clear_attachments(self):
        self.attachments = []
    
    def add_attachment(self,file_path):
        if os.path.isfile(file_path) is True:
            self.attachments.append(file_path)
        
    def send_email(self,from_address,to_address, subject, body):
        try:
            msg = MIMEMultipart()
            msg['From'] = from_address
            msg['To'] = to_address
            msg['Date'] = formatdate(localtime=True)
            msg['Subject'] = subject
            msg.attach(MIMEText(body))
            
            for attachment in self.attachments:
                with open(attachment, "rb") as fil:
                    part = MIMEApplication(
                        fil.read(),
                        Name=basename(attachment)
                    )
                part['Content-Disposition'] = 'attachment; filename="%s"' % basename(attachment)
                msg.attach(part)

            server_ret = self.server.connect(self.email_server)
            print(server_ret)
            self.server.ehlo()
            self.server.starttls()
            self.server.login(self.email_user, self.email_password)
            self.server.sendmail(from_address, [to_address], msg.as_string())
            self.server.close()
        except:
            e = sys.exc_info()
            print("error in send_email: %s" % str(e))
