#!/usr/bin/python
#imei_cal_match_it_50_gui_check_3g.pyw

import Tkinter
from Tkinter import *
import tkMessageBox
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
import ConfigParser as cparser
import shutil



the_first_lay_dir = False

IS_FOR_CASTLE_TST = True #False True

#release note:
#v1.1101Beta -->fix bug when checking band support
#v1.1105Beta -->add a new Entry to appoint Cal PATH
#v1.1111Beta -->add a Progressbar
#v1.1119Beta -->add overlap check for imei and chip id
#v1.1121Beta -->output excel as report, need install xlwt module first for your python
#v1.1200Beta -->fill the ENTRY for UI
#current_version = "v1.1210Beta" #-->add error message box for exceptions
#current_version = "v1.1212Beta" #-->divided top view to two sheet, for abnormal data view 
#current_version = "v1.1220Beta" #-->more REF calibrate data for check, not use 'X' at invalid imei
current_version = "[check] v6.0100Beta" #-->copy cal file to custom dir

class Application(Frame):
    xlsioException = 0
    refFileException = 0

    default_config_ini =    ["\n[UI setting]\n",
                             "process_folder = 1307004-1008-t-3g\n",
                             "calibrat_folder = Z\NVRAM\NVD_IMEI\n",
                             "imei_range_head = 35909402000000\n",
                             "imei_range_tail = 35909402000005\n",
                             "\n[Inner setting]\n",
                             "timerange_head = 2013-07-25 00:00:00\n",
                             "timerange_tail = 2014-12-25 00:00:00\n",
                             "need_scatter_imei = 0 ;0 or 1\n",
                             "check_st33_files = 0 ;0 or 1 for WASION project\n",
                             "ref_calibrat_dir = REFCALIBRAT_3G\n",
                             "auto_open_result_file = 1\n",
                             "cust_cal_folder = 0\n"]
    
    #to walk through the dir
    def mydir(self, arg, dirname, names):
        #global gNvCalPath
        global the_first_lay_dir
        fileget = [normpath(tfile) for tfile in names]
        fullfilename = [abspath(join(dirname,tfile)) for tfile in names]
        #copy it, $file and $fullfilename are one-one correspondence
        if(dirname == self.contents.get()):
            pass
            #print "totall files:" + dirname + "===>" +str(len(fileget))+"\n"
        for i in range(0,len(fileget)):
            if isfile(fullfilename[i]):#only save files
                #save WriteIMEI*.ini files
                p = re.compile("WriteIMEI.*\.ini$")
                matchit = p.match(fileget[i])
                if matchit:
                    #print matchit.group()
                    print 'find on WriteImei_ini file: ' + fileget[i]
                    self.list_ini_files.append(fullfilename[i])
                    #continue
                
            if isdir(fullfilename[i]):#only save path
                #save cal files's RID
                p = re.compile("[0-9A-Fa-f]{32}")
                matchit = p.match(fullfilename[i][-32:])
                if matchit:
                    self.lallCalNumInCal.append(fullfilename[i][-32:])# save RID
                    
                    #print 'processing ' + fullfilename[i][-32:]
                    confirm_band_support = False
                    #for j in range(0, int(self.config_ini_data['ref_calibrat_num'])):
                    for tpath in self.ref_path_list:
                            
                        #here we need to compare with DEFAULT cal file under \Z\NVRAM\CALIBRAT\    
                        #check DAUL DATA
                        dmatch, dmismatch, derrors = filecmp.cmpfiles(join(str(fullfilename[i]), gNvCalPath), join(self.config_ini_data['ref_calibrat_dir'], tpath), self.DUALCalFileList, shallow=False)
                        #qmatch, qmismatch, qerrors = filecmp.cmpfiles(join(str(fullfilename[i]), gNvCalPath), join(self.config_ini_data['ref_calibrat_dir'], tpath, "QUAD"), self.QUADCalFileList, shallow=False)
                        
                        #print join(str(fullfilename[i]), gNvCalPath)
                        #print join(self.config_ini_data['ref_calibrat_dir'], str(i), "DUAL")
                        #print "Dual result: %d-%d-%d" %(len(dmatch), len(dmismatch), len(derrors)) 
                        #print "Quad result: %d-%d-%d" %(len(qmatch), len(qmismatch), len(qerrors))
                        
                        if(not os.path.isdir(join(str(fullfilename[i]), 'Z\NVRAM\CALIBRAT'))):
                            self.lIsNULLBandCalByChipID.append(fullfilename[i][-32:])
                        else:
                            if len(os.listdir(join(str(fullfilename[i]), 'Z\NVRAM\CALIBRAT'))) < 140:
                                self.lIsNULLBandCalByChipID.append(fullfilename[i][-32:])
                        
                        if(len(derrors) == 0):
                            self.lIsDUALCalByChipID.append(fullfilename[i][-32:])
                        else:
                            self.lIsNULLBandCalByChipID.append(fullfilename[i][-32:])
                                                          
                        if(len(dmatch) == 4):
                            if fullfilename[i][-32:] not in self.lDUALDefaultCalByChipID:
                                self.lDUALDefaultCalByChipID.append(fullfilename[i][-32:])
                                              
                    #continue
                    if(int(self.config_ini_data['check_st33_files'])):
                        self.sum_ws_st33_file_number(str(fullfilename[i]))
                        
            if(dirname == self.contents.get()):
                #update bar 
                show_value = i*100/len(fileget)
                self.pbar.config(value=show_value)
                
                #and ignore other type of files
        if(the_first_lay_dir == False):
            the_first_lay_dir = True
        #print "\n".join(list_ini_files)       

    def sum_ws_st33_file_number(self, tdir):
        st33number = 0
        for parent, dirnames, filenames in os.walk(tdir+"\\Z\\NVRAM\\NVD_IMEI"):
            for filename in filenames:
                #print "SEE ST33 file?-->" + filename + "\n"
                p = re.compile("ST33.*")
                matchit = p.match(filename)
                if matchit:
                    st33number = st33number + 1
        if st33number > 1:
            #print "GET ONE LIST: " + tdir[-32:] +" is ST33" + "\n"
            self.ws_st33_file_number = self.ws_st33_file_number + 1
        else:
            #print "GET ONE LIST: " + tdir[-32:] +" is NOT ST33" + "\n"
            self.ws_not_st33_file_number = self.ws_not_st33_file_number + 1
            self.NotST33FileList.append(tdir[-32:])
        return 0
           
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
               or tpair[4] != 0 or tpair[5] != 0):
                abnormal_pair.append(tpair)
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
    
        self.ws_st33_file_number = 0
        self.ws_not_st33_file_number = 0
        del self.NotST33FileList[:]
        del self.olpWhenCpyByChipID[:]
        del self.imei_range_arry[:]
        self.imei_with_time_dic.clear()
        
    def run_check(self, tpath, thead, ttail, calpath):
        
        global gNvCalPath
        gNvCalPath = calpath
                
        print self.version_info , '\n'
        print "Cal Path:" , gNvCalPath, '\n' 
        print "[path imeiHead imeiTail]"
        
        path = tpath
        imei_range_head = int(thead)*10
        imei_range_tail = int(ttail)*10 + 9
        #print("searching range: [%d, %d]\n" %(imei_range_head, imei_range_tail))
        
        #some check work before running
        if(not os.path.isdir(path)):
            root.event_generate('<<PROCESS_DIR_ERROR>>', when='tail')
            return           
        
        try:
            self.check_ref_cal_files()
        except Exception as e:
            #print ("Workbook save exception: %s" % e)
            Application.refFileException = str(e);
            root.event_generate('<<REFCALIBRAT_ERROR>>', when='tail')
            return
        
        
        workbook = xlwt.Workbook()
        workbook.add_sheet('only test', cell_overwrite_ok=True)
        try:
            workbook.save('TotalView.xls')
        except Exception as e:
            Application.xlsioException = str(e);
            root.event_generate('<<XLS_ERROR>>', when='tail')
            self.lb_title["text"] = "pls close opened xls file!"
            return

        
        ###
        if os.path.isfile('main_ini_file.ini'):
            #print 'Begin to delete TotalView.xls'
            os.remove('main_ini_file.ini') 
        newiniFileHandle = open('main_ini_file.ini','w+')
        for parent, dirnames, filenames in os.walk(self.config_ini_data['process_folder']):
            for tfile in filenames:
                p = re.compile("WriteIMEI.*\.ini")
                matchit = p.match(tfile)
                if matchit:
                    #print matchit.group()
                    iniFHandle = open(join(parent, tfile),'r')
                    newiniFileHandle.write(iniFHandle.read())
                    iniFHandle.close()

        newiniFileHandle.close()
        
        if self.config_ini_data['cust_cal_folder'] != '0':
            print 'need to cpy all cal files to cust folder!!!'
            self.cpy_cal_files_to_cust_folder()
            path = self.config_ini_data['cust_cal_folder']
            shutil.copyfile("main_ini_file.ini", self.config_ini_data['cust_cal_folder'] + "\\WriteIMEI.ini")
        
        
        self.lb_title["text"] = 'seraching ' + path
        
        print 'Walk with ' + path
        walk(path, self.mydir, 1)
        
        self.pbar.config(value=110)
     
        """
        Parse the imei from WriteIMEI*.ini
        """
        if len(self.list_ini_files)==0:
            print ("No WriteIMEI.ini found!\n exit\n")
            self.lb_title["text"] = "Error:No WriteIMEI.ini!"
            self.hi_there["state"] = "active"
            #show the warning messagebox
            root.event_generate('<<Ask>>', when='tail')
            return
        
        #get time head and tail
        self.time_range_head = self.time_to_int(self.config_ini_data['timerange_head'])
        self.time_range_tail = self.time_to_int(self.config_ini_data['timerange_tail'])
        
        if self.time_range_head == 0 or self.time_range_tail == 0:
            root.event_generate('<<TIMERANGE_ERROR>>', when='tail')
            return
     
        #really begin to check
        need_imei_range = 1
        for iniFile in self.list_ini_files:
            iniFileHandle = open(iniFile,'r')
            readState = 0
            imei_state = 0
            imei_header_reg = 0
            matchit1 = 0
            matchit2 = 0
            matchit3 = 0
            strIMEI = 0
            strChipID = 0
            strTime = 0
            imei_h = 0
            imei_t = 0
            #only read the first WriteIMEI.ini for imei range
            while True:
                line = iniFileHandle.readline()
                
                if not line:
                    iniFileHandle.close()
                    readState = 0
                    break
                if(need_imei_range):
                    if imei_state == 0:
                        imei_r_h = "Range\dStart = (\d{15})"
                        imei_h = re.search(imei_r_h, line)
                        if imei_h:
                            self.contentshead.set(imei_h.group(1)[0:14])
                            imei_range_head = int(imei_h.group(1)[0:14])
                            thead = imei_range_head
                            imei_header_reg = imei_range_head
                            imei_state = 1
                            
                    if imei_state == 1:
                        imei_r_t = "Range\dEnd = (\d{15})"
                        imei_t = re.search(imei_r_t, line)
                        if imei_t:
                            self.contentstail.set(imei_t.group(1)[0:14])
                            imei_range_tail = int(imei_t.group(1)[0:14])
                            ttail = imei_range_tail
                            if(ttail>imei_header_reg):
                                self.imei_range_arry.append((imei_header_reg, ttail))
                            imei_state = 0

                imei = "\[\d{15}\]" #a real imei
                matchit1 = re.search(imei, line)
                if matchit1:
                    self.lallCalNumInINI.append(matchit1.group()[1:16])
                    readState = 1
                    strIMEI = matchit1.group()[1:16]
                    
                timed = "time=\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
                matchit2 = re.search(timed, line)
                if matchit2:
                    if(readState == 1):
                        readState = 2
                        strTime = matchit2.group()[5:24]
                    
                rid = "rid=[0-9A-Fa-f]{32}" #a real rid
                matchit3 = re.search(rid, line)
                if matchit3:
                    self.lallRidNumInINI.append(matchit3.group()[4:36])
                    if(readState == 2):
                        readState = 3
                        strChipID = matchit3.group()[4:36]
                """        
                ischeck = "check=1"
                matchit4 = re.search(ischeck, line)
                if matchit4:
                    if(readState == 3):
                        readState = 4
                """        
                if readState == 3:
                    t_pair = (strIMEI, strChipID, strTime)
                    if(t_pair not in self.IMEIAndChipIDPair):
                        self.IMEIAndChipIDPair.append(t_pair)
                    readState = 0
                    self.imei_with_time_dic[strIMEI] = strTime
                    
            need_imei_range = 0        
            iniFileHandle.close()
            readState = 0
            
   
        print ("time range: %d:%d" %(self.time_range_head, self.time_range_tail))
        
        #for ttPair in self.imei_with_time_dic:
        #print (self.imei_with_time_dic.items())
    
        #Comparison Table, now is the total view
        #total view: <imei><chip id><is cal exist><DUAL is defult><QUAD is defult><cal is bad>[be chipid overlap][imei overlap]
        #init total view:
        
        self.lb_title["text"] = 'process big table'
        del self.imei_range_arry[:]
        self.imei_range_arry.append((int(self.config_ini_data['imei_range_head']), int(self.config_ini_data['imei_range_tail'])))
        for imei_range_pair in self.imei_range_arry:
            print "Get one range pair: %d--->%d" %(imei_range_pair[0], imei_range_pair[1])
            for i in range(imei_range_pair[0], imei_range_pair[1]+1):
                t_pair = [i, self.a_null_chip_id, 0, 1, 1, 1, 0, 0]
                if t_pair not in self.totalView:
                    self.totalView.append(t_pair)
        
        for tpair in self.totalView:
         
            tpair[1] = self.get_chipid_by_imei(str(tpair[0]))
            #print 'big table: %s' %(str(tpair[0]))
            #check over-lapped chipid:
            """
            if(tpair[1] != self.a_null_chip_id):
                temp_imei = self.get_imei_by_chipid(tpair[1])
                if(str(tpair[0]) == temp_imei[0:14]):
                    pass  
                else:#may use a used chip id
                    tpair[6] = tpair[6] + 1
            """

            #tpair[6] = tpair[6] - 1        
            
            temp_imei = self.get_full_imei_by_imei(str(tpair[0]))
            if(len(temp_imei) != 0):
                tpair[0] = temp_imei[:14] + '|' + temp_imei[14:]
            else:
                tpair[0] = str(tpair[0]) + '|' + str(self.get_imei_x_bit(str(tpair[0])))

            #self.IMEIAndChipIDPair
            cur_time_stp = '0000-00-00 00:00:00'
            for tiple_pair in self.IMEIAndChipIDPair:
                if(tpair[1] == tiple_pair[1] and tpair[0][0:14] == tiple_pair[0][0:14]):
                    if(self.time_to_int(cur_time_stp) < self.time_to_int(tiple_pair[2])):#get the last stamp
                        cur_time_stp = tiple_pair[2]
                        #print 'Get self timestamp: ' + cur_time_stp

            for tiple_pair in self.IMEIAndChipIDPair:
                if(tpair[1] == tiple_pair[1] and tpair[0] != tiple_pair[0]):
                    if(self.time_to_int(cur_time_stp) < self.time_to_int(tiple_pair[2])):#it's older
                        #print 'it is older: %s==>%s' %(cur_time_stp, tiple_pair[2]) 
                        tpair[6] = tpair[6] + 1
                       
            tpair[2] = self.if_cal_file_exist(tpair[1])
            tpair[3] = self.if_cal_file_is_dual_defualt(tpair[1])
            tpair[4] = self.if_cal_file_is_quad_defualt(tpair[1])
            tpair[5] = self.if_cal_file_is_bad_cal(tpair[1])            

            #print("See total view: %dX--->%s--->%d:%d:%d:%d" %(tpair[0], tpair[1], tpair[2], tpair[3], tpair[4], tpair[5])) 
            
            #check over-lapped imei:
            same_imei_pair = []
            for ttPair in self.IMEIAndChipIDPair:
                if(ttPair[0][:14] == tpair[0][:14] and len(ttPair[0]) != 0):
                    same_imei_pair.append((ttPair[0], ttPair[1]))# well, now the pair included timestamp, ignore it
            set_for_same_imei_pair = set(same_imei_pair)
            if(len(set_for_same_imei_pair) > 1):
                tpair[7] = len(set_for_same_imei_pair)-1
        
        #excel:::
        self.lb_title["text"] = 'Generate result xls'
        
        try:
            workbook = xlwt.Workbook()
            
            self.form_total_view_excel(workbook)
            self.form_total_abnormal_excel(workbook)
            self.form_result_excel(workbook)
            
            """
            self.form_band_confirm_excel(workbook)
            self.form_comparison_excel(workbook)
            if(int(self.config_ini_data['check_st33_files'])):
                self.form_st33_check_excel(workbook)
            self.form_combine_result_excel(workbook)
            """
            
            '''    
            self.try_to_close_xls_program()
            if os.path.isfile('TotalView.xls'):
                print 'Begin to delete TotalView.xls'
                os.remove('TotalView.xls')    
        '''    

            #os.system('taskkill /f /im et.exe')
            #os.system('taskkill /f /im EXCEL.EXE')

            workbook.save('TotalView.xls')
        except Exception as e:
            print ("Workbook save exception: %s" % e)
            Application.xlsioException = str(e);
            root.event_generate('<<XLS_ERROR>>', when='tail')
            self.lb_title["text"] = "pls close opened xls file!"
        else:
            self.lb_title["text"] = "FINISHED!"
            self.pbar.config(value=120)
            #really finished, open excel file?
            if(int(self.config_ini_data['auto_open_result_file'])):
                #os.system(r'TotalView.xls')
                os.startfile('TotalView.xls')
        finally:
            #INPUT_SOME = raw_input("Press ENTER key to exit.")
            self.do_clean_work()
            self.hi_there["state"] = "active"
       
        
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
        
    def callCheckbutton(self):    
        print("callCheckbutton")
        print self.checkv.get()
        
    def tst_click(self):
        print("tst_click")
        
    def createWidgets(self):
        global IS_FOR_CASTLE_TST
        self.lb_title = Label(root,text = self.version_info)
        self.lb_title.pack({"side": "top"})
        
        #path for workspace
        self.entrythingy = Entry(justify = "left",width = 40)
        self.entrythingy.pack(expand=YES, fill=BOTH)

        # here is the application variable
        self.contents = StringVar()
        # set it to some value
        if(IS_FOR_CASTLE_TST != True):
            self.contents.set(self.config_ini_data['process_folder'])
        else:
            self.contents.set(self.config_ini_data['process_folder'])
        # tell the entry widget to watch this variable
        self.entrythingy["textvariable"] = self.contents
        self.entrythingy["state"] = 'disabled'
        #self.entrythingy["click"] = self.tst_click
        
        # and here we get a callback when the user hits return.
        # we will have the program print out the value of the
        # application variable when the user hits return
        self.entrythingy.bind('<Key-Return>', self.print_contents)
        
       
       
        #path for NVRAM CAL DATA
        self.calpathentry = Entry(justify = "left",width = 40)
        self.calpathentry.pack(expand=YES, fill=BOTH)

        # here is the application variable
        self.contentscal = StringVar()
        # set it to some value
        self.contentscal.set(self.config_ini_data['calibrat_folder'])
        # tell the entry widget to watch this variable
        self.calpathentry["textvariable"] = self.contentscal   
       
        vcmd = (self.register(self.validate),'%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        #head
        self.imeihead = Entry(validate = 'key', justify = "left",width = 40)
        self.imeihead.pack(expand=YES, fill=BOTH)

        # here is the application variable
        self.contentshead = StringVar()
        # set it to some value
        self.contentshead.set(self.config_ini_data['imei_range_head'])

        self.imeihead["textvariable"] = self.contentshead
        self.imeihead["state"] = 'disabled'
        
        #tail
        self.imeitail = Entry(validate = 'key', justify = "left",width = 40)
        self.imeitail.pack(expand=YES, fill=BOTH)

        # here is the application variable
        self.contentstail = StringVar()
        # set it to some value
        self.contentstail.set(self.config_ini_data['imei_range_tail'])

        self.imeitail["textvariable"] = self.contentstail
        self.imeitail["state"] = 'disabled'
        
        self.hi_there = Button(self, relief=RAISED, width = 15)
        self.hi_there["text"] = "RUN",
        self.hi_there["fg"] = "blue"
        self.hi_there["command"] = self.say_hi
        
        self.hi_there.pack({"side": "left"})
        
        
        self.SAVE = Button(self, relief=RAISED, width = 15)
        self.SAVE["text"] = "SAVE"
        self.SAVE["fg"] = "blue"
        self.SAVE["command"] = self.save_to_config_ini

        self.SAVE.pack({"side": "left"})       
        
        self.QUIT = Button(self, relief=RAISED, width = 15)
        self.QUIT["text"] = "QUIT"
        self.QUIT["fg"] = "red"
        self.QUIT["command"] = self.quit

        self.QUIT.pack({"side": "left"})

        """
        self.checkv = IntVar()
        if(int(self.config_ini_data['need_scatter_imei'])):
            self.checkv.set(1)
        self._checkbutton = Checkbutton(self, variable = self.checkv, text = "scatter", command = self.callCheckbutton)
        self._checkbutton.pack({"side": "right"})
        """
        self.pbar = ttk.Progressbar(root, orient = "horizontal", length=370, maximum=120)
        self.pbar.pack(expand=YES, fill=BOTH)

    def validate(self, action, index, value_if_allowed, prior_value, text, validation_type, trigger_type, widget_name):             
        if len(value_if_allowed) > 14:
            return False

        if text in '0123456789':
            return True
        else:
            return False

    def init_font_style(self):
        
        #add border
        borders = xlwt.Borders()
        borders.left = 1
        borders.right = 1
        borders.top = 1
        borders.bottom = 1
        borders.bottom_colour = 0x3A    
        
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
        self.title_style.borders = borders 

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
        self.subtitle_style.borders = borders 
        
        #label font and style
        labelfont = xlwt.Font() # Create Font 
        labelfont.bold = True # Set font to Bold 
        labelfont.name = 'Verdana'#'Times New Roman'
        labelfont.height =  20 * 12 #12ptx

        labelpattern = xlwt.Pattern()
        labelpattern.pattern = xlwt.Pattern.SOLID_PATTERN
        labelpattern.pattern_fore_colour = xlwt.Style.colour_map['gray25']#Search in Style.py for _colour_map_text

        self.label_style = xlwt.XFStyle() # Create Style 
        self.label_style.font = labelfont # Add Bold Font to Style 
        self.label_style.pattern = labelpattern        
        self.label_style.borders = borders 
        
        #normal data font and style
        ndfont = xlwt.Font() # Create Font 
        #ndfont.bold = True # Set font to Bold 
        ndfont.name = 'Lucida Sans Typewriter'#'Times New Roman''Lucida Sans Typewriter'
        ndfont.height =  20 * 13 #12ptx

        ndpattern = xlwt.Pattern()
        #ndpattern.pattern = xlwt.Pattern.SOLID_PATTERN
        #ndpattern.pattern_fore_colour = xlwt.Style.colour_map['gray80']#Search in Style.py for _colour_map_text

        self.nordata_style = xlwt.XFStyle() # Create Style 
        self.nordata_style.font = ndfont # Add Bold Font to Style 
        self.nordata_style.pattern = ndpattern
        self.nordata_style.borders = borders 
        
        #abnormal data font and style
        adfont = xlwt.Font() # Create Font 
        adfont.bold = True # Set font to Bold 
        adfont.name = 'Lucida Sans Typewriter'#'Times New Roman'
        adfont.height =  20 * 13 #12ptx

        adpattern = xlwt.Pattern()
        adpattern.pattern = xlwt.Pattern.SOLID_PATTERN
        adpattern.pattern_fore_colour = xlwt.Style.colour_map['red']#Search in Style.py for _colour_map_text

        self.abnordata_style = xlwt.XFStyle() # Create Style 
        self.abnordata_style.font = adfont # Add Bold Font to Style 
        self.abnordata_style.pattern = adpattern
        self.abnordata_style.borders = borders 
        
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
        
        worksheet.panes_frozen = True
        worksheet.remove_splits = True
        worksheet.horz_split_pos = 4
        
        #set titles
        worksheet.write_merge(ttoffset, ttoffset, 0, 1, '********The Total View Table For Check:********', self.title_style) 
        ttoffset = ttoffset + 2
        ttstr = "Total count theoretically: %d" %(len(self.totalView))
        worksheet.write_merge(ttoffset, ttoffset, 0, 1, ttstr, self.subtitle_style)
        
        #set label
        ttoffset = ttoffset + 1
        tlabel = ['IMEI', 'Chip ID', 'have cal', 'DUAL DFT', 'QUAD DFT', 'Is bad?']
        for i, e in zip(range(len(tlabel)), tlabel):
        #for i in range(0,len(tlabel)):
            worksheet.write(ttoffset, i, e, self.label_style)

        #set datas
        ttoffset = ttoffset + 1
        for i, e in zip(range(len(self.totalView)), self.totalView):
            #imei
            worksheet.write(i+ttoffset, 0, e[0], self.nordata_style)
            #chip id
            worksheet.write(i+ttoffset, 1, e[1], self.get_chipid_style_for_xlwt(e[1]))
            #have cal
            worksheet.write(i+ttoffset, 2, e[2], self.get_data_style_for_xlwt_ex(e[2]))
            #is dual defualt
            worksheet.write(i+ttoffset, 3, e[3], self.get_data_style_for_xlwt(e[3]))        
            #is quad defualt
            worksheet.write(i+ttoffset, 4, e[4], self.get_data_style_for_xlwt(e[4]))   
            #is bad
            worksheet.write(i+ttoffset, 5, e[5], self.get_data_style_for_xlwt(e[5]))
            #chipid overlap
            #worksheet.write(i+ttoffset, 6, e[6], self.get_data_style_for_xlwt(e[6]))   
            #imei overlap
            #worksheet.write(i+ttoffset, 7, e[7], self.get_data_style_for_xlwt(e[7]))   
        ttoffset = ttoffset + len(self.totalView) + 2
        
        
    
    def form_total_abnormal_excel(self, workbook):
        ttoffset = 0
        worksheet = workbook.add_sheet('result', cell_overwrite_ok=True)
        worksheet.col(0).width =  256 * 26
        worksheet.col(1).width =  256 * 50
        
        for i in range(2, 8):
            worksheet.col(i).width =  256 * 15
        
        worksheet.panes_frozen = True
        worksheet.remove_splits = True
        worksheet.horz_split_pos = 5
        
        #set titles
        worksheet.write_merge(ttoffset, ttoffset, 0, 1, '********The Total Abnormal Table For Check:********', self.title_style) 
        ttoffset = ttoffset + 2
        ttstr = "Total count theoretically: %d" %(len(self.totalView))
        worksheet.write_merge(ttoffset, ttoffset, 0, 1, ttstr, self.subtitle_style)
        
        ttoffset = ttoffset + 1
        
        abnormal_pair,sub_abnormal_pair = self.hold_abnormal_pair_from()
        ttstr = "Total abnormal data: %d while good data: %d" %(len(abnormal_pair), len(self.totalView)-len(abnormal_pair))
        worksheet.write_merge(ttoffset, ttoffset, 0, 1, ttstr, self.subtitle_style)
        
        ttoffset = ttoffset + 1
        tlabel = ['IMEI', 'Chip ID', 'have cal', 'DUAL DFT', 'QUAD DFT', 'Is bad?']
        for i, e in zip(range(len(tlabel)), tlabel):
        #for i in range(0,len(tlabel)):
            worksheet.write(ttoffset, i, e, self.label_style)
         
        ttoffset = ttoffset + 1

        for i, e in zip(range(len(abnormal_pair)), abnormal_pair):
            #imei
            worksheet.write(i+ttoffset, 0, e[0], self.nordata_style)
            #chip id
            worksheet.write(i+ttoffset, 1, e[1], self.get_chipid_style_for_xlwt(e[1]))
            #have cal
            worksheet.write(i+ttoffset, 2, e[2], self.get_data_style_for_xlwt_ex(e[2]))
            #is dual defualt
            worksheet.write(i+ttoffset, 3, e[3], self.get_data_style_for_xlwt(e[3]))        
            #is quad defualt
            worksheet.write(i+ttoffset, 4, e[4], self.get_data_style_for_xlwt(e[4]))   
            #is bad
            worksheet.write(i+ttoffset, 5, e[5], self.get_data_style_for_xlwt(e[5]))
            #chipid overlap
            #worksheet.write(i+ttoffset, 6, e[6], self.get_data_style_for_xlwt(e[6]))   
            #imei overlap
            #worksheet.write(i+ttoffset, 7, e[7], self.get_data_style_for_xlwt(e[7]))  
        ttoffset = ttoffset + len(abnormal_pair) + 1
        
        pass
    
    def form_result_excel(self, workbook):
        ttoffset = 0
        worksheet = workbook.add_sheet('resultb', cell_overwrite_ok=True)
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
        #for i, e in zip(range(len(list(allCalNumInINI-mixCalNum))), list(allCalNumInINI-mixCalNum)):
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
            tResult = ''
            if(self.if_cal_file_is_bad_cal(tChipID)):
                tResult = 'Bad Data'
            else:
                if(self.if_cal_file_is_dual_defualt(tChipID)):
                    tResult = 'Dual Defual'
                elif(self.if_cal_file_is_quad_defualt(tChipID)):
                    tResult = 'Quad Defual'
                else:
                    tResult = 'OK'
            if tResult == 'OK':
                tStyle = self.nordata_style
            else:
                tStyle = self.abnordata_style
            worksheet.write(the_liter + ttoffset, 1, tResult, tStyle)
            #worksheet.write(the_liter + ttoffset, 1, self.get_imei_by_chipid(tChipID), self.label_style)
            the_liter += 1
        ttoffset = ttoffset + len(list(allCalNumInCal-mixCalNum)) + 2
        
        ###
        countRange = 0
        imei_range_head = int(self.imeihead.get())*10
        imei_range_tail = int(self.imeitail.get())*10 + 9
        lallCalNumInINI_set = set(self.lallCalNumInINI)
                
        the_liter = 0
        for (k, v) in self.imei_with_time_dic.items():
            #print ("%s-->%s" %(k, v))
            reImeiNo = int(k[0:16])
            if (not self.is_imei_in_range(reImeiNo)):
                if(self.time_to_int(v)>self.time_range_head and self.time_to_int(v)<self.time_range_tail):
                    #outResultFileHandle.write("Out of range imei: %s\n" %(cnini))
                    worksheet.write(countRange + ttoffset, 0, v, self.nordata_style)
                    worksheet.write(countRange + ttoffset, 1, k, self.nordata_style)
                    countRange += 1

        ttoffset = ttoffset + countRange 
        ttstr = "totally %d items,and %d out of range." %(len(lallCalNumInINI_set), countRange)
        worksheet.write_merge(ttoffset, ttoffset, 0, 1, ttstr, self.subtitle_style)        
        ttoffset = ttoffset + 2
        
        ###
        ttstr = "totally %d CAL data are DUAL DEFAULT CAL data:" %(len(self.lDUALDefaultCalByChipID))
        worksheet.write_merge(ttoffset, ttoffset, 0, 1, ttstr, self.subtitle_style)        
        ttoffset = ttoffset + 1        
    
        for i, e in zip(range(len(self.lDUALDefaultCalByChipID)), self.lDUALDefaultCalByChipID):
            worksheet.write(the_liter + ttoffset, 0, e, self.nordata_style)
            worksheet.write(the_liter + ttoffset, 1, self.get_imei_by_chipid(e), self.nordata_style)
        ttoffset = ttoffset + len(self.lDUALDefaultCalByChipID) + 2

        ###
        ttstr = "totally %d CAL data are QUAD DEFAULT CAL data:" %(len(self.lQUADDefaultCalByChipID))
        worksheet.write_merge(ttoffset, ttoffset, 0, 1, ttstr, self.subtitle_style)        
        ttoffset = ttoffset + 1        
        for i, e in zip(range(len(self.lQUADDefaultCalByChipID)), self.lQUADDefaultCalByChipID):
            worksheet.write(the_liter + ttoffset, 0, e, self.nordata_style)
            worksheet.write(the_liter + ttoffset, 1, self.get_imei_by_chipid(e), self.nordata_style)
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
        for i, e in zip(range(len(self.lIsDUALCalByChipID)), self.lIsDUALCalByChipID):
            worksheet.write(i + ttoffset, 0, 'DUAL', self.nordata_style)
            worksheet.write(i + ttoffset, 1, e, self.nordata_style)
            worksheet.write(i + ttoffset, 2, self.get_imei_by_chipid(e), self.nordata_style)
        ttoffset = ttoffset + len(self.lIsDUALCalByChipID) + 2
        
        worksheet.write_merge(ttoffset, ttoffset, 0, 2, 'The list below is Band support with QUAD', self.subtitle_style)
        ttoffset = ttoffset +1
        for i, e in zip(range(len(self.lIsQUADCalByChipID)), self.lIsQUADCalByChipID):
            worksheet.write(i + ttoffset, 0, 'QUAL', self.nordata_style)
            worksheet.write(i + ttoffset, 1, e, self.nordata_style)
            worksheet.write(i + ttoffset, 2, self.get_imei_by_chipid(e), self.nordata_style)
        ttoffset = ttoffset + len(self.lIsQUADCalByChipID) + 2
        
        worksheet.write_merge(ttoffset, ttoffset, 0, 2, 'The list below is Band support with NONE(error with CAL)', self.subtitle_style)
        ttoffset = ttoffset +1
        for i, e in zip(range(len(self.lIsNULLBandCalByChipID)), self.lIsNULLBandCalByChipID):
            worksheet.write(i + ttoffset, 0, 'NULL', self.nordata_style)
            worksheet.write(i + ttoffset, 1, e, self.nordata_style)
            worksheet.write(i + ttoffset, 2, self.get_imei_by_chipid(e), self.nordata_style)
        ttoffset = ttoffset + len(self.lIsNULLBandCalByChipID) + 2        
        
        pass
    
    def form_comparison_excel(self, workbook):
        ttoffset = 0
        worksheet = workbook.add_sheet('cpsn', cell_overwrite_ok=True)
        
        worksheet.col(0).width =  256 * 26
        worksheet.col(1).width =  256 * 50
        worksheet.write_merge(ttoffset, ttoffset, 0, 1, '****The Comparison Table For IMEI and ChipID****', self.title_style)
        ttoffset = ttoffset + 2        
        
        for i, e in zip(range(len(self.IMEIAndChipIDPair)), self.IMEIAndChipIDPair):
            worksheet.write(i + ttoffset, 0, e[0], self.nordata_style)
            worksheet.write(i + ttoffset, 1, e[1], self.nordata_style)
        ttoffset = ttoffset + len(self.IMEIAndChipIDPair) + 2
        
        pass
          
    def form_st33_check_excel(self, workbook):
        ttoffset = 0
        worksheet = workbook.add_sheet('st33', cell_overwrite_ok=True)
        
        worksheet.col(0).width =  256 * 50  
        worksheet.col(1).width =  256 * 26
        worksheet.write_merge(ttoffset, ttoffset, 0, 1, '****The Check work for ST33****', self.title_style)
        ttoffset = ttoffset + 2        
        
        ttstr = "CAL NUMS with ST33* > 1 = %d" %(self.ws_st33_file_number)
        worksheet.write_merge(ttoffset, ttoffset, 0, 1, ttstr, self.subtitle_style)   
        ttoffset = ttoffset + 1
        ttstr = "CAL NUMS with ST33* < 1 = %d" %(self.ws_not_st33_file_number)
        worksheet.write_merge(ttoffset, ttoffset, 0, 1, ttstr, self.subtitle_style)   
        ttoffset = ttoffset + 2
        
        ttstr = "NOT ENOUGH ST33 by chip id and imei:"
        worksheet.write_merge(ttoffset, ttoffset, 0, 1, ttstr, self.subtitle_style)   
        ttoffset = ttoffset + 1
        the_liter = 0
        for i, e in zip(range(len(self.NotST33FileList)), self.NotST33FileList):
            worksheet.write(the_liter + ttoffset, 0, e, self.nordata_style)
            worksheet.write(the_liter + ttoffset, 1, self.get_imei_by_chipid(e), self.nordata_style)
            the_liter = the_liter + 1
        ttoffset = ttoffset + len(self.NotST33FileList) + 2
        
        pass          

    def form_combine_result_excel(self, workbook):
        worksheet = workbook.add_sheet('combine', cell_overwrite_ok=True)
        ttoffset = 0
        worksheet.col(0).width =  256 * 100
        
        ttstr = "***CAL Folder overlopped when combine***"
        worksheet.write(ttoffset, 0, ttstr, self.title_style)
        
        ttoffset = ttoffset + 1
        for chipidstr in set(self.olpWhenCpyByChipID):
            worksheet.write(ttoffset, 0, chipidstr, self.nordata_style)
            ttoffset = ttoffset + 1

    def time_to_int(self, time_str):#XXXX-XX-XX XX:XX:XX
        reg = "(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})" #a real rid
        matchit = re.search(reg, time_str)
        if matchit:
            bigstr = '%s%s%s%s%s%s' %(matchit.group(1),matchit.group(2),matchit.group(3),matchit.group(4),matchit.group(5),matchit.group(6))
            #print ("Castle see: %s" %(bigstr))
            return int(bigstr)
        return 0
    
    def check_ref_cal_files(self):
        #check refcalibrate files
        
        refCalFiles = []
        #generate refCalFiles
        for filename in self.DUALCalFileList:
            refCalFiles.append(filename)

        #get all ref node dir
        for path in os.listdir(self.config_ini_data['ref_calibrat_dir']):
            self.ref_path_list.append(path)
        
        for tpath in self.ref_path_list:
                        
            refCalFilesFull = set()          
            current_refcalfile = set()
           
            for sub_dir in refCalFiles:
                refCalFilesFull.add(join(self.config_ini_data['ref_calibrat_dir'], tpath, sub_dir))
            
            for parent, dirnames, filenames in os.walk(join(self.config_ini_data['ref_calibrat_dir'], tpath)):
                for filename in filenames:
                    #print "SEE REF CAL files-->" + join(parent,filename) + "\n"
                    current_refcalfile.add(join(parent,filename))
                    
            for iii in current_refcalfile:
                print iii;
            for iii in refCalFilesFull:
                print iii;
                
            if(current_refcalfile >= refCalFilesFull):#is child set?
                print join(self.config_ini_data['ref_calibrat_dir'], tpath) + ' Check OK!'
                pass
            else:
                print join(self.config_ini_data['ref_calibrat_dir'], tpath) + ' Check Error!'
                raise RuntimeError("Error Files in " + join(self.config_ini_data['ref_calibrat_dir'], tpath))
                #return False
        
        return True
              
              
    def read_from_config_ini(self):
        isexist = os.path.isfile('config_3g.ini') 
        if(isexist):
            print "config_3g.ini existed."
        else:
            iniConfigHd = open("config_3g.ini",'w')
            print "create config_3g.ini by default.\n"
            iniConfigHd.write(";Generated time:" +time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) + '\n')
            iniConfigHd.writelines(Application.default_config_ini)
            iniConfigHd.close()
            
        config = cparser.ConfigParser()
        config.read("config_3g.ini")
        for section in config.sections():
            print "In section [%s]" % section
            for (key, value) in config.items(section):
                print "Key '%s' has value '%s'" % (key, value)
                self.config_ini_data[key] = value
                
    def save_to_config_ini(self):
        print "save_to_config_ini"
        config = cparser.ConfigParser()
        config.read("config_3g.ini")

        config.set('UI setting', 'process_folder', self.contents.get())
        config.set('UI setting', 'calibrat_folder', self.contentscal.get())
        config.set('UI setting', 'imei_range_head', self.contentshead.get())
        config.set('UI setting', 'imei_range_tail', self.contentstail.get())
        
        config.write(open("config_3g.ini", "w"))         
        self.lb_title["text"] = "Save OK!"
        
    def get_imei_x_bit(self, imei):
        imei_int_0 = int(imei[0])
        imei_int_1 = int(imei[1]) * 2
        imei_int_2 = int(imei[2])
        imei_int_3 = int(imei[3]) * 2
        imei_int_4 = int(imei[4])
        imei_int_5 = int(imei[5]) * 2
        imei_int_6 = int(imei[6])
        imei_int_7 = int(imei[7]) * 2
        imei_int_8 = int(imei[8])
        imei_int_9 = int(imei[9]) * 2
        imei_int_10 = int(imei[10])
        imei_int_11 = int(imei[11]) * 2
        imei_int_12 = int(imei[12])
        imei_int_13 = int(imei[13]) * 2
    
        imei_pro =  imei_int_0 + (imei_int_1/10) + (imei_int_1%10) \
                    + imei_int_2 + (imei_int_3/10) + (imei_int_3%10) \
                    + imei_int_4 + (imei_int_5/10) + (imei_int_5%10) \
                    + imei_int_6 + (imei_int_7/10) + (imei_int_7%10) \
                    + imei_int_8 + (imei_int_9/10) + (imei_int_9%10) \
                    + imei_int_10 + (imei_int_11/10) + (imei_int_11%10) \
                    + imei_int_12 + (imei_int_13/10) + (imei_int_13%10)

        return (10 - imei_pro % 10) % 10

    def try_to_close_xls_program(self):
        
        xls_program = ['et.exe', 'EXCEL.EXE']
        
        cmd_out = os.popen('tasklist')  
        cmd_out_txt = cmd_out.read()  
        cmd_out.close() 
        
        for prog in xls_program:
            nPos = 0
            try:     
                nPos = cmd_out_txt.index(prog)
            except Exception as e:
                pass
            else:
                pass
            if (nPos != 0):
                print 'GET %d for Close process %s' %(nPos, prog)
                os.system('taskkill /f /im ' + prog)

                
    def cpy_cal_files_to_cust_folder(self):
        
        the_target_all_cal = self.config_ini_data['cust_cal_folder']
        the_source_cal_mass = self.config_ini_data['process_folder']
        print 'cpy while search ' + the_source_cal_mass
        if(not os.path.isdir(the_target_all_cal)):
            os.makedirs(the_target_all_cal)
            
        if(os.path.isdir(the_target_all_cal)):
            #os.mkdir(the_target_all_cal)
            for parent, dirnames, filenames in os.walk(the_source_cal_mass):
                for dirdir in dirnames:
                    #print '-->' + dirdir
                    p = re.compile("([0-9A-Fa-f]{32})")
                    matchit = p.match(dirdir)
                    if matchit:
                        #print 'copying ' + dirdir
                        self.lb_title["text"] = 'cpying ' + dirdir
                        real_dir = dirdir
                        real_deep = parent.split('\\')
                        while(os.path.isdir(join(the_target_all_cal, real_dir))):
                            #real_dir = join(real_dir + '.tree')
                            #print 'GET olp cpy when combine: ' + dirdir
                            self.olpWhenCpyByChipID.append(dirdir)
                            real_dir = real_dir + '.' + real_deep[len(real_deep)-2]
                        #print 'Target dir: ' + real_dir
                        shutil.copytree(join(parent, dirdir), join(the_target_all_cal, real_dir))            
        else:
            print 'Create ' + the_target_all_cal + 'failed!'
            
    def is_imei_in_range(self, in_imei):
        for pair in self.imei_range_arry:
            if(in_imei>=((pair[0])*10) and in_imei<=((pair[1])*10)+9):
                #print 'imei in range %d' %(in_imei)
                return True
        #print 'imei not in range %d' %(in_imei)
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
        self.DUALCalFileList = ["MP0BA001", "MP0BB001", "ST33A004", "ST33B004"]
        self.QUADCalFileList = ["MT09_002", "MT06_002", "MT0O_002", "MT0L_002"]
        
        #IMEIAndChipIDPair = []#save the pair for IMEI and ChipID
        
        self.lallCalNumInINI_set = set()
        
        self.allCalNumInCal = set()
        self.allCalNumInINI = set()
        self.mixCalNum = ()
        self.list_ini_files = []#save all the WriteIMEI*.ini files
        
        self.imei_range_head = 0
        self.imei_range_tail = 0
        
        self.time_range_head = 0
        self.time_range_tail = 0
        
        self.resultOfCompFile = 0
        
        self.totalView = []
        
        self.version_info = "imei_cal_match_it version " + current_version
        self.a_null_chip_id = "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"
        
        self.overlaped_imei = [] #different imei use same chipid with cal
        
        self.ws_st33_file_number = 0
        self.ws_not_st33_file_number = 0
        self.NotST33FileList = []
        
        self.imei_with_time_dic = dict()
        self.config_ini_data = dict()
        
        self.read_from_config_ini()
        
        self.ref_path_list = []
        
        self.olpWhenCpyByChipID = []
        
        self.imei_range_arry = []
        
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()
        
        self.init_font_style()
        
    @classmethod
    def askt(cls, event=None):
        tkMessageBox.showwarning('Error', 'Error:No WriteIMEI.ini!')
        
    @classmethod
    def save_error(cls, event=None):
        tkMessageBox.showwarning('Error', Application.xlsioException)
    
    @classmethod
    def time_range_error(cls, event=None):
        tkMessageBox.showwarning('Error', 'time range error!')        
        
    @classmethod
    def ref_cal_error(cls, event=None):
        tkMessageBox.showwarning('Error', Application.refFileException)        
    
    @classmethod
    def process_folder_error(cls, event=None):
        tkMessageBox.showwarning('Error', 'no process_folder')        
        
if __name__=="__main__":

    root = Tk()
    root.title("IMEI CHECK") 
    #lock the size
    root.minsize(380,178)
    root.maxsize(380,178)
    
    root.bind('<<Ask>>', Application.askt)
    root.bind('<<XLS_ERROR>>', Application.save_error)
    root.bind('<<TIMERANGE_ERROR>>', Application.time_range_error)
    root.bind('<<REFCALIBRAT_ERROR>>', Application.ref_cal_error)
    root.bind('<<PROCESS_DIR_ERROR>>', Application.process_folder_error)
    
    app = Application(master=root)
    app.mainloop()

