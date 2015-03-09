#
import sys
import requests
import time
import thread
from threading import Timer
from threading import _Timer

import smtplib,re  
from email.mime.text import MIMEText  

WARNMAILBLK = False
TIMERRUNNING = 0
TIMERMAIL = 0

#castle_odinland@126.com
#castleodinland@yeah.com

sourc_mail_addr = "cexuscastle@126.com"
dest_mail_addr = ["cexuscastle@126.com"]

def sendWarningMail (text):  
    msg = MIMEText(text)  
    msg['Subject'] = "Aptamil 1+ comming!!!"  
    msg['From'] = sourc_mail_addr  
    smtp = smtplib.SMTP()  
    smtp.connect(r'smtp.126.com')
    smtp.login(sourc_mail_addr, "zxcvbnm123")  
    smtp.sendmail(sourc_mail_addr, dest_mail_addr, msg.as_string())  
    smtp.close() 
    

def canSendMailAgain():
    global WARNMAILBLK 
    WARNMAILBLK = False

def runAnotherStart():
    global TIMERRUNNING 
    TIMERRUNNING = Timer(10.0, checkAptamilHandler, [])
    TIMERRUNNING.start()

def checkAptamilHandler():
    global WARNMAILBLK 
    global TIMERRUNNING 
    global TIMERMAIL
    
    strs_for_item = []
    main_rst = []
    try:
        r = requests.get('http://www.windeln.de/zh/aptamil-milchnahrung.html?selectedean=4008976022299', timeout=10)
    except Exception as e:
        print ("requests failed: %r" % e)
        outResultFileHandle = open("SearchAptamil.log",'a')
        outResultFileHandle.write("\n%r\n" % e)
        outResultFileHandle.close()
        TIMERRUNNING = Timer(30.0, checkAptamilHandler, [])
        TIMERRUNNING.start()
        return
    """
    print r.status_code
    print r.headers
    print r.encoding
    print r.text.encode('utf-8')
    """
    thtml = r.text.encode('utf-8')
    
    tResult_h = 0
    tResult_t = 0

    #search title
    for i in range(0,4):
        #now we only search Kinder-Milch 1 plus
        tResult_h = thtml.find('<span itemprop="itemOffered">Kinder-Milch 1 plus', tResult_t)
        if(tResult_h == -1):
            #if miss one title, break, start another try
            runAnotherStart()
            return
        else:
            tResult_t = thtml.find('<div class="product-row span-20', tResult_h)
            if(tResult_t == -1):
                #if miss one ending, break, start another try
                runAnotherStart()
                return
            strs_for_item.append(thtml[tResult_h:tResult_t])

    #parse the item and save into main_rst
    for str in strs_for_item:
        #print '---------------------------------------------------------'
        #print str + '\n'
        sh = str.find('<span itemprop="itemOffered">')
        sh += len('<span itemprop="itemOffered">')
        st = str.find('St', sh)
        pitemOffered = str[sh:st+2]
        #print pitemOffered
        
        sh = str.find('<span class="raw-price">')
        sh += len('<span class="raw-price">')
        st = str.find('</span>', sh)
        rawPrice = str[sh:st]
        #print rawPrice
        
        sh = str.find('<span class="product-note align-right right" id="notShippable">')
        if(sh == -1):
            shippable = True
        else:
            shippable = False
        main_rst.append((pitemOffered, rawPrice, shippable))
   
    email_str = ""
    for node in main_rst:
        email_str += "%s|%sEUR|%s\n" % (node[0], node[1], node[2])
     
    #only test   
    #sendWarningMail(email_str)
    
    timestr = time.ctime(time.time())
        
    print ("%s\n%s" % (timestr.encode('ascii'), email_str))
    outResultFileHandle = open("SearchAptamil.log",'a')
    outResultFileHandle.write("%s\n%s" % (timestr.encode('ascii'), email_str))
    
    #check if Shippable, send warning email
    for node in main_rst:
        if(node[2] == True and WARNMAILBLK == False):
            sendWarningMail(email_str);
            WARNMAILBLK = True
            outResultFileHandle.write("Send Email once.\n")
            TIMERMAIL = Timer(600.0, canSendMailAgain, [])#600s to send again
            TIMERMAIL.start()
            break
            
    outResultFileHandle.close()
    TIMERRUNNING = Timer(60.0, checkAptamilHandler, [])
    TIMERRUNNING.start()

def main_run():
    global TIMERRUNNING 
    global TIMERMAIL 
    
    TIMERRUNNING = Timer(0.5, checkAptamilHandler, [])
    TIMERRUNNING.start()
    while(True):
        content = raw_input("")
        if content == 'exit':
            if(isinstance(TIMERRUNNING, _Timer)):
                TIMERRUNNING.cancel()
            if(isinstance(TIMERMAIL, _Timer)):
                TIMERMAIL.cancel()
            break
    

if __name__=="__main__":
    main_run()
    print 'ByeBye'
    
