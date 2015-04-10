import Tkinter
from Tkinter import *
import tkFont
import tkFileDialog
import threading
import time
import os
import subprocess


class Application(Frame):
    
    def start_to_download(self):
        #self.dl_thread = thread.start_new_thread(self.run_jlink_check, ())
        self.dl_thread = threading.Thread(target=self.run_jlink_check)
        self.dl_thread.start()
    
    def run_jlink_check(self):
        
        self.brun["state"] = "disable"
        
        #hide or show the black windows
        st=subprocess.STARTUPINFO
        st.dwFlags=subprocess.STARTF_USESHOWWINDOW
        st.wShowWindow=subprocess.STARTF_USESHOWWINDOW #SW_HIDE
        
        if(not self.HexFile):
            self.returnAndReloaderWidgets('No HEX file!', 'red', 'active')
            return
        
        JLink_dir = ''
        nRFSto_dir = ''
        JLink_cmd = "JLink.exe"
        nRFSto_cmd = "nrfjprog.exe"
        JLink_dir_win7 = "C:\\Program Files (x86)\\SEGGER\\JLinkARM_V474b\\"
        JLink_dir_xp = "C:\\Program Files\\SEGGER\\JLinkARM_V474b\\"
        nRFSto_dir_win7 = "C:\\Program Files (x86)\\Nordic Semiconductor\\nrf51\\bin\\"
        nRFSto_dir_xp = "C:\\Program Files\\\Nordic Semiconductor\\\nrf51\\bin\\"
        
        if(os.path.isfile(JLink_dir_win7+JLink_cmd)):
            JLink_dir = JLink_dir_win7
        elif(os.path.isfile(JLink_dir_xp+JLink_cmd)):
            JLink_dir = JLink_dir_xp
        else:
            self.returnAndReloaderWidgets('NO JLink Driver!', 'red', 'active')
            return
        """
        if(os.path.isfile(nRFSto_dir_win7+nRFSto_cmd)):
            nRFSto_dir = nRFSto_dir_win7
        elif(os.path.isfile(nRFSto_dir_xp+nRFSto_cmd)):
            nRFSto_dir = nRFSto_dir_xp
        else:
            self.returnAndReloaderWidgets('NO nRF Stdio!', 'red', 'active')
            return       
        """
        
        self.llabel['text'] = 'Running...'
        self.llabel['bg'] = 'turquoise'
        
        #check JLink drive and cable
        self.ttext.insert(END, 'Start to Download...\r\n')
        self.ttext.insert(END, 'Searching JLink Drivers...\r\n')

        RUN_CMD = JLink_dir + JLink_cmd
        try:
            self.current_process = subprocess.Popen(RUN_CMD, 
                               shell=False, 
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.STDOUT,
                               env=None,
                               startupinfo=st)#st need show the windows, or will cause block.
            
            self.current_process.stdin.write('exit\r\n')
            self.current_process.wait()
        except Exception as e:
            self.returnAndReloaderWidgets('JLink_cmd error!', 'red', 'active')
            self.ttext.insert(END, "Exception: %r\n" % (e) )
            return
        
        self.JLinkSn = ''
        tstr = self.current_process.stdout.readline()
        
        while tstr:
            p = re.compile("S/N: ([0-9A-Fa-f]{9})")
            matchit = p.match(tstr)
            if matchit:
                self.JLinkSn = matchit.group(1)
                break
            #self.ttext.insert(INSERT, tstr)
            tstr = self.current_process.stdout.readline()
        
        if(self.JLinkSn):
            self.ttext.insert(END, 'Get JLink SN:' + self.JLinkSn + '\r\n')
        else:
            self.returnAndReloaderWidgets('NO JLink Driver!', 'red', 'active')
            return
        
        st.dwFlags=subprocess.STARTF_USESHOWWINDOW
        st.wShowWindow=subprocess.SW_HIDE
        
        #Erase the Flash
        self.ttext.insert(END, '----------------------------------------------\r\n')
        self.ttext.insert(END, 'Erase the Flash\r\n')
        Erase_cmd = nRFSto_dir + "nrfjprog.exe -s " + self.JLinkSn +" --eraseall"
        try:
            self.current_process = subprocess.Popen(Erase_cmd, 
                               shell=False, 
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.STDOUT,
                               env=None,
                               startupinfo=st)
            errcode = self.current_process.wait()
        except Exception as e:
            self.returnAndReloaderWidgets('Erase failed!', 'red', 'active')
            self.ttext.insert(END, "Exception: %r\n" % (e) )
            return
        
        tstr = self.current_process.stdout.readline()
        while tstr:
            self.ttext.insert(END, tstr)
            tstr = self.current_process.stdout.readline()
        self.ttext.see(END)
        
        if(errcode):
            self.returnAndReloaderWidgets('Erase failed!', 'red', 'active')
            return
        
        self.ttext.insert(END, '----------------------------------------------\r\n')
        self.ttext.insert(END, 'Begin to Program...\r\n')
        Program_cmd = nRFSto_dir + 'nrfjprog.exe -s ' + self.JLinkSn +' --program ' + self.HexFile +'  --reset'
        try:
            self.current_process = subprocess.Popen(Program_cmd, 
                               shell=False, 
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.STDOUT,
                               env=None,
                               startupinfo=st)
            errcode = self.current_process.wait()
        except Exception as e:
            self.returnAndReloaderWidgets('Download failed!', 'red', 'active')
            self.ttext.insert(END, "Exception: %r\n" % (e) )
            return
            
        if(errcode):
            self.returnAndReloaderWidgets('Download failed!', 'red', 'active')
            self.ttext.insert(END, "ErrorCode: %d\n" % (errcode) )
            return
        
        tstr = self.current_process.stdout.readline()
        while tstr:
            self.ttext.insert(END, tstr)
            tstr = self.current_process.stdout.readline()
        self.ttext.see(END)
        timetstr = time.ctime(time.time())
        self.ttext.insert(END, "%s\n" % (timetstr))
        self.ttext.insert(END, '----------------------------------------------\r\n')
        self.ttext.insert(END, '----------------------------------------------\r\n') 
        
        self.returnAndReloaderWidgets('P A S S', 'SpringGreen', 'active')
        
    def returnAndReloaderWidgets(self, label_text, label_bg, brun_state):
        self.llabel['text'] = label_text
        self.llabel['bg'] = label_bg
        self.brun["state"] = brun_state
        if(brun_state == 'active'):
            self.brun['fg'] = 'blue'
            
    def stopCurrentProcess(self):
        root.quit()
        pass
            
    def selectHexFile(self):
        self.HexFile = ''
        self.HexFile = tkFileDialog.askopenfilename(filetypes=[("HEX Files", ".hex")])
        if(self.HexFile):
            self.ttext.insert(END, 'Hex file: ' + self.HexFile + '\n')
        self.llabel['text'] = 'Ready'
        self.llabel['bg'] = 'turquoise'
        
    def createWidgets(self, main_frame):
        ftLabel = tkFont.Font(family = 'Verdana', size = 20, weight = tkFont.BOLD)
        ftText = tkFont.Font(family = 'Verdana', size = 10, weight = tkFont.BOLD)
        ftButton = tkFont.Font(family = 'Verdana', weight = tkFont.BOLD)
        
        self.llabel = Label(main_frame, text="Ready", width=20, bg="turquoise", font = ftLabel)
        self.llabel.grid(row=0, column=0, sticky=W+E) #columnspan=2
        
        self.bfile = Button(main_frame, text='HEX File', width=20, font = ftButton)
        self.bfile.grid(row=0, column=1, sticky=W+E+N+S)
        self.bfile["command"] = self.selectHexFile
        
        self.ttext = Text(main_frame, font = ftText)
        self.ttext.grid(row=1, column=0,columnspan=2, sticky=W+E)
        #self.ttext['background'] = 'Aquamarine'
        #self.ttext['state'] = 'disabled'
        #self.ttext.bind("<KeyPress>", lambda e : "break")
        
        #self.pbar = ttk.Progressbar(main_frame)
        #self.pbar.grid(row=2, column=0, columnspan=2, sticky=W+E+N+S)
        
        self.scrollbar = Scrollbar(main_frame)
        self.scrollbar.grid(row=1, column=1, sticky=N+S+E)
        self.scrollbar.config(command=self.ttext.yview)
        self.ttext['yscrollcommand'] = self.scrollbar.set
        
        self.brun = Button(main_frame, text='RUN', width=20, font = ftButton)
        self.brun.grid(row=3, column=0, sticky=W+E+N+S)
        self.bstop = Button(main_frame, text='STOP', width=20, font = ftButton)
        self.bstop.grid(row=3, column=1, sticky=W+E+N+S)
        
        self.brun['fg'] = 'blue'
        self.brun["command"] = self.start_to_download
        self.bstop['fg'] = 'red'
        self.bstop["command"] = self.stopCurrentProcess
        
        self.current_process = 0
        self.JLinkSn = ''
        self.HexFile = ''
        
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack(fill=BOTH, expand=1)
        main_frame = Frame(master)
        main_frame.pack(fill="y", expand=1)
        self.createWidgets(main_frame)
        self.dl_thread = 0

if __name__=="__main__":

    root = Tk()
    root.title("JLink Download nRF")
    
    #lock the root size
    root.resizable(False,False)
    
    app = Application(master=root)
    app.mainloop()
    