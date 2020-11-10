import os, sys
from time import time

class Reformat(object):

    def __init__(self, path_out):
        self.po = path_out
        
    def data_sorting(self):
        f_name = 'therm_records'
        f = open (f_name,'r')
        lines = f.readlines()
        f.close()
        d = self.date_read(lines[0])
        s = ''
        for line in lines:
            if line[0] == 'D':
                continue
            j = int(0)
            beg = int(0)
            end = int(0)
            for i in range(0,len(line)):
                if line[i] == ':':
                    beg = i + 2
                elif line[i] == 'd' and i > beg:
                    end = i - 2
                    s = s + line[beg:end]+ '    '
                    j += 1
                    beg = 0
                    end = 0 
                if j == 4:
                    s = s + '\n'
                    break
        self.data_write(d, s)

    def date_read(self, line0):
        c = int(0)
        for i in range(0, len(line0)):
            if line0[i] == ':':
                beg = i+2
            if line0[i] == '_':
                c += 1
                if c == 3:
                    end = i
                    date = line0[beg:end]
                    break
        print(date)
        return date
                              
    def data_write(self, date, s):
        outname = 'thermal_sorted_' + date +'.txt'
        out = self.po + '/' + outname
        f = open (out,'a+')
        f.write('%s\n' %s)
        f.close()

# MAIN FUNCTION:
#input the work path
work_path = 'H:/Signal_recording_project_dataprocessing/Lawrence_SOUTH_W19toW20' # CHANGE HERE!, attention: '\' need to be changed to '/' !!!!!!
######
#end here#

t1 = time()
inpth = work_path + '/therm_backup'
opth = work_path + '/out'
if not os.path.exists(opth):
    os.makedirs(opth)
rf = Reformat(opth)
for root,dirs,files in os.walk(inpth):
    for l in dirs:
        dir_path = inpth + '/' +l
        try:
            os.chdir(dir_path)
        except Exception as err:
            print(err)
        try:
            rf.data_sorting()
        except:
            continue
print ('done!')
t2 = time()
ts = t2 - t1
print('time consumption: %02f secs' %ts)
