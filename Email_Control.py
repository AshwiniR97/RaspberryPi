import imaplib
import RPi.GPIO as GPIO
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import getpass
import feedparser
from email.mime.base import MIMEBase
from email import encoders
import picamera

pin0 = 11
pin1 = 12
pin2 = 13
pin3 = 15

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)    #To remove any warnings
GPIO.setup(pin1,GPIO.OUT)
GPIO.setup(pin2,GPIO.OUT)
GPIO.setup(pin0,GPIO.OUT)
GPIO.setup(pin3,GPIO.OUT)
p = GPIO.PWM(pin3,700)
p.start(0)

def takin():
    a = [GPIO.input(pin0), GPIO.input(pin1), GPIO.input(pin2),GPIO.input(pin3)]
    return a

def logout():               #For total logout from servers
    sendser.quit()

    server.close()
    server.logout()
    GPIO.cleanup()
    return

def sending(mylist = [], *a):        #function to send email
    text = "Current state: "
    j=1
    for i in mylist:
        text = text + '\nAppliance ' + str((j)) + ': ' + str(i)
        j=j+1
    msg=MIMEText(text)
    msg['Subject'] = "Testing"
    msg['From'] = sendac
    msg['To'] = myac
    sendser.sendmail(sendac,myac,msg.as_string())
    print 'Status has been sent'
    return
def sendingintrude():
    sendac ="sendingac1@gmail.com"  #Sending Account Information
    pwdsend = "sendingaccount1"
    myac= "receivingac1@gmail.com"  #Receiving Account Information
    sendser = smtplib.SMTP('smtp.gmail.com:587')
    sendser.ehlo_or_helo_if_needed()
    sendser.starttls()
    sendser.ehlo_or_helo_if_needed()
    sendser.login(sendac,pwdsend)
    msg = MIMEMultipart()
    msg['Subject'] = "Intruder Alert"
    msg['From'] = sendac
    msg['To'] = myac
    body = 'Someboy trying to enter house!'
    msg.attach(MIMEText(body,'plain'))

    filename='xyz.jpg'
    attachment  =open(filename,'rb')

    part = MIMEBase('application','octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',"attachment; filename= "+filename)

    msg.attach(part)
    text = msg.as_string()
    sendser.sendmail(sendac,myac,msg.as_string())
    return

def receiving():            #function to receive email
    resp = feedparser.parse("https://" + sendac + ":" + pwdsend + "@mail.google.com/gmail/feed/atom")
    unread = int(resp["feed"]["fullcount"])  #checking if any unread mail
    if unread==0:                           #if no unread mail
        print ('Mail Not Received')
    else:
        subj = resp['items'][0].title
        if subj=='Testing':                #checking if mail is one we need
            stat, count = server.select('Inbox')
            stat, data = server.fetch(count[0], '(UID BODY[TEXT])')
            temp = data[0][1]
            ogh = ''
            new = ''
            for i in range(76,len(temp)):
                ogh = ogh + temp[i]
            interpret(ogh)
            
            state = takin()      #new pin status
            sending(state)
        else:
            print "Testing Mail not received."
    return
def interpret(text):
    d={"A1":"pin0","A2":"pin1","A3":"pin2","A4":"pin3"}
    dd={"0":"0","1":"20","2":"40","3":"60","4":"80","5":"100"}
    tosend=''
    rep="GPIO.output("
    nn=''
    aa=0
    for i in text:
        nn=nn+i
        if i=='~':
            break
        if i=='-':
            nn=nn.replace('-','')
            nn=nn.replace('\n','')
            nn=nn.replace('\r','')
            fin=d[nn]
            if nn=="A4":
                tosend=tosend+'p.ChangeDutyCycle('
                aa=1
            else:
                tosend=tosend+rep+fin+",GPIO."
            nn=''
        if i=='.':
            nn=nn.replace('.','')
            nn=nn.replace('\n','')
            nn=nn.replace('\r','')
            print nn
            if aa==1:
                nn=dd[nn]
                aa=0
            if nn=='exit':
                tosend='exit()'
            elif nn=='state':
                state=takin()
                sending(state)
            else:
                tosend=tosend+nn+")"
            print tosend
            exec(tosend)
            nn=''
            tosend=''
    return         

pw = getpass.getpass()

if pw=='1235':
    print ('You may proceed.')
    #get current status and print
else:
    print 'Incorrect. One more try.'
    pw = getpass.getpass()
    if pw=='1235':
        print ('You may proceed.')
    else:
        print('Intruder alert!!/n Capturing photo!')
        with picamera.PiCamera() as camera:
            camera.resolution=(1280,720)
            camera.capture("xyz.jpg")
        sendingintrude()
        exit()

sendac ="sendingac1@gmail.com"  #Sending Account Information
pwdsend = "sendingaccount1"
myac= "receivingac1@gmail.com"  #Receiving Account Information

sendser = smtplib.SMTP('smtp.gmail.com:587')
sendser.ehlo_or_helo_if_needed()
sendser.starttls()
sendser.ehlo_or_helo_if_needed()
sendser.login(sendac,pwdsend)
server=imaplib.IMAP4_SSL("imap.gmail.com",993)
server.login(sendac,pwdsend)

#Sending Initial Status Email
state = takin()
sending(state)
time.sleep(3)
    
while True:
    receiving()
    time.sleep(2)

