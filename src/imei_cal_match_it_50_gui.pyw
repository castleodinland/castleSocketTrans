#!/usr/bin/python
#imei_cal_match_it_50_gui.pyw

import Tkinter
from Tkinter import *
import ttk
from os.path import walk, join, normpath, isdir, isfile, abspath
import sys
import re
#import copy
import filecmp
import time
import thread

the_first_lay_dir = False

#release note:
#v1.1101Beta -->fix bug when checking band support
#v1.1105Beta -->add a new Entry to appoint Cal PATH
#v1.1111Beta -->add a Progressbar

class Application(Frame):

    #to walk through the dir
    def mydir(self, arg, dirname, names):
        #global gNvCalPath
        global the_first_lay_dir
        file = [normpath(tfile) for tfile in names]
        fullfilename = [abspath(join(dirname,tfile)) for tfile in names]
        #copy it, $file and $fullfilename are one-one correspondence
        if(dirname == self.contents.get()):
            print "totall files:" + dirname + "===>" +str(len(file))+"\n"
        for i in range(0,len(file)):
            if isfile(fullfilename[i]):#only save files
                #save WriteIMEI*.ini files
                p = re.compile("WriteIMEI.*\.ini")
                matchit = p.match(file[i])
                if matchit:
                    #print matchit.group()
                    self.list_ini_files.append(fullfilename[i])
                    #continue
                
            if isdir(fullfilename[i]):#only save path
                #save cal files's RID
                p = re.compile("[0-9A-Fa-f]{32}")
                matchit = p.match(fullfilename[i][-32:])
                if matchit:
                    self.lallCalNumInCal.append(fullfilename[i][-32:])# save RID 
                    #here we need to compare with DEFAULT cal file under \Z\NVRAM\CALIBRAT\    
                    #check DAUL DATA
                    dmatch, dmismatch, derrors = filecmp.cmpfiles(str(fullfilename[i]) + gNvCalPath, "REFCALIBRAT\\DUAL", self.DUALCalFileList, shallow=False)
                    qmatch, qmismatch, qerrors = filecmp.cmpfiles(str(fullfilename[i]) + gNvCalPath, "REFCALIBRAT\\QUAD", self.QUADCalFileList, shallow=False)
                    
                    #print str(fullfilename[i]) + gNvCalPath, '\n'
                    #print 'DMatch:', dmatch, '\n'
                    #print 'DMismatch:', dmismatch, '\n'
                    #print 'DErrors:', derrors, '\n'
                    #print 'QMatch:', qmatch, '\n'
                    #print 'QMismatch:', qmismatch, '\n'
                    #print 'QErrors:', qerrors, '\n'    
                            
                    if(len(dmatch) == 4):
                        self.lDUALDefaultCalByChipID.append(fullfilename[i][-32:])
                        
                    if(len(qmatch) == 4):
                        self.lQUADDefaultCalByChipID.append(fullfilename[i][-32:])                
    
                        
                    if(len(derrors) == 0 and len(qerrors) == 0):
                        self.lIsQUADCalByChipID.append(fullfilename[i][-32:])
                    elif(len(derrors) == 0 and len(qerrors) == 4):
                        self.lIsDUALCalByChipID.append(fullfilename[i][-32:])
                    else:
                        self.lIsNULLBandCalByChipID.append(fullfilename[i][-32:])                        
                    #continue
            if(dirname == self.contents.get()):
                #update bar 
                show_value = i*100/len(file)
                self.pbar.config(value=show_value)
                
                #and ignore other type of files
        if(the_first_lay_dir == False):
            the_first_lay_dir = True
        #print "\n".join(list_ini_files)       
           
    def get_imei_by_chipid(self, chipid):
        #print "run get_imei_by_chipid", self.IMEIAndChipIDPair
        for tPair in self.IMEIAndChipIDPair:
            if(tPair[1] == chipid):
                return tPair[0]
        #return 0

    def do_clean_work(self):
        del self.lallCalNumInCal[:]
        del self.lallCalNumInINI[:]
        del self.lallRidNumInINI[:]

        del self.lDUALDefaultCalByChipID[:]
        del self.lQUADDefaultCalByChipID[:]
        del self.lIsDUALCalByChipID[:]
        del self.lIsQUADCalByChipID[:]
        del self.lIsNULLBandCalByChipID[:]
        del self.IMEIAndChipIDPair[:]

        del self.list_ini_files[:]
    
    def run_check(self, tpath, thead, ttail, calpath):
        
        global gNvCalPath
        gNvCalPath = calpath
                
        print self.version_info , '\n'
        print "Cal Path:" , gNvCalPath, '\n' 
        print "[path imeiHead imeiTail]"
    
        path = tpath
        imei_range_head = int(thead)*10
        imei_range_tail = int(ttail)*10 + 9
        print("searching range: [%d, %d]\n" %(imei_range_head, imei_range_tail))
        
        #self.pbar.config(value=10)
        
        walk(path, self.mydir, 1)
        
        self.pbar.config(value=110)
        
        outResultFileHandle = open("result.txt",'w+')
        
        """
        check *.cal files imei inside and outside
        """
        outResultFileHandle.write("Check calibration files consistency\n")
     
        """
        Parse the imei from WriteIMEI*.ini
        """
        if len(self.list_ini_files)==0:
            print ("No WriteIMEI.ini found!\n exit\n")
            self.lb_title["text"] = "Error:No WriteIMEI.ini!"
            self.hi_there["state"] = "active"
            return
        
        for iniFile in self.list_ini_files:
            iniFileHandle = open(iniFile,'r')
            readState = 0
            matchit1 = 0
            matchit2 = 0
            strIMEI = 0
            strChipID = 0
            while True:
                line = iniFileHandle.readline()
                
                if not line:
                    iniFileHandle.close()
                    readState = 0
                    break
                imei = "\[\d{15}\]" #a real imei
                matchit1 = re.search(imei, line)
                if matchit1:
                    self.lallCalNumInINI.append(matchit1.group()[1:16])
                    readState = 1
                    strIMEI = matchit1.group()[1:16]
                    
                rid = "rid=[0-9A-Fa-f]{32}" #a real rid
                matchit2 = re.search(rid, line)
                if matchit2:
                    self.lallRidNumInINI.append(matchit2.group()[4:36])
                    if(readState == 1):
                        readState = 2
                        strChipID = matchit2.group()[4:36]
    
                if readState == 2:
                    t_pair = (strIMEI, strChipID)
                    self.IMEIAndChipIDPair.append(t_pair)
                    readState = 0
    
            iniFileHandle.close()
            readState = 0
    
        #for tPair in IMEIAndChipIDPair:
        #    print tPair[0]+"=====>"+tPair[1]+"\n"
    
        #self.pbar.config(value=90)
    
        """
        save the two lists in set and get the intersection 
        """        
        allCalNumInCal = set(self.lallCalNumInCal)
        allCalNumInINI = set(self.lallRidNumInINI)
        
        outResultFileHandle.write("\nTotal real cal folder number is: %d\n" %(len(list(allCalNumInCal))))
        outResultFileHandle.write("\nTotal cal serial number in INI is: %d\n" %(len(list(allCalNumInINI))))
        
        mixCalNum = allCalNumInCal&allCalNumInINI
        #print list(mixCalNum)
        
        outResultFileHandle.write("\ncalibration numbers in ini but not in cal:\n")
        outResultFileHandle.write("\n".join(list(allCalNumInINI-mixCalNum)))
        outResultFileHandle.write("\ntotally %d items found!\n" %(len(list(allCalNumInINI-mixCalNum))))
        outResultFileHandle.write("=============================================================================================================\n\n")
        
        outResultFileHandle.write("\ncalibration numbers in cal but not in ini:\n")
        outResultFileHandle.write("\n".join(list(allCalNumInCal-mixCalNum)))
        outResultFileHandle.write("\ntotally %d items found!\n" %(len(list(allCalNumInCal-mixCalNum))))
        
        outResultFileHandle.write("=============================================================================================================\n\n")
        
        countRange = 0
        
        
        #for cnini in lallCalNumInINI:
        #    reImeiNo = int(cnini[0:16])
        #    if reImeiNo < imei_range_head or reImeiNo > imei_range_tail:
        #        outResultFileHandle.write("Out of range imei: %s\n" %(cnini))
        #        countRange += 1
        
        lallCalNumInINI_set = set(self.lallCalNumInINI)
        for cnini in lallCalNumInINI_set:
            reImeiNo = int(cnini[0:16])
            if reImeiNo < imei_range_head or reImeiNo > imei_range_tail:
                outResultFileHandle.write("Out of range imei: %s\n" %(cnini))
                countRange += 1
        
        outResultFileHandle.write("\ntotally %d items,and %d out of range.\n" %(len(lallCalNumInINI_set), countRange))
        outResultFileHandle.write("=============================================================================================================\n\n")
        
        outResultFileHandle.write("\ntotally %d CAL data are DUAL DEFAULT CAL data:\n" %(len(self.lDUALDefaultCalByChipID)))
        #outResultFileHandle.write("\n".join(lDUALDefaultCalByChipID))
        for chipid in self.lDUALDefaultCalByChipID:
            outResultFileHandle.write("%s----->%s\n" %(chipid, self.get_imei_by_chipid(chipid)))
        
        outResultFileHandle.write("\n=============================================================================================================\n\n")
        
        outResultFileHandle.write("\ntotally %d CAL data are QUAD DEFAULT CAL data:\n" %(len(self.lQUADDefaultCalByChipID)))
        #outResultFileHandle.write("\n".join(lQUADDefaultCalByChipID))
        for chipid in self.lQUADDefaultCalByChipID:
            outResultFileHandle.write("%s----->%s\n" %(chipid, self.get_imei_by_chipid(chipid)))
        outResultFileHandle.write("\n=============================================================================================================\n\n")
        
        outResultFileHandle.write("END\n\n\n")    
        
        print("Done!\n")
        
        outResultFileHandle.close()#close result.txt
        
        #Comparison Table
        outResultFileHandle = open("ComparisonTable.txt",'w+')
        outResultFileHandle.write("The Comparison Table For IMEI and ChipID:\n\n")
        
        for tPair in self.IMEIAndChipIDPair:
            #print tPair[0]+"=====>"+tPair[1]+"\n"
            outResultFileHandle.write("%s======>%s\n" %(tPair[0], tPair[1]))
        
        outResultFileHandle.close()#close ComparisonTable.txt
    
        #Band Confirm table
        outResultFileHandle = open("BandConfirm.txt",'w+') 
        outResultFileHandle.write("Band Confirm table:\n\n")
        outResultFileHandle.write("\n=============================================================================================================\n\n")
        outResultFileHandle.write("The list below is Band support with DUAL\n")
        for tChipID in self.lIsDUALCalByChipID:
            outResultFileHandle.write("DUAL====>%s--->%s\n" %(tChipID, self.get_imei_by_chipid(tChipID)))
        outResultFileHandle.write("\n=============================================================================================================\n\n")        
        outResultFileHandle.write("The list below is Band support with QUAD\n")
        for tChipID in self.lIsQUADCalByChipID:
            outResultFileHandle.write("QUAD====>%s--->%s\n" %(tChipID, self.get_imei_by_chipid(tChipID)))
        outResultFileHandle.write("\n=============================================================================================================\n\n")
        outResultFileHandle.write("The list below is Band support with NONE(error with CAL)\n")
        for tChipID in self.lIsNULLBandCalByChipID:
            outResultFileHandle.write("NULL====>%s--->%s\n" %(tChipID, self.get_imei_by_chipid(tChipID)))
    
        outResultFileHandle.write("\n=============================================================================================================\n\n")
        outResultFileHandle.write("END")
        outResultFileHandle.close()#close BandConfirm.txt
        
        #INPUT_SOME = raw_input("Press ENTER key to exit.")
        self.lb_title["text"] = "FINISHED!"
        self.do_clean_work()
        self.hi_there["state"] = "active"
        self.pbar.config(value=120)
        
    def say_hi(self):
        self.lb_title["text"] = "RUNING, Please wait..."
        #main run, open a new thread to handle
        thread.start_new_thread(self.run_check, (self.contents.get(), self.imeihead.get(), self.imeitail.get(), self.contentscal.get()))
        #self.run_check(self.contents.get(), self.imeihead.get(), self.imeitail.get())
        self.hi_there["state"] = "disable"
        self.pbar.config(value=0)
        
    def print_contents(self, event):
        print("Well done, continue...", self.contents.get())
        self.lb_title["text"] = "Well done, continue..." + self.contents.get()
        
    def createWidgets(self):
        
        self.lb_title = Label(root,text = self.version_info)
        self.lb_title.pack({"side": "top"})
        
        #path for workspace
        self.entrythingy = Entry(justify = "left",width = 40)
        self.entrythingy.pack({"side": "top"})

        # here is the application variable
        self.contents = StringVar()
        # set it to some value
        self.contents.set("input work space path here...")
        # tell the entry widget to watch this variable
        self.entrythingy["textvariable"] = self.contents

        # and here we get a callback when the user hits return.
        # we will have the program print out the value of the
        # application variable when the user hits return
        self.entrythingy.bind('<Key-Return>', self.print_contents)
       
       
        #path for NVRAM CAL DATA
        self.calpathentry = Entry(justify = "left",width = 40)
        self.calpathentry.pack({"side": "top"})

        # here is the application variable
        self.contentscal = StringVar()
        # set it to some value
        self.contentscal.set("\\Z\\NVRAM\\CALIBRAT")
        # tell the entry widget to watch this variable
        self.calpathentry["textvariable"] = self.contentscal   
       
        vcmd = (self.register(self.validate),'%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        #head
        self.imeihead = Entry(validate = 'key', validatecommand = vcmd, justify = "left",width = 40)
        self.imeihead.pack({"side": "top"})

        # here is the application variable
        self.contentshead = StringVar()
        # set it to some value
        self.contentshead.set("00000000000000")
        self.imeihead["textvariable"] = self.contentshead
        
        #tail
        self.imeitail = Entry(validate = 'key', validatecommand = vcmd, justify = "left",width = 40)
        self.imeitail.pack({"side": "top"})

        # here is the application variable
        self.contentstail = StringVar()
        # set it to some value
        self.contentstail.set("99999999999999")
        self.imeitail["textvariable"] = self.contentstail
        
        self.QUIT = Button(self, relief=RAISED, width = 15)
        self.QUIT["text"] = "QUIT"
        self.QUIT["fg"] = "red"
        self.QUIT["command"] = self.quit

        self.QUIT.pack({"side": "right"})

        self.hi_there = Button(self, relief=RAISED, width = 15)
        self.hi_there["text"] = "RUN",
        self.hi_there["fg"] = "blue"
        self.hi_there["command"] = self.say_hi
        
        self.hi_there.pack({"side": "left"})

        self.pbar = ttk.Progressbar(root, length=284, maximum=120)
        self.pbar.pack()

    def validate(self, action, index, value_if_allowed, prior_value, text, validation_type, trigger_type, widget_name):             
        if len(value_if_allowed) > 14:
            return False

        if text in '0123456789':
            return True
        else:
            return False

    def __init__(self, master=None):
        
        self.IMEIAndChipIDPair = []
        
        self.lallCalNumInCal = []#set of cal files
        self.lallCalNumInINI = []#set of imei in WriteIMEI.ini
        self.lallRidNumInINI = []#set of rid in WriteIMEI.ini
        
        self.lDUALDefaultCalByChipID = []
        self.lQUADDefaultCalByChipID = []
        self.lIsDUALCalByChipID = []
        self.lIsQUADCalByChipID = []
        self.lIsNULLBandCalByChipID = []
        self.DUALCalFileList = ["MT08_002", "MT07_002", "MT0N_002", "MT0M_002"]
        self.QUADCalFileList = ["MT09_002", "MT06_002", "MT0O_002", "MT0L_002"]
        
        #IMEIAndChipIDPair = []#save the pair for IMEI and ChipID
        
        self.lallCalNumInINI_set = set()
        
        self.allCalNumInCal = set()
        self.allCalNumInINI = set()
        self.mixCalNum = ()
        self.list_ini_files = []#save all the WriteIMEI*.ini files
        
        self.imei_range_head = 0
        self.imei_range_tail = 0
        
        self.resultOfCompFile = 0
        
        self.version_info = "imei_cal_match_it version v1.1111Beta"
        
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()
        
        
        
if __name__=="__main__":
    root = Tk()
    
    #lock the size
    root.minsize(300,160)
    root.maxsize(300,160)
    
    app = Application(master=root)
    app.mainloop()



