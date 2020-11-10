#!/usr/bin/env python
# -*- coding: utf-8 -*-
print('####///////////////////////////////////####\nDeveloped by Hankun Li\nUniversity of Kansas')
print('Therm & video monitoring based on Raspberry pi 3\nVersion: 1.2\nLatest update: NOV 2, 2019')
print('NEW: Developed based on v1.2.2se2, Picam removed, Bugs fixed\n####///////////////////////////////////####\n\n')
print('##############################\nAttendtion! Up to 4 External storage supported+\
(flash drive or hard drive)\nPlease name them as:EXAMPLE,EXAMPLE01,EXAMPLE02,EXAMPLE03\n##############################\n')

from time import sleep
import time
import os, subprocess
import sys


###------------------------------###
#initialization of the w1 devices!
os.system ('sudo modprobe w1-gpio')
os.system ('sudo modprobe w1-therm')
###------------------------------###

class Webcam_control:

    #CAM_ID_path:
    RED = '/dev/video0'
    YELLOW = '/dev/video2'
    ######uncomment this line if this CAM available!!!!!!!################################# NOTE
    GREEN = '/dev/video4' 

    def capture (self, dir_path, tag):
        os.chdir(dir_path)
        try:
            os.system('fswebcam -d ' + self.RED + ' img_red%s.jpg' %tag)
            sleep(1.5)
            os.system('fswebcam -d ' + self.YELLOW + ' img_yellow%s.jpg' %tag)
            sleep(1.5)
            ######uncomment this line if this CAM available!!!!!!!######################### NOTE
            os.system('fswebcam -d ' + self.GREEN + ' img_green%s.jpg' %tag)
            sleep(1.5)
        except Exception as err:
            wrt_err_log (errlog, err)

#DEBUG STARTING HERE 09/02/2019 #Notes: need to add checking function and self-debuging later! IMPORTANT!!!!! 
class W1_thermsensor:
    
    #ID and default save path need to be assigned!!!!!!!!!
    #Sensor name = RED,YELLOW,GREEN OR AMBIENT#
    RED = '28-0119143e039c'
    YELLOW = '28-0119143b5a24'
    GREEN = '28-0119143656f5'
    AMBIENT = '28-0119143ec7d1'
    ####PATH = '/home/pi/test1' (can be deleted later)
    #pre_defined here: 0 is for celcius and others is for fahrenheit, default is celcius!!!!!!!
    switch = int(0)
    def raw_value (self, sensorID):
        #path_ID
        p = subprocess.Popen(['cat', '/sys/bus/w1/devices/' + sensorID + '/w1_slave'], stdout=subprocess.PIPE)
        sleep(1)
        out = p.communicate()
        return out
    
    def get_temp (self, s_name):
        sensorID = self.get_ID(s_name)
        try:
            w1 = str(self.raw_value(sensorID)[0]).replace(' ','')
            #print(w1)
        ### need more clarify here###
            beg = int(w1.find('t='))+2
            end = int(len(w1))-3
            raw_temp = str(w1[beg:end])
            celcius = float(raw_temp)/1000
            fahrenheit =(celcius * 1.8)+32
        except Exception as err:
            a = int(1000)
            return a
        if self.switch == 0:
            return celcius 
        else:
            return fahrenheit
    
    def get_ID(self, name):
        if name in ['RED','red','Red']:
            ID = self.RED
        elif name in ['YELLOW', 'yellow', 'Yellow']:
            ID = self.YELLOW
        elif name in ['GREEN', 'green', 'Green']:
            ID = self.GREEN
        elif name in ['AMBIENT', 'ambient', 'Ambient']:
            ID = self.AMBIENT
        else:
            print('ID name not available!')
            return()
        return ID

######Error log need to be added here!!!!!!!!!!!!######
    def record_temp (self, dir_path, tag):
        r = 'RED'
        y = 'YELLOW'
        g = 'GREEN'
        a = 'AMBIENT'
        temp_R = self.get_temp(r)
        temp_Y = self.get_temp(y)
        temp_G = self.get_temp(g)
        temp_A = self.get_temp(a)
        f_name = dir_path + '/therm_records'
        try:
            f = open (f_name,'a+')
            f.write('Dataset #%s date: ' %tag + time.strftime("%m_%d_%Y_%H:%M:%S", time.localtime()) + ';CDT\n')
            f.write('T_RED: %f deg. ;T_YELLOW: %f deg. ;T_GREEN: %f deg. ;T_AMBIENT: %f deg.\n' %(temp_R,temp_Y,temp_G,temp_A))
            f.close()
        except Exception as err:
            try:
                os.system('sudo rm -r ' + dir_path)
            except Exception:
                print (err)
        if temp_A > 4:
            rank = 0
        else:
            rank = 1
        if temp_R < -4 or temp_Y < -4 or temp_G < -4:
            rank = 2
        return rank
