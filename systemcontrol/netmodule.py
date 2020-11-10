#!/usr/bin/env python
# -*- coding: utf-8 -*-

print('####///////////////////////////////////####\nDeveloped by Hankun Li\nUniversity of Kansas')
print('Network module for LedSignalMonitoring OS version 1.0')
print('update: Aug 1 2020\n####///////////////////////////////////####\n\n\n')
print('Attention: Input VendorID, ProductID, Users email information\n')

from time import sleep
import time
import os, subprocess
import sys
import smtplib
from email.message import EmailMessage

class Netcheck(object):

    def __init__(self,vendor,product,address):
        self.vd = str(vendor)
        self.pd = str(product)
        self.ltepath = str(address)

    def netping(self):
        try:
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.quit
            return(1)
        except Exception as err:
            print(err)
            return(0)

    def reset(self):
        try:
            if os.path.exists(self.ltepath):
                os.system('sudo usb_modeswitch -R -v %s -p %s' %(self.vd, self.pd))
        except Exception as err:
            print(err)


class AutoUpload(object):

    def __init__(self,unm,pd,reciever,testsite,filename,dirpath,date):
        self.usr = str(unm)
        self.pswd = str(pd)
        self.recv = str(reciever)
        self.fname = str(filename)
        self.path = str(dirpath)
        self.site = str(testsite)
        self.date = str(date)

    def autoemail(self):
        try:
            s = smtplib.SMTP('smtp.gmail.com', 587) #server note: gmail sever require turn on the [less secure access] option in adv settings
            s.starttls()
            s.login(self.usr, self.pswd)
        except Exception as err:
            print(err)
            return
        try:
            message = 'Temperature data auto uploaded from the test site: %s, date: %s' %(self.site, self.date)
            fpath = self.path + '/' + self.fname
            msg = EmailMessage()
            msg['From'] = self.usr
            msg['Subject'] = 'Site_%s_Date_%s' %(self.site, self.date)
            msg['To'] = self.recv 
            msg.set_content(message)
            msg.add_attachment(open(fpath, 'r').read(), filename = '%s_%s' %(self.site, self.date)) # attached file full path
            s.send_message(msg)
            s.quit()
        except Exception as err:
            print(err)



# usr input
sw = 1 # 0:off 1:on
vd = '19d2' #input vendor id
pd = '1405' #input product id
lteaddr = '/media/pi/ZTEMODEM' #input modems path
sender = 'kulrlsignal20lawrence@gmail.com' #Set up the sender account
pswd = 'Leep2400' #Set up the sender account
reciever = 'hankunli@ku.edu' #Set up the reciever
testsite = 'LAWRENCE' # name of test site
# common usr input end !
filename = 'therm_records' # Dont change this one !!! (only do under certain conditions)
# usr input end here!

nc = Netcheck(vd,pd,lteaddr)
# program start here!
if sw == 1:
    sleep(10)
    print('network module enabled!\n')
    path0 = ''
    date0 = ''
    while True:
        if os.path.exists(lteaddr):
            # print('check 1\n') #debug
            if nc.netping() == 1:
                print('checked\n') #debug
                bckpath = '/home/pi/therm_backup/' + time.strftime("%m_%d_%Y", time.localtime())
                print('path',path0,bckpath) # debug
                pdebug = '/home/pi/debug/' + time.strftime("%m_%d_%Y", time.localtime())
                if os.path.exists(pdebug):
                    fdebug = pdebug + '/pinglog'
                else:
                    try:
                        os.makedirs(pdebug)
                        fdebug = pdebug + '/pinglog'
                    except Exception as err:
                        print(err)
                try:
                    f = open(fdebug,'a+')
                    f.write(time.strftime("%H_%M_%S", time.localtime()) + '\n')
                    f.close()
                except Exception as err1:
                    os.system('sudo rm -r ' + pdebug)
                    print(err1)
                    os.system('sudo rm -r ' + pdebug)
                if path0 != '' and path0 != bckpath:
                    print ('check 3\n') #debug
                    try:
                        au = AutoUpload(sender,pswd,reciever,testsite,filename,path0,date0)
                        au.autoemail()
                    except Exception as err:
                        print(err)
                path0 = bckpath
                date0 = time.strftime("%m%d%Y", time.localtime())
            else:
                print('warning!\n') #debug
                sleep(5)
                nc.reset()
                sleep(60)
        elif nc.netping() == 1:
            print('Device network: wifi/ethernet mode \n')
            bckpath = '/home/pi/therm_backup/' + time.strftime("%m_%d_%Y", time.localtime())
            if path0 != '' and path0 != bckpath:
                print ('check 3\n') #debug
                try:
                    au = AutoUpload(sender,pswd,reciever,testsite,filename,path0,date0)
                    au.autoemail()
                except Exception as err:
                    print(err)
            path0 = bckpath
            date0 = time.strftime("%m%d%Y", time.localtime())
        sleep(180)
else:
    print('network module disabled!\n')

# debug code below
'''
path0 = '/home/pi/therm_backup' + '/'+ time.strftime("%m_%d_%Y", time.localtime())
date0 = time.strftime("%m%d%Y", time.localtime())
au = AutoUpload(sender,pswd,reciever,testsite,filename,path0,date0)
'''
