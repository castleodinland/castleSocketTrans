from os.path import walk, join, normpath, isdir, isfile, abspath
import sys
import re
import copy

allCalFile = []#with file name
allFullCalFileName = []#with full path and file name
lallCalNumInCal = []#set of cal files
lallCalNumInINI = []#set of imei in WriteIMEI.ini
lallRidNumInINI = []#set of rid in WriteIMEI.ini

lallCalNumInINI_set = set()

allCalNumInCal = set()
allCalNumInINI = set()
mixCalNum = ()
list_ini_files = []#save all the WriteIMEI*.ini files

imei_range_head = 0
imei_range_tail = 0

def mydir(arg, dirname, names):
    file = [normpath(tfile) for tfile in names]
    fullfilename = [abspath(join(dirname,tfile)) for tfile in names]
    #copy it, $file and $fullfilename are one-one correspondence
    for i in range(0,len(file)):
        if isfile(fullfilename[i]):#only save files
            #save WriteIMEI*.ini files
            p = re.compile("WriteIMEI.*\.ini")
            matchit = p.match(file[i])
            if matchit:
                #print matchit.group()
                list_ini_files.append(fullfilename[i])
                continue
     
        if isdir(fullfilename[i]):#only save path
            #save cal files's RID
            p = re.compile("[0-9A-Fa-f]{32}")
            matchit = p.match(fullfilename[i][-32:])
            if matchit:
                lallCalNumInCal.append(fullfilename[i][-32:])# save RID 
                continue
            
            
            #and ignore other type of files
    
    #print "\n".join(list_ini_files)
    
if __name__=="__main__":
    print("imei_cal_match_it version v0.827Beta\n")
    print "[path imeiHead imeiTail]"
    if len(sys.argv) == 1:
        paramStr = raw_input("input the folder name to search:\n")

        p = re.compile(".* \d{14} \d{14}")
        matchit = p.match(paramStr)
        if matchit:
            #print matchit.group()
            path = paramStr.split()[0]
            imei_range_head = int(paramStr.split()[1])
            imei_range_tail = int(paramStr.split()[2])
            imei_range_head = imei_range_head * 10
            imei_range_tail = imei_range_tail * 10 + 9
            print("searching range: [%d, %d]\n" %(imei_range_head, imei_range_tail))
        else:
            print "parameter error!!!"
            print "[path imeiHead imeiTail]"
            INPUT_SOME = raw_input("Press any key to exit.\n")
            raise exit(0)
    elif len(sys.argv) == 4:
        path = sys.argv[1]
        p = re.compile("[\d{14}]")
        matchit = p.match(sys.argv[2])
        if matchit:
            imei_range_head = int(sys.argv[2][1:15])*10
        else:
            print "imei1 length error, need 14 numbers!!!"
            INPUT_SOME = raw_input("Press any key to exit.\n")
            raise exit(0)
        
        print ("para2: %s" %(sys.argv[3]))
        matchit = p.match(sys.argv[3])
        if matchit:
            imei_range_tail = int(sys.argv[3][1:15])*10 + 9
        else:
            print "imei2 length error, need 14 numbers!!!"
            INPUT_SOME = raw_input("Press any key to exit.\n")
            raise exit(0)
        print("searching range: [%d, %d]\n" %(imei_range_head, imei_range_tail))
    else:
        print "parameter error!!!"
        print "[path <imeiHead> <imeiTail>]"
        INPUT_SOME = raw_input("Press any key to exit.\n")
        raise exit(0)

    
    walk(path, mydir, 1)
    
    outResultFileHandle = open("result.txt",'w+')
    
    """
    check *.cal files imei inside and outside
    """
    outResultFileHandle.write("Check calibration files consistency\n")
 
    """
    Parse the imei from WriteIMEI*.ini
    """
    if len(list_ini_files)==0:
        print ("No WriteIMEI.ini found!\n exit\n")
        INPUT_SOME = raw_input("Press any key to exit.\n")
        raise exit(0)
    
    for iniFile in list_ini_files:
        iniFileHandle = open(iniFile,'r')

        while True:
            line = iniFileHandle.readline()
            if not line:
                break
            imei = "\[\d{15}\]" #a real imei
            matchit = re.search(imei, line)
            if matchit:
                lallCalNumInINI.append(matchit.group()[1:16])
                
            rid = "rid=[0-9A-Fa-f]{32}" #a real rid
            matchit = re.search(rid, line)
            if matchit:
                lallRidNumInINI.append(matchit.group()[4:36])     
        iniFileHandle.close()
        
    """
    save the two lists in set and get the intersection 
    """        
    allCalNumInCal = set(lallCalNumInCal)
    allCalNumInINI = set(lallRidNumInINI)
    
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
    
    lallCalNumInINI_set = set(lallCalNumInINI)
    for cnini in lallCalNumInINI_set:
        reImeiNo = int(cnini[0:16])
        if reImeiNo < imei_range_head or reImeiNo > imei_range_tail:
            outResultFileHandle.write("Out of range imei: %s\n" %(cnini))
            countRange += 1
    
    outResultFileHandle.write("\ntotally %d items,and %d out of range.\n" %(len(lallCalNumInINI_set), countRange))
    outResultFileHandle.write("=============================================================================================================\n\n")
    
    outResultFileHandle.write("END\n\n\n")    
    
    print("Done!\n")
    
    outResultFileHandle.close()
    
    INPUT_SOME = raw_input("Press ENTER key to exit.")