#DBUG END HERE    

    
def path_loaded (savepath):
    i = int (1) #new 
    while True:
        if os.path.exists (savepath) == True:
            break
        else:
            print ('savepath Not Found!! please wait for 30s\n Hints: You should check availability of current path %s\n +\
If not, press "Ctrl+C" to kill progress\nthen delete %s and re-initialize the program' %(savepath, fname))
            sleep (30)
            i += 1 #new
            if i == 20: #new
                savepath = savepath_switch ()
                if os.path.exists (savepath) == True:
                    break
                else: 
                    print ('No available savepath! shut the main system, run back up system')
                    sleep (10)
                    return 'NONE'
                    #exit()
    return savepath

def savepath_switch ():
    df_path = Read_savepath(fname)
    path = df_path
    for i in range (1,4):
        try:
            if os.path.exists(path) == False:
                path = df_path + '%02d' %i
                continue
        except:
            path = df_path + '%02d' %i
            continue
        disk = os.statvfs(path)
        storage = (disk.f_bavail * disk.f_bsize) / (1024**3)
        if storage < 0.15:
            path = df_path + '%02d' %i
        else:
            break
    # print ('Data saved to:',path) #debug 2
    return path

def Wrt_tag (fname, new_tag):
    f = open (fname,'a+')
    f.write("%s\n" %new_tag)
    f.close()
    
def Read_savepath(fname):
    f = open (fname,'r')
    a = f.readline()
    b = f.readline()
    savepath = str(f.readline().strip('\n'))
    f.close()
    return savepath

def Wrt_log_cont (fname, ts, ti, savepath, init_ts): #xx4
    Cont_tag = int(gettag_photo('', int(), fname)) - 1 
    f = open(fname, 'w')
    f.write("%d\n" %ts)
    f.write("%f\n" %ti)
    f.write("%s\n" %savepath)
    f.write("%d\n" %init_ts)
    f.write("%d\n" %Cont_tag)
    f.close()

def Wrt_log_new (fname, ts, ti, savepath, init_ts): #xx5
    f = open(fname, 'w')
    f.write("%d\n" %ts)
    f.write("%f\n" %ti)
    f.write("%s\n" %savepath)
    f.write("%d\n" %init_ts)
    f.write("0\n")
    f.close()

def new_ts_contWork (fname):
    num_recorded = int(gettag_photo('', int(), fname)) - 1 
    old_ts = retrieve_t4 (fname)
    new_ts = old_ts - num_recorded
    return new_ts

def storage_check (path):
    if os.path.exists(path) == False:
        return 0
    disk = os.statvfs(path)
    storage_aval = (disk.f_bavail * disk.f_bsize) / (1024**3)
    if storage_aval < 0.14: # if storage less than 140 MB (resered for preview captures), stop and quit the program!
        print (" Warning! Low storage space! %s GiB space remaining.\nplease set a different path\n" %storage_aval)
        return 0
    return 1
    
def gettag_photo(a, b, fname):
    c = ''
    d = int()
    f = open (fname,'rb')
    offset = int(-6)
    while True:
        i = int(1)
        f.seek(offset,2)
        a = f.readlines()
        if len(a) != 1:
            while i <= len(a):
                c = a[-i].decode('utf-8')
                try:
                    d = int(c.strip('\n'))  
                    break
                except:
                    i += 1
            break
        else:
            offset *= 2   
    f.close()
    b = d + 1
    return b

def previewmode (a,c,path):
    while a != 'exit':
        a = input("Type 'exit' to exit the preview mode. \nOr press 'q' to executing one measurement. \n")
        if a not in ['exit', 'q']:
            print ("%s is not a command\n" %a)
            continue
        elif a == 'q':
            c += 1
            prev_path = path + "/" + "Preview" +time.strftime("%m_%d_%Y", time.localtime())
            if os.path.exists(prev_path) == True:
                pass
            else:
                os.makedirs(prev_path)
            webcam.capture(prev_path, c)
            t_sensor.record_temp(prev_path, c)
            #camera.capture(prev_path + "/" + "preview_" + time.strftime("%m_%d_%Y_%H%M%S", time.localtime()) + "_img%d.jpg" %c)
            print ("preview data set# %d recorded, check them in the file:%s \n" %(c,prev_path))
    else:
        print ("debuging mode will be stoped in 3 sec!")
        sleep (3)
        if c == 0:
            pass
        else:
            print ("\ntotal %d set(s) data recorded.\n" %c)
    
def foldermaker(savepath, dir_path): # 1 return the destination Path
    path = savepath + "/CAMrecord/"+ time.strftime("%m_%d_%Y", time.localtime())
    path1 = path
    if dir_path == '':
        pass
    else: 
        path = dir_path
    i = int(1)
    c = int(1)
    var = 1
    while var == 1:
        if (os.path.exists(path) == True) and (gettag_photo('',int(),fname) != 1):
            if if_cont (fname) == 0 and date_check (path, path1):
                break
            elif path != path1:  # date_check (path, path1) == False:
                if os.path.exists(path1) == False:
                    os.makedirs(path1)
                path = path1
                break
            while os.path.exists(path) == True:
                path = path1 + '_task_%02d' %c
                c += 1
            c -= 2
            if c == 0:
                path = path1
                break
            else:
                path = path1 + '_task_%02d' %c
                break
        elif os.path.exists(path) == True:
            path = path1 + '_task_%02d' %i
            i += 1
        else:
            os.makedirs(path)
            break
    return path
    
###modify here### 09/02/2019
def autorecord(savepath, fname, dir_path):
    new_tag = gettag_photo('',int(),fname)
    c = int(new_tag)
    dir_path = foldermaker(savepath, dir_path) # 1 return to here
    webcam.capture(dir_path, c)
    t_sensor.record_temp(dir_path, c)
    Wrt_tag (fname, new_tag)
    print ('Data#%03d recorded!' %c)
    return dir_path
    
def if_cont (fname): #xx3
    f = open (fname,'r')
    t1 = f.readline()
    t2 = f.readline()
    t3 = f.readline()
    t4 = f.readline()
    t5 = int(f.readline().strip('\n'))
    f.close()
    return t5

def retrieve_t4 (fname):
    f = open (fname,'r')
    t1 = f.readline()
    t2 = f.readline()
    t3 = f.readline()
    t4 = int(f.readline().strip('\n'))
    f.close()
    return t4

def backup_tag (tag, bckup_path):
    f = open(bckup_path, 'w')
    f.write("%d\n" %tag)
    f.close()

def date_check (path, path1):
    t = int(len(path1))
    return (path [0:t] == path1 [0:t])

######## attention! below are for self out-of-hardware issue solution########
def reboot ():
    os.system ('sudo reboot')
    
#def restart_script (): #not yet created
    
def wrt_err_log (errlog, err):
    f = open (errlog,'a+')
    f.write(time.strftime("%m_%d_%Y_%H:%M:%S:", time.localtime())+ " :%s\n" %err)
    f.close()
    
#######Program START here!!!#######
# sys log established? check#
if os.path.exists('/home/pi/CAMsysLog') == False:
    os.makedirs('/home/pi/CAMsysLog')
fname = '/home/pi/CAMsysLog/CAM_logger01'
errlog = '/home/pi/CAMsysLog/ERR_log'
bckup_path = '/home/pi/CAMsysLog/backuptag'
svPth_log = '' # keep the oringnal savepath
webcam = Webcam_control()
t_sensor = W1_thermsensor()


if os.path.exists(fname) == True:
    if os.path.getsize(fname) > 5:
        f = open(fname, 'r')
        t1 = retrieve_t4 (fname)
        t2 = gettag_photo('', int(), fname)
        f.close()
        if t1 > t2:
            keyy1 = 'n'
            keyy2 = 'n'
            print ('Unfinished job will be resumed in 8 secs, press "Ctrl+C" to terminate it\nDelete the log file [%s] to start a new job\n' %fname)
            sleep(8)
        else:
            keyy1 = 'y'
            keyy2 = ''
            print ('Initialization start in 2 secs!')
            sleep (2) 
    else:
        keyy1 = 'y'
        keyy2 = ''
        print ('Initialization start in 2 secs!')
        sleep (2)
