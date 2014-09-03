#!/usr/bin/python
#imei_cal_match_it_50_gui.pyw

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

the_first_lay_dir = False

IS_FOR_CASTLE_TST = True #False True

#release note:
#v1.1101Beta -->fix bug when checking band support
#v1.1105Beta -->add a new Entry to appoint Cal PATH
#v1.1111Beta -->add a Progressbar
#v1.1119Beta -->add overlap check for imei and chip id
#v1.1121Beta -->output excel as report, need install xlwt module first for your python
#v1.1200Beta -->fill the ENTRY for UI
class Application(Frame):
    xlsioException = 0
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
                    
                    self.sum_ws_st33_file_number(str(fullfilename[i]))
            if(dirname == self.contents.get()):
                #update bar 
                show_value = i*100/len(file)
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
    
        self.ws_st33_file_number = 0
        self.ws_not_st33_file_number = 0
        del self.NotST33FileList[:]
        
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
            #show the warning messagebox
            root.event_generate('<<Ask>>', when='tail')
            return
        
        #really begin to check
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
        
        #excel:::
        workbook = xlwt.Workbook()
        if (self.checkv.get() != 1):
            self.form_total_view_excel(workbook)
        self.form_result_excel(workbook)
        self.form_band_confirm_excel(workbook)
        self.form_comparison_excel(workbook)
        self.form_st33_check_excel(workbook)
        try:
            workbook.save('TotalView.xls')
        except Exception as e:
            print ("Workbook save exception: %s" % e)
            Application.xlsioException = str(e);
            root.event_generate('<<XLS_ERROR>>', when='tail')
            self.lb_title["text"] = "pls close opened xls file!"
        else:
            self.lb_title["text"] = "FINISHED!"
            self.pbar.config(value=120)
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
            self.contents.set("input work space path here...")
        else:
            self.contents.set("1307004-1008-t")
        # tell the entry widget to watch this variable
        self.entrythingy["textvariable"] = self.contents

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
        self.contentscal.set("\\Z\\NVRAM\\CALIBRAT")
        # tell the entry widget to watch this variable
        self.calpathentry["textvariable"] = self.contentscal   
       
        vcmd = (self.register(self.validate),'%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        #head
        self.imeihead = Entry(validate = 'key', justify = "left",width = 40)
        self.imeihead.pack(expand=YES, fill=BOTH)

        # here is the application variable
        self.contentshead = StringVar()
        # set it to some value
        if(IS_FOR_CASTLE_TST != True):
            self.contentshead.set("00000000000000")
        else:
            self.contentshead.set("35909402000003")
        self.imeihead["textvariable"] = self.contentshead
        
        #tail
        self.imeitail = Entry(validate = 'key', justify = "left",width = 40)
        self.imeitail.pack(expand=YES, fill=BOTH)

        # here is the application variable
        self.contentstail = StringVar()
        # set it to some value
        if(IS_FOR_CASTLE_TST != True):
            self.contentstail.set("00000000000008")
        else:
            self.contentstail.set("35909402000008")
        self.imeitail["textvariable"] = self.contentstail
        
        self.hi_there = Button(self, relief=RAISED, width = 15)
        self.hi_there["text"] = "RUN",
        self.hi_there["fg"] = "blue"
        self.hi_there["command"] = self.say_hi
        
        self.hi_there.pack({"side": "left"})
        
        self.QUIT = Button(self, relief=RAISED, width = 15)
        self.QUIT["text"] = "QUIT"
        self.QUIT["fg"] = "red"
        self.QUIT["command"] = self.quit

        self.QUIT.pack({"side": "left"})

        self.checkv = IntVar()
        self._checkbutton = Checkbutton(self, variable = self.checkv, text = "scatter", command = self.callCheckbutton)
        self._checkbutton.pack({"side": "right"})

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
        tlabel = ['IMEI', 'Chip ID', 'have cal', 'DUAL DFT', 'QUAD DFT', 'Is bad?', 'chipid olp', 'imei olp']
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
            worksheet.write(i+ttoffset, 6, e[6], self.get_data_style_for_xlwt(e[6]))   
            #imei overlap
            worksheet.write(i+ttoffset, 7, e[7], self.get_data_style_for_xlwt(e[7]))   
        ttoffset = ttoffset + len(self.totalView) + 2
        
        #abnormal data
        worksheet.write_merge(ttoffset, ttoffset, 0, 1, '********The Total View Summary:********', self.title_style)
        
        ttoffset = ttoffset + 2
        abnormal_pair,sub_abnormal_pair = self.hold_abnormal_pair_from()
        
        ttstr = "Total abnormal data: %d" %(len(abnormal_pair))
        worksheet.write_merge(ttoffset, ttoffset, 0, 1, ttstr, self.subtitle_style)
        
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
            worksheet.write(i+ttoffset, 6, e[6], self.get_data_style_for_xlwt(e[6]))   
            #imei overlap
            worksheet.write(i+ttoffset, 7, e[7], self.get_data_style_for_xlwt(e[7]))  
        ttoffset = ttoffset + len(abnormal_pair) + 1
        
        #sub-abnormal data
        ttstr = "Total sub-abnormal data: %d" %(len(sub_abnormal_pair))
        worksheet.write_merge(ttoffset, ttoffset, 0, 1, ttstr, self.subtitle_style)
        ttoffset = ttoffset + 1
       
        for i, e in zip(range(len(sub_abnormal_pair)), sub_abnormal_pair):
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
            worksheet.write(i+ttoffset, 6, e[6], self.get_data_style_for_xlwt(e[6]))   
            #imei overlap
            worksheet.write(i+ttoffset, 7, e[7], self.get_data_style_for_xlwt(e[7]))  
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
        
        self.version_info = "imei_cal_match_it version v1.1202Beta"
        self.a_null_chip_id = "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"
        
        self.overlaped_imei = [] #different imei use same chipid with cal
        
        self.ws_st33_file_number = 0
        self.ws_not_st33_file_number = 0
        self.NotST33FileList = []
        
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
        
if __name__=="__main__":
    root = Tk()
    root.title("IMEI CHECK") 
    #lock the size
    root.minsize(380,178)
    root.maxsize(380,178)
    root.bind('<<Ask>>', Application.askt)
    root.bind('<<XLS_ERROR>>', Application.save_error)
    
    app = Application(master=root)
    app.mainloop()

