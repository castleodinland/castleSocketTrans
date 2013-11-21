#!/usr/bin/python
#imei_cal_match_it_50_gui.pyw

import Tkinter
from Tkinter import *
import ttk
import os
from os.path import walk, join, normpath, isdir, isfile, abspath
import sys
import re
#import copy
import filecmp
import time
import thread
#import xlrd
import xlwt

the_first_lay_dir = False

#release note:
#v1.1101Beta -->fix bug when checking band support
#v1.1105Beta -->add a new Entry to appoint Cal PATH
#v1.1111Beta -->add a Progressbar
#v1.1119Beta -->add overlap check for imei and chip id
#v1.1121Beta -->output excel as report, need install xlwt module first for your python

class Application(Frame):

    #to walk through the dir
    def mydir(self, arg, dirname, names):
        #global gNvCalPath
        global the_first_lay_dir
        file = [normpath(tfile) for tfile in names]
        fullfilename = [abspath(join(dirname,tfile)) for tfile in names]
        #copy it, $file and $fullfilename are one-one correspondence
        if(dirname == self.contents.get()):
            pass
            #print "totall files:" + dirname + "===>" +str(len(file))+"\n"
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
        return 0
        
    def get_chipid_by_imei(self, imei):
        #print "get_chipid_by_imei:", imei
        for tPair in self.IMEIAndChipIDPair:
            #print "have see", tPair[0][0:13]
            if(tPair[0][0:14] == imei):
                return tPair[1]
        return self.a_null_chip_id

    def get_full_imei_by_imei(self, imei):
        for tPair in self.IMEIAndChipIDPair:
        #print "have see", tPair[0][0:13]
            if(tPair[0][0:14] == imei):
                return tPair[0]
        return ''

    def if_cal_file_exist(self, chipid):
        for node in self.lallCalNumInCal:
            if(node == chipid):
                return True 
        return False

    def if_cal_file_is_dual_defualt(self, chipid):
        for node in self.lDUALDefaultCalByChipID:
            if(node == chipid):
                return True
        return False
    
    def if_cal_file_is_quad_defualt(self, chipid):
        for node in self.lQUADDefaultCalByChipID:
            if(node == chipid):
                return True
        return False
    
    def if_cal_file_is_bad_cal(self, chipid):
        for node in self.lIsNULLBandCalByChipID:
            if(node == chipid):
                return True
        return False        
        
    def hold_abnormal_pair_from(self):
        abnormal_pair = []
        sub_abnormal_pair = []
        for tpair in self.totalView:
            if(tpair[1] == self.a_null_chip_id or tpair[2] != 1 or tpair[3] != 0
               or tpair[4] != 0 or tpair[5] != 0 or tpair[6] != 0 or tpair[7] != 0):
                abnormal_pair.append(tpair)
                if(tpair[6] != 0):
                    for ttpair in self.totalView:
                        if(ttpair[1] == tpair[1] and ttpair[0] != tpair[0]):
                            sub_abnormal_pair.append(ttpair)
           
        return abnormal_pair, sub_abnormal_pair

    
                
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
        
        del self.totalView[:]
    
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
    
        outResultFileHandle = open("result.txt",'w+')
        
        """
        check *.cal files imei inside and outside
        """
        outResultFileHandle.write("Check calibration files consistency\n")
    
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
        #outResultFileHandle.write("\n".join(list(allCalNumInINI-mixCalNum)))
        for tChipID in list(allCalNumInINI-mixCalNum):
            outResultFileHandle.write("%s--->%s\n" %(tChipID, self.get_imei_by_chipid(tChipID)))
            
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
        
        #Comparison Table, now is the total view
        #total view: <imei><chip id><is cal exist><DUAL is defult><QUAD is defult><cal is bad>[be chipid overlap][imei overlap]
        #init total view:
        for i in range(int(thead),int(ttail)+1):
            t_pair = [i, self.a_null_chip_id, 0, 1, 1, 1, 0, 0]
            self.totalView.append(t_pair)
        
        for tpair in self.totalView:
         
            tpair[1] = self.get_chipid_by_imei(str(tpair[0]))
            
            #check over-lapped imei:
            if(tpair[1] != self.a_null_chip_id):
                temp_imei = self.get_imei_by_chipid(tpair[1])
                
                if(str(tpair[0]) == temp_imei[0:14]):
                    pass  
                else:#may use a used chip id
                    tpair[6] = tpair[6] + 1
            else:
                pass

            temp_imei = self.get_full_imei_by_imei(str(tpair[0]))
            if(len(temp_imei) != 0):
                tpair[0] = temp_imei[:14] + '|' + temp_imei[14:]
            else:
                tpair[0] = str(tpair[0]) + '|X'
                       
            tpair[2] = self.if_cal_file_exist(tpair[1])
            tpair[3] = self.if_cal_file_is_dual_defualt(tpair[1])
            tpair[4] = self.if_cal_file_is_quad_defualt(tpair[1])
            tpair[5] = self.if_cal_file_is_bad_cal(tpair[1])            

            #print("See total view: %dX--->%s--->%d:%d:%d:%d" %(tpair[0], tpair[1], tpair[2], tpair[3], tpair[4], tpair[5])) 
            
            #check over-lapped imei:
            same_imei_pair = []
            for ttPair in self.IMEIAndChipIDPair:
                if(ttPair[0][:14] == tpair[0][:14] and len(ttPair[0]) != 0):
                    same_imei_pair.append(ttPair)
            set_for_same_imei_pair = set(same_imei_pair)
            if(len(set_for_same_imei_pair) > 1):
                tpair[7] = len(set_for_same_imei_pair)
                
            #print "SAME IMEI : %d" %(len(set_for_same_imei_pair))
            #print same_imei_pair
        abnormal_pair,sub_abnormal_pair = self.hold_abnormal_pair_from()
        
        outResultFileHandle = open("TotalView.txt",'w+')
        outResultFileHandle.write("********The Total View Table For Check:********\n\n")
        outResultFileHandle.write("Total count theoretically: %d\n\n" %(len(self.totalView)))
        outResultFileHandle.write("[IMEI]--->[Chip ID]--->([have cal] [is dual defualt][is quad defualt] [is bad])=([chipid overlap]=[imei overlap])\n")
        for tpair in self.totalView:
            outResultFileHandle.write("%s--->%s--->(%d=====%d=====%d=====%d)=====(%d=====%d)\n" %(tpair[0], tpair[1], tpair[2], tpair[3], tpair[4], tpair[5], tpair[6], tpair[7]))
        
        outResultFileHandle.write("\n\n********The Total View Summary:********\n\n")
        outResultFileHandle.write("Total abnormal data: %d\n\n" %(len(abnormal_pair)))
        for tpair in abnormal_pair:
            outResultFileHandle.write("%s--->%s--->(%d=====%d=====%d=====%d)=====(%d=====%d)\n" %(tpair[0], tpair[1], tpair[2], tpair[3], tpair[4], tpair[5], tpair[6], tpair[7]))
        
        outResultFileHandle.write("\n\nTotal sub-abnormal data: %d\n\n" %(len(sub_abnormal_pair)))
        for tpair in sub_abnormal_pair:
            outResultFileHandle.write("%s--->%s--->(%d=====%d=====%d=====%d)=====(%d=====%d)\n" %(tpair[0], tpair[1], tpair[2], tpair[3], tpair[4], tpair[5], tpair[6], tpair[7]))
        
        outResultFileHandle.close()
        
        #==============================================================================#
        outResultFileHandle = open("ComparisonTable.txt",'w+')
        outResultFileHandle.write("The Comparison Table For IMEI and ChipID:\n\n")
        
        for tPair in self.IMEIAndChipIDPair:
            #print tPair[0]+"=====>"+tPair[1]+"\n"
            outResultFileHandle.write("%s======>%s\n" %(tPair[0], tPair[1]))
        
        outResultFileHandle.close()#close ComparisonTable.txt
        #==============================================================================#

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
        
        #delete txt that we use excel now
        os.remove("ComparisonTable.txt")
        os.remove("BandConfirm.txt")
        os.remove("result.txt")
        os.remove("TotalView.txt")
        
        #excel:::
        workbook = xlwt.Workbook()
        self.form_total_view_excel(workbook)
        self.form_result_excel(workbook)
        self.form_band_confirm_excel(workbook)
        self.form_comparison_excel(workbook)
        workbook.save('TotalView.xls')
        
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
        #self.contents.set("1307004-1008-t")
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
        self.imeihead = Entry(validate = 'key', justify = "left",width = 40)
        self.imeihead.pack({"side": "top"})

        # here is the application variable
        self.contentshead = StringVar()
        # set it to some value
        self.contentshead.set("00000000000000")
        #self.contentshead.set("35909402000003")
        self.imeihead["textvariable"] = self.contentshead
        
        #tail
        self.imeitail = Entry(validate = 'key', justify = "left",width = 40)
        self.imeitail.pack({"side": "top"})

        # here is the application variable
        self.contentstail = StringVar()
        # set it to some value
        self.contentstail.set("00000000000008")
        #self.contentstail.set("35909402000008")
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

    def init_font_style(self):
        #title font and style
        titlefont = xlwt.Font() # Create Font 
        titlefont.bold = True # Set font to Bold 
        titlefont.name = 'Verdana'#'Times New Roman'
        titlefont.height =  20 * 12 #12ptx

        titlepattern = xlwt.Pattern()
        titlepattern.pattern = xlwt.Pattern.SOLID_PATTERN
        titlepattern.pattern_fore_colour = xlwt.Style.colour_map['turquoise']#Search in Style.py for _colour_map_text

        self.title_style = xlwt.XFStyle() # Create Style 
        self.title_style.font = titlefont # Add Bold Font to Style 
        self.title_style.pattern = titlepattern

        #sub title font and style
        subtitlefont = xlwt.Font() # Create Font 
        subtitlefont.bold = True # Set font to Bold 
        subtitlefont.name = 'Verdana'#'Times New Roman'
        subtitlefont.height =  20 * 12 #12ptx

        subtitlepattern = xlwt.Pattern()
        subtitlepattern.pattern = xlwt.Pattern.SOLID_PATTERN
        subtitlepattern.pattern_fore_colour = xlwt.Style.colour_map['aqua']#Search in Style.py for _colour_map_text

        self.subtitle_style = xlwt.XFStyle() # Create Style 
        self.subtitle_style.font = subtitlefont # Add Bold Font to Style 
        self.subtitle_style.pattern = subtitlepattern
        
        #label font and style
        labelfont = xlwt.Font() # Create Font 
        labelfont.bold = True # Set font to Bold 
        labelfont.name = 'Verdana'#'Times New Roman'
        labelfont.height =  20 * 12 #12ptx

        labelpattern = xlwt.Pattern()
        labelpattern.pattern = xlwt.Pattern.SOLID_PATTERN
        labelpattern.pattern_fore_colour = xlwt.Style.colour_map['sea_green']#Search in Style.py for _colour_map_text

        self.label_style = xlwt.XFStyle() # Create Style 
        self.label_style.font = labelfont # Add Bold Font to Style 
        self.label_style.pattern = labelpattern        
        
        #normal data font and style
        ndfont = xlwt.Font() # Create Font 
        #ndfont.bold = True # Set font to Bold 
        ndfont.name = 'Lucida Sans Typewriter'#'Times New Roman''Lucida Sans Typewriter'
        ndfont.height =  20 * 12 #12ptx

        ndpattern = xlwt.Pattern()
        #ndpattern.pattern = xlwt.Pattern.SOLID_PATTERN
        #ndpattern.pattern_fore_colour = xlwt.Style.colour_map['gray80']#Search in Style.py for _colour_map_text

        self.nordata_style = xlwt.XFStyle() # Create Style 
        self.nordata_style.font = ndfont # Add Bold Font to Style 
        self.nordata_style.pattern = ndpattern
        
        #abnormal data font and style
        adfont = xlwt.Font() # Create Font 
        adfont.bold = True # Set font to Bold 
        adfont.name = 'Lucida Sans Typewriter'#'Times New Roman'
        adfont.height =  20 * 12 #12ptx

        adpattern = xlwt.Pattern()
        adpattern.pattern = xlwt.Pattern.SOLID_PATTERN
        adpattern.pattern_fore_colour = xlwt.Style.colour_map['red']#Search in Style.py for _colour_map_text

        self.abnordata_style = xlwt.XFStyle() # Create Style 
        self.abnordata_style.font = adfont # Add Bold Font to Style 
        self.abnordata_style.pattern = adpattern
        
    def get_data_style_for_xlwt_ex(self, tinput):
        if(tinput == 1):
            return self.nordata_style
        else:
            return self.abnordata_style
        
    def get_data_style_for_xlwt(self, tinput):
        if(tinput == 0):
            return self.nordata_style
        else:
            return self.abnordata_style        
        
    def get_chipid_style_for_xlwt(self, chipid):
        if(chipid == self.a_null_chip_id):
            return self.abnordata_style
        else:
            return self.nordata_style  
        
    def form_total_view_excel(self, workbook):
        ttoffset = 0
        worksheet = workbook.add_sheet('top view', cell_overwrite_ok=True)
        worksheet.col(0).width =  256 * 26
        worksheet.col(1).width =  256 * 50
        
        for i in range(2, 8):
            worksheet.col(i).width =  256 * 15
        
        #set titles
        worksheet.write_merge(ttoffset, ttoffset, 0, 1, '********The Total View Table For Check:********', self.title_style) 
        ttoffset = ttoffset + 2
        ttstr = "Total count theoretically: %d" %(len(self.totalView))
        worksheet.write_merge(ttoffset, ttoffset, 0, 1, ttstr, self.subtitle_style)
        
        #set label
        ttoffset = ttoffset + 1
        tlabel = ['IMEI', 'Chip ID', 'have cal', 'DUAL DFT', 'QUAD DFT', 'Is bad?', 'chipid olp', 'imei olp']
        for i in range(0,len(tlabel)):
            worksheet.write(ttoffset, i, tlabel[i], self.label_style)

        #set datas
        ttoffset = ttoffset + 1
        for i in range(0, len(self.totalView)):
            cur = self.totalView[i]
            #imei
            worksheet.write(i+ttoffset, 0, cur[0], self.nordata_style)
            #chip id
            worksheet.write(i+ttoffset, 1, cur[1], self.get_chipid_style_for_xlwt(cur[1]))
            #have cal
            worksheet.write(i+ttoffset, 2, cur[2], self.get_data_style_for_xlwt_ex(cur[2]))
            #is dual defualt
            worksheet.write(i+ttoffset, 3, cur[3], self.get_data_style_for_xlwt(cur[3]))        
            #is quad defualt
            worksheet.write(i+ttoffset, 4, cur[4], self.get_data_style_for_xlwt(cur[4]))   
            #is bad
            worksheet.write(i+ttoffset, 5, cur[5], self.get_data_style_for_xlwt(cur[5]))
            #chipid overlap
            worksheet.write(i+ttoffset, 6, cur[6], self.get_data_style_for_xlwt(cur[6]))   
            #imei overlap
            worksheet.write(i+ttoffset, 7, cur[7], self.get_data_style_for_xlwt(cur[7]))   
        ttoffset = ttoffset + len(self.totalView) + 2
        
        #abnormal data
        worksheet.write_merge(ttoffset, ttoffset, 0, 1, '********The Total View Summary:********', self.title_style)
        
        ttoffset = ttoffset + 2
        abnormal_pair,sub_abnormal_pair = self.hold_abnormal_pair_from()
        
        ttstr = "Total abnormal data: %d" %(len(abnormal_pair))
        worksheet.write_merge(ttoffset, ttoffset, 0, 1, ttstr, self.subtitle_style)
        
        ttoffset = ttoffset + 1
        for i in range(0,len(tlabel)):
            worksheet.write(ttoffset, i, tlabel[i], self.label_style)
        ttoffset = ttoffset + 1
        for i in range(0, len(abnormal_pair)):
            cur = abnormal_pair[i]
            #imei
            worksheet.write(i+ttoffset, 0, cur[0], self.nordata_style)
            #chip id
            worksheet.write(i+ttoffset, 1, cur[1], self.get_chipid_style_for_xlwt(cur[1]))
            #have cal
            worksheet.write(i+ttoffset, 2, cur[2], self.get_data_style_for_xlwt_ex(cur[2]))
            #is dual defualt
            worksheet.write(i+ttoffset, 3, cur[3], self.get_data_style_for_xlwt(cur[3]))        
            #is quad defualt
            worksheet.write(i+ttoffset, 4, cur[4], self.get_data_style_for_xlwt(cur[4]))   
            #is bad
            worksheet.write(i+ttoffset, 5, cur[5], self.get_data_style_for_xlwt(cur[5]))
            #chipid overlap
            worksheet.write(i+ttoffset, 6, cur[6], self.get_data_style_for_xlwt(cur[6]))   
            #imei overlap
            worksheet.write(i+ttoffset, 7, cur[7], self.get_data_style_for_xlwt(cur[7]))  
        ttoffset = ttoffset + len(abnormal_pair) + 1
        
        #sub-abnormal data
        ttstr = "Total sub-abnormal data: %d" %(len(sub_abnormal_pair))
        worksheet.write_merge(ttoffset, ttoffset, 0, 1, ttstr, self.subtitle_style)
        
        ttoffset = ttoffset + 1
        for i in range(0,len(tlabel)):
            worksheet.write(ttoffset, i, tlabel[i], self.label_style)
        ttoffset = ttoffset + 1            
        for i in range(0, len(sub_abnormal_pair)):
            cur = sub_abnormal_pair[i]
            #imei
            worksheet.write(i+ttoffset, 0, cur[0], self.nordata_style)
            #chip id
            worksheet.write(i+ttoffset, 1, cur[1], self.get_chipid_style_for_xlwt(cur[1]))
            #have cal
            worksheet.write(i+ttoffset, 2, cur[2], self.get_data_style_for_xlwt_ex(cur[2]))
            #is dual defualt
            worksheet.write(i+ttoffset, 3, cur[3], self.get_data_style_for_xlwt(cur[3]))        
            #is quad defualt
            worksheet.write(i+ttoffset, 4, cur[4], self.get_data_style_for_xlwt(cur[4]))   
            #is bad
            worksheet.write(i+ttoffset, 5, cur[5], self.get_data_style_for_xlwt(cur[5]))
            #chipid overlap
            worksheet.write(i+ttoffset, 6, cur[6], self.get_data_style_for_xlwt(cur[6]))   
            #imei overlap
            worksheet.write(i+ttoffset, 7, cur[7], self.get_data_style_for_xlwt(cur[7]))  
        ttoffset = ttoffset + len(abnormal_pair) + 2        
        #worksheet2 = workbook.add_sheet('EMPTY', cell_overwrite_ok=True) 
    
    def form_result_excel(self, workbook):
        ttoffset = 0
        worksheet = workbook.add_sheet('result', cell_overwrite_ok=True)
        worksheet.col(0).width =  256 * 50
        worksheet.col(1).width =  256 * 26
        worksheet.write_merge(ttoffset, ttoffset, 0, 1, '*****Check calibration files consistency:*****', self.title_style)
        ttoffset = ttoffset + 2
        
        allCalNumInCal = set(self.lallCalNumInCal)
        allCalNumInINI = set(self.lallRidNumInINI)
        
        ttstr = "Total real cal folder number is: %d" %(len(list(allCalNumInCal)))
        worksheet.write_merge(ttoffset, ttoffset, 0, 1, ttstr, self.subtitle_style)
        ttoffset = ttoffset + 1
        
        ttstr = "Total cal serial number in INI is: %d" %(len(list(allCalNumInINI)))
        worksheet.write_merge(ttoffset, ttoffset, 0, 1, ttstr, self.subtitle_style)        
        ttoffset = ttoffset + 1
        
        ###
        mixCalNum = allCalNumInCal&allCalNumInINI
        ttstr = "calibration numbers in ini but not in cal: %d" %(len(list(allCalNumInINI-mixCalNum)))
        worksheet.write_merge(ttoffset, ttoffset, 0, 1, ttstr, self.subtitle_style)        
        ttoffset = ttoffset + 1        
        
        the_liter = 0
        for tChipID in list(allCalNumInINI-mixCalNum):
            worksheet.write(the_liter + ttoffset, 0, tChipID, self.nordata_style)
            worksheet.write(the_liter + ttoffset, 1, self.get_imei_by_chipid(tChipID), self.nordata_style)
            the_liter = the_liter + 1
        ttoffset = ttoffset + len(list(allCalNumInINI-mixCalNum)) + 2
                        
        ttstr = "calibration numbers in cal but not in ini: %d" %(len(list(allCalNumInCal-mixCalNum)))
        worksheet.write_merge(ttoffset, ttoffset, 0, 1, ttstr, self.subtitle_style)        
        ttoffset = ttoffset + 1        
        
        the_liter = 0
        for tChipID in list(allCalNumInCal-mixCalNum):
            worksheet.write(the_liter + ttoffset, 0, tChipID, self.nordata_style)
            #worksheet.write(the_liter + ttoffset, 1, self.get_imei_by_chipid(tChipID), self.label_style)
            the_liter = the_liter + 1
        ttoffset = ttoffset + len(list(allCalNumInCal-mixCalNum)) + 2
        
        ###
        countRange = 0
        imei_range_head = int(self.imeihead.get())*10
        imei_range_tail = int(self.imeitail.get())*10 + 9
        lallCalNumInINI_set = set(self.lallCalNumInINI)
                
        the_liter = 0
        for cnini in lallCalNumInINI_set:
            reImeiNo = int(cnini[0:16])
            if reImeiNo < imei_range_head or reImeiNo > imei_range_tail:
                #outResultFileHandle.write("Out of range imei: %s\n" %(cnini))
                worksheet.write(countRange + ttoffset, 0, cnini, self.nordata_style)
                countRange += 1
                
        ttoffset = ttoffset + countRange 
        ttstr = "totally %d items,and %d out of range." %(len(lallCalNumInINI_set), countRange)
        worksheet.write_merge(ttoffset, ttoffset, 0, 1, ttstr, self.subtitle_style)        
        ttoffset = ttoffset + 2
        
        ###
        ttstr = "totally %d CAL data are DUAL DEFAULT CAL data:" %(len(self.lDUALDefaultCalByChipID))
        worksheet.write_merge(ttoffset, ttoffset, 0, 1, ttstr, self.subtitle_style)        
        ttoffset = ttoffset + 1        
        
        for i in range(0, len(self.lDUALDefaultCalByChipID)):
            chipid = self.lDUALDefaultCalByChipID[i]
            worksheet.write(the_liter + ttoffset, 0, chipid, self.nordata_style)
            worksheet.write(the_liter + ttoffset, 1, self.get_imei_by_chipid(chipid), self.nordata_style)
        ttoffset = ttoffset + len(self.lDUALDefaultCalByChipID) + 2

        ###
        ttstr = "totally %d CAL data are QUAD DEFAULT CAL data:" %(len(self.lQUADDefaultCalByChipID))
        worksheet.write_merge(ttoffset, ttoffset, 0, 1, ttstr, self.subtitle_style)        
        ttoffset = ttoffset + 1        
        
        for i in range(0, len(self.lQUADDefaultCalByChipID)):
            chipid = self.lQUADDefaultCalByChipID[i]
            worksheet.write(the_liter + ttoffset, 0, chipid, self.nordata_style)
            worksheet.write(the_liter + ttoffset, 1, self.get_imei_by_chipid(chipid), self.nordata_style)
        ttoffset = ttoffset + len(self.lQUADDefaultCalByChipID) + 2
        
        pass
    
    def form_band_confirm_excel(self, workbook):
        ttoffset = 0
        worksheet = workbook.add_sheet('bd_cfm', cell_overwrite_ok=True)
        
        worksheet.col(0).width =  256 * 10
        worksheet.col(1).width =  256 * 50
        worksheet.col(2).width =  256 * 26
        worksheet.write_merge(ttoffset, ttoffset, 0, 2, '*******Band Confirm table:*******', self.title_style)
        ttoffset = ttoffset + 2
        
        worksheet.write_merge(ttoffset, ttoffset, 0, 2, 'The list below is Band support with DUAL', self.subtitle_style)
        ttoffset = ttoffset +1
        for i in range(0, len(self.lIsDUALCalByChipID)):
            tchipID = self.lIsDUALCalByChipID[i]
            worksheet.write(i + ttoffset, 0, 'DUAL', self.nordata_style)
            worksheet.write(i + ttoffset, 1, tchipID, self.nordata_style)
            worksheet.write(i + ttoffset, 2, self.get_imei_by_chipid(tchipID), self.nordata_style)
        ttoffset = ttoffset + len(self.lIsDUALCalByChipID) + 2
        
        worksheet.write_merge(ttoffset, ttoffset, 0, 2, 'The list below is Band support with QUAD', self.subtitle_style)
        ttoffset = ttoffset +1
        for i in range(0, len(self.lIsQUADCalByChipID)):
            tchipID = self.lIsQUADCalByChipID[i]
            worksheet.write(i + ttoffset, 0, 'QUAL', self.nordata_style)
            worksheet.write(i + ttoffset, 1, tchipID, self.nordata_style)
            worksheet.write(i + ttoffset, 2, self.get_imei_by_chipid(tchipID), self.nordata_style)
        ttoffset = ttoffset + len(self.lIsQUADCalByChipID) + 2
        
        worksheet.write_merge(ttoffset, ttoffset, 0, 2, 'The list below is Band support with NONE(error with CAL)', self.subtitle_style)
        ttoffset = ttoffset +1
        for i in range(0, len(self.lIsNULLBandCalByChipID)):
            tchipID = self.lIsNULLBandCalByChipID[i]
            worksheet.write(i + ttoffset, 0, 'NULL', self.nordata_style)
            worksheet.write(i + ttoffset, 1, tchipID, self.nordata_style)
            worksheet.write(i + ttoffset, 2, self.get_imei_by_chipid(tchipID), self.nordata_style)
        ttoffset = ttoffset + len(self.lIsNULLBandCalByChipID) + 2        
        
        pass
    
    def form_comparison_excel(self, workbook):
        ttoffset = 0
        worksheet = workbook.add_sheet('cpsn', cell_overwrite_ok=True)
        
        worksheet.col(0).width =  256 * 26
        worksheet.col(1).width =  256 * 50
        worksheet.write_merge(ttoffset, ttoffset, 0, 1, '****The Comparison Table For IMEI and ChipID****', self.title_style)
        ttoffset = ttoffset + 2        
        
        for i in range(0, len(self.IMEIAndChipIDPair)):
            tPair0 = self.IMEIAndChipIDPair[i][0]
            tPair1 = self.IMEIAndChipIDPair[i][1]
            worksheet.write(i + ttoffset, 0, tPair0, self.nordata_style)
            worksheet.write(i + ttoffset, 1, tPair1, self.nordata_style)
        ttoffset = ttoffset + len(self.IMEIAndChipIDPair) + 2
        
        pass
                   
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
        
        self.totalView = []
        
        self.version_info = "imei_cal_match_it version v1.1119Beta"
        self.a_null_chip_id = "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"
        
        self.overlaped_imei = [] #different imei use same chipid with cal
        
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()
        
        self.init_font_style()
        
        
if __name__=="__main__":
    root = Tk()
    
    #lock the size
    root.minsize(300,160)
    root.maxsize(300,160)
    
    app = Application(master=root)
    app.mainloop()

