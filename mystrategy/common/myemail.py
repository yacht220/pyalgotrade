# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText

canSend = True

def sendEmail(text):
    if canSend is True:
        from_ = 'yizhou.zhou@noreply.com'
        to_ = 'yizhou.zhou@outlook.com'
        msg = MIMEText(text)
        msg['Subject'] = 'PyalgoTrade notification'
        msg['From'] = from_
        msg['To'] = to_

        # Send the message via our own SMTP server, but don't include the
        # envelope header.
        s = smtplib.SMTP('mailhubwc.lss.emc.com')
        s.sendmail(from_, [to_], msg.as_string())
        s.quit()
