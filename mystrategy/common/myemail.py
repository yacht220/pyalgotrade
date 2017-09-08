# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText

canSend = True

def sendEmail(from_, to_):
    if canSend is True:
        msg = MIMEText("Everything is OK")
        msg['Subject'] = 'PyalgoTrade heartbeat'
        msg['From'] = from_
        msg['To'] = to_

        # Send the message via our own SMTP server, but don't include the
        # envelope header.
        s = smtplib.SMTP('mailhubwc.lss.emc.com')
        s.sendmail(from_, [to_], msg.as_string())
        s.quit()