else:
    keyy1 = 'y'
    keyy2 = ''
    print ('Initialization start in 2 secs!')
    sleep (2)

# IF run the initialization or NOT?
if keyy1 in ['Y', 'y']: #initialization process start
    print('Start initialization process:\nPlease follow the instruction to set up system!\n')
    t_sensor.switch = int(input('Recording temperature value in PI or SI units? SI: enter 0; PI: enter 1\n'))
    ts = int(input("#1 Set the total measurements (type in an positive integer)\n"))
    ti = float(input("#2 Set the Trigger interval for each shoot (type in an positive number)\n")) # should be integer at this this later it can be a float.
    constant_ts = int()
    init_ts = ts
    while ts > 0 and ti > 0:
        break
    else:
        ts = int(input("TRY AGIAN! Set the total shoots (type in an positive integer)\n"))
        ti = int(input("TRY AGIAN! Set the time interval for each shoot (type in an positive integer)\n"))
    savepath = input("#3 Type in the destination path for this job\n")
    while os.path.exists(savepath) != True:
        savepath = input("#3 Path is invalid, please try agian!\n")
    if storage_check (savepath) == 0:
        print ('no enough space')
    print ('Disk space check pass!')
    Wrt_log_new (fname, ts, ti, savepath, init_ts) #XX2
elif keyy1 in ['N', 'n']: #skip initialization process
    if os.path.exists(fname) == True:
        f=open(fname,'r')
        ts = f.readline()
        ti = f.readline()
        savepath = f.readline()
        f.close()
    else:
        print ('system not initialized! please run the initialization process!\n')
        exit()
    ts = int(new_ts_contWork (fname))
    ti = float(ti.strip('\n'))
    savepath = str(savepath.strip('\n'))
    svPth_log = savepath
    savepath = path_loaded (savepath)
    if ts > 0:
        Wrt_log_cont (fname, ts, ti, svPth_log, t1)  #XX1
        print ('Continue last job: %d datasets(s)\nTrigger interval: %f(s)\nSave path is: %s\n' %(ts, ti, savepath))
    if savepath != 'NONE' and storage_check (savepath) == 1:
        pass
    else:
        wrt_err_log (errlog, 'path error')
        
        
        
#Default sys_log path:       
print ('\nsys_logger path: %s, Please DO NOT delete it!!!' %fname)
sz = os.path.getsize(fname)
print ('system log created! Default size is: %d\n' %sz)
final_path = ''
i = int(1)
######start recording!!!!!!#####
if ts <= 0:
    print ('No job found! Please start a new job! program killed in 3 secs\n')
    sleep(3)
    exit()
elif keyy2 == 'n':
    pass
else:
    while keyy2 not in ['Y', 'y', 'N', 'n']:
        keyy2 = input ("Enter the Preview Mode? Y:Enter; N:Skip \n")
        if keyy2 in ['Y', 'y']:
            previewmode ('',0,savepath)
            break
        elif keyy2 in ['N', 'n']:
            break
print ("@@@Auto-recording begin! workload: %d set(s); Trigger interval: %f sec(s)@@@\n" %(ts, ti))
ct = 0
cam_op = 0
while i <= ts:
    i += 1
    sleep(ti)
        # new developed system
    bckpath = '/home/pi/therm_backup/' + time.strftime("%m_%d_%Y", time.localtime())
    if os.path.exists(bckpath) == True:
        pass
    else:
        os.makedirs(bckpath)
        cam_op = 0
    if storage_check (bckpath) == 0:
        exit()
    rk = t_sensor.record_temp(bckpath, 'b')
    if rk == 0:
        if ct == 20:
            ct = 0
        else:
            ct += 1
            print('no ice risk!pass')
            continue
    if os.path.exists(savepath) == True and storage_check (savepath) == 1:
        final_path = autorecord (savepath, fname, final_path)
    else:
        if rk == 2 and cam_op <= 10:
            webcam.capture(bckpath, 'b')
            cam_op += 1

print("\nfinished!")
sleep(2)
print ("\n@@@Recording jobs finished! Data saved to %s@@@" %final_path)
