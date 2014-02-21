import smtplib, logging

from ConfigLoader import getCfg

'''
Send an email to users:

recievers: a list of CC elements
subject: email subject
message: email message
contentType: text/html by default
mime: 1.0 by default
'''

def send(recievers, subject, message, contentType='text/html', mime='1.0'):
    ''' Send an email to a group of users '''
    # The guy marked as 'the one :D'
    sender = getCfg('EMAIL', 'sender')

    content = "From: %s\r\n"         % sender
    content+= "BCC: %s\r\n"          % ",".join(recievers)
    content+= "MIME-Version: %s\r\n" % mime
    content+= "Content-type: %s\r\n" % contentType
    content+= "Subject: %s\r\n"      % subject
    content+= "\r\n"
    content+= message

    to = [sender] + recievers

    try:
        # start new connection
        server = smtplib.SMTP(getCfg('EMAIL', 'host'))

        # TLS REQUIRED
        if getCfg('EMAIL', 'tls', 'boolean') == True:
            server.ehlo()
            server.starttls()

        # LOGIN REQUIRED
        if getCfg('EMAIL', 'auth', 'boolean') == True:
            server.login(getCfg('EMAIL', 'login'), getCfg('EMAIL', 'password'))

        # save and exit
        server.sendmail(sender, to, content)
        server.quit()

    except smtplib.SMTPException:
        logging.error('SMTP: unable to send email')


if __name__ == '__main__':
    send([sender], 'Super sujet', 'Super content')