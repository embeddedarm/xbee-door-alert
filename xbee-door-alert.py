import serial, os, datetime, time, smtplib, ConfigParser, sys
from datetime import timedelta
from email.mime.text import MIMEText
from xbee import XBee

# Need to be sure to reset the XBee radio socket before starting
os.system("echo 0 > /sys/class//leds/en-xbee-3v3/brightness")
os.system("echo 1 > /sys/class//leds/en-xbee-3v3/brightness")

# Setup the serial port
serial_port = serial.Serial('/dev/ttymxc7', 57600)

wait = 300 # 5 minutes
last_sent = datetime.datetime(1, 1, 1, 0, 0)

def print_data(data):
    print data

def send_alert():

    # For security, let's grab credentials from a config file.
    # Copy config.example.ini to config.ini with your info.
    config = ConfigParser.ConfigParser() 
    config.read("config.ini")

    gmail_user = config.get('Credentials', 'Username')
    gmail_password = config.get('Credentials', 'Password')

    try:  
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)

        msg = MIMEText("The office door has been opened! Hope it was you...")

        msg['Subject'] = "Office Door Opened!"
        msg['From'] = gmail_user
        msg['To'] = gmail_user

        server.sendmail(gmail_user, [gmail_user], msg.as_string())
        server.close()

        print "Alert email sent!"

    except:  
        print "Something went wrong in send_alert()!"
        print sys.exc_info()[0]
        raise

def handler(data):
    """
    This method is called whenever data is received
    from the associated XBee device. Its first and
    only argument is the data contained within the
    frame.
    """
   
    global last_sent
    global wait

    delta = datetime.datetime.now() - last_sent
 
    if data['samples'][0]['dio-0'] and delta.total_seconds() > wait:
        print "Door opened!"
        send_alert()
        last_sent = datetime.datetime.now()

# Change 'send_alert' to 'print_data' for debugging
xbee = XBee(serial_port, callback=handler)

while True:
    try:
        time.sleep(0.1)
    except KeyboardInterrupt:
        break

xbee.halt()
serial_port.close()
