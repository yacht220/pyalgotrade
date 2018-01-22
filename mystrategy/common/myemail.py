# Import smtplib for the actual sending function
import smtplib
from mystrategy import common

# Import the email modules we'll need
from email.mime.text import MIMEText

'''def sendEmail(text):
    if common.canSendEmail is True:
        from_ = 'yizhou.zhou@noreply.com'
        to_ = 'yizhou.zhou@outlook.com'
        smtp_server = '' # Enter the ip address or hostname of smtp server
        msg = MIMEText(text)
        msg['Subject'] = 'PyalgoTrade notification'
        msg['From'] = from_
        msg['To'] = to_

        # Send the message via our own SMTP server, but don't include the
        # envelope header.
        s = smtplib.SMTP(smtp_server)
        s.sendmail(from_, [to_], msg.as_string())
        s.quit()'''

class MyEmailServer(object):
    def __init__(self):
        if common.canSendEmail is True:
            self.__from = 'yizhou.zhou@outlook.com'
            self.__to = 'yizhou.zhou@outlook.com'
            self.__smtp_server = 'smtp-mail.outlook.com' # Enter the ip address or hostname of smtp server
            self.__mail_account = 'yizhou.zhou@outlook.com'
            self.__mail_passwd = ''           

            self.__server = smtplib.SMTP(self.__smtp_server, 587)
            self.__server.ehlo()
            self.__server.starttls()
            self.__server.login(self.__mail_account, self.__mail_passwd)

    def __del__(self):
        if common.canSendEmail is True:
            self.__server.close()

    def sendEmail(self, text):
        if common.canSendEmail is True:
            msg = MIMEText(text)
            msg['Subject'] = 'PyalgoTrade notification'
            msg['From'] = self.__from
            msg['To'] = self.__to
            self.__server.sendmail(self.__from, [self.__to], msg.as_string())
            
if __name__ == '__main__':
    emailServer = MyEmailServer()
    emailServer.sendEmail("test mail 1")
    emailServer.sendEmail("test mail 2")