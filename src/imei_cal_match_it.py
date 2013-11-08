from os.path import walk, join, normpath, isdir, isfile, abspath
import sys
import re
import copy

allCalFile = []#with file name
allFullCalFileName = []#with full path and file name
lallCalNumInCal = []#set of cal files
lallCalNumInINI = []#set of imei in WriteIMEI.ini
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
            
            #save *.cal files
            p = re.compile("\d{15}.cal")
            matchit = p.match(file[i])
            if matchit:
                allCalFile.append(file[i])
                lallCalNumInCal.append(file[i][0:15])
        
                allFullCalFileName.append(fullfilename[i]) 
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
            print("searching range: [%d, %d]\n" %(imei_range_head, imei_range_tail))
        else:
            print "parameter error!!!"
            print "[path imeiHead imeiTail]"
            INPUT_SOME = raw_input("Press any key to exit.\n")
            raise exit(0)
    elif len(sys.argv) == 4:
        path = sys.argv[1]
        imei_range_head = int(sys.argv[2])
        imei_range_tail = int(sys.argv[3])
        print("searching range: [%d, %d]\n" %(imei_range_head, imei_range_tail))
    else:
        print "parameter error!!!"
        print "[path imeiHead imeiTail]"
        INPUT_SOME = raw_input("Press any key to exit.\n")
        raise exit(0)

    
    walk(path, mydir, 1)
    
    outResultFileHandle = open("result.txt",'w+')
    
    """
    check *.cal files imei inside and outside
    """
    outResultFileHandle.write("Check calibration files consistency\n")
    countConsis = 0
    for filename in allFullCalFileName:
        #print filename
        if isfile(filename):
            calFileHandle = open(filename, 'r')
            noField = False
            
            while True:
                lineData = calFileHandle.readline()
                if not lineData:
                    noField = True
                    break
                rexImei = "[iI][mM][eE][iI]=\d{15}"
                #print lineData
                matchit = re.search(rexImei, lineData)
                if matchit: #get the imei in cal
                    #getImei = str(matchit)
                    getImei = matchit.group()[5:20]
                    #print getImei
                    matchitAga = re.search(getImei, filename)
                    if matchitAga:
                        break
                    else:
                        outResultFileHandle.write("cal file not matched: %s==>%s\n" %(filename, getImei))
                        countConsis += 1
                        break
            if noField:
                outResultFileHandle.write("file %s has no IMEI field!\n" %(filename))
                countConsis += 1
            calFileHandle.close()
            
    outResultFileHandle.write("Totally %d items found\nCheck calibration files consistency END\n" %(countConsis))
    outResultFileHandle.write("=============================================================================================================\n\n")

    outResultFileHandle.write("Check calibration files range\n")
    
    countRange = 0
    for imeiNo in lallCalNumInCal:
        
        reImeiNo = int(imeiNo[0:14])
        if reImeiNo < imei_range_head or reImeiNo > imei_range_tail:
            outResultFileHandle.write("Out of range imei: %s.cal\n" %(imeiNo))
            countRange += 1
    
    outResultFileHandle.write("Totally %d items found\nCheck calibration files range END\n" %(countRange))
    outResultFileHandle.write("=============================================================================================================\n\n")
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
            if matchit: #get the reference
                lallCalNumInINI.append(matchit.group()[1:16])
                #print matchit.group()[1:16]
        iniFileHandle.close()
        
    """
    save the two lists in set and get the intersection 
    """        
    allCalNumInCal = set(lallCalNumInCal)
    allCalNumInINI = set(lallCalNumInINI)
    
    mixCalNum = allCalNumInCal&allCalNumInINI
    #print list(mixCalNum)
    
    outResultFileHandle.write("\ncalibration numbers in ini but not in cal:\n")
    outResultFileHandle.write("\n".join(list(allCalNumInINI-mixCalNum)))
    outResultFileHandle.write("\ntotally %d items found!\n" %(len(list(allCalNumInINI-mixCalNum))))
    outResultFileHandle.write("=============================================================================================================\n\n")
    
    outResultFileHandle.write("\ncalibration numbers in cal but not in ini:\n")
    outResultFileHandle.write("\n".join(list(allCalNumInCal-mixCalNum)))
    outResultFileHandle.write("\ntotally %d items found!\n" %(len(list(allCalNumInCal-mixCalNum))))
    
    outResultFileHandle.write("END\n\n\n")    
    
    print("Done!\n")
    
    outResultFileHandle.close()
    
    INPUT_SOME = raw_input("Press ENTER key to exit.")
