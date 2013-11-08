from os.path import walk, join, normpath, isdir, isfile, abspath
import filecmp
import sys

DUALCalFileList = ["MT08_002", "MT07_002", "MT0N_002", "MT0M_002"]
QUADCalFileList = ["MT09_002", "MT06_002", "MT0O_002", "MT0L_002"]

if __name__=="__main__":
    #print("imei_cal_match_it version v1.1029Beta\n")
    #print "[path imeiHead imeiTail]"
    if len(sys.argv) != 2:
        raise sys.exit(0xff)
    
    compfilename = sys.argv[1]
    dmatch, dmismatch, derrors = filecmp.cmpfiles(compfilename+"\\Z\\NVRAM\\CALIBRAT", "REFCALIBRAT\\DUAL", DUALCalFileList, shallow=False)
    qmatch, qmismatch, qerrors = filecmp.cmpfiles(compfilename+"\\Z\\NVRAM\\CALIBRAT", "REFCALIBRAT\\QUAD", QUADCalFileList, shallow=False)
    
    if(len(derrors) == 0 and len(qerrors) == 0):
        #lIsQUADCalByChipID.append(fullfilename[i][-32:])
        raise sys.exit(0x10)
    elif(len(derrors) == 0 and len(qerrors) == 4):
        #lIsDUALCalByChipID.append(fullfilename[i][-32:])
        raise sys.exit(0x20)
    else:
        #lIsNULLBandCalByChipID.append(fullfilename[i][-32:])
        raise sys.exit(0xf0)
    
    