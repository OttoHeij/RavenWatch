#!/usr/bin/env python
__author__ = "James Burnett"
__copyright__ = "Copyright (C) James Burnett (https://jamesburnett.io)"
__license__ = "GNU AGPLv3"
__maintainer__ = "James Burnett"
__email__ = "james@jamesburnett.io"
__status__ = "Development"

import sys
import json
sys.path.append('../lib')

from alerts import Email


conf_file = sys.argv[1]
with open(conf_file) as f:
    config = json.load(f)


email = Email(config["email_server"],config["email_server_username"],config["email_server_password"])

email.add_attachment("/tmp/1.jpg")

email.add_attachment("/tmp/2.jpg")

email.send_email(config["alert_to_email"],config["alert_from_email"],"Test Email Subject","This is a test email message")

