import sys
import os
import string


if __name__=="__main__":

    if (len(sys.argv) <3):
        print("FileToATCmdScript <PC side file path> <file path on target>")
        INPUT_SOME = raw_input("Press any key to exit.")
        raise exit(0)
    
    inputFileName = sys.argv[1]
    outputFileName = "ATCmdScript.txt" 
    targetOutFileName = sys.argv[2]
    
    inFileHandle = open(inputFileName,'rb')
    if (inFileHandle == None):
        print("Open Input file error!")
        raise exit(0)
    
    #delete script any way
    if os.path.isfile(outputFileName):
        os.remove(outputFileName);
    
    outFileHandle = open(outputFileName,'w')
    if (outFileHandle == None):
        print("Open/Create Output file error!")
        raise exit(0)
    
    #
    outFileHandle.write("AT+ESLP=0\nAT+ISP=RCAL:9\nAT+ISP=RCAL:9\nAT+ISP=RCAL:9\n")
    outFileHandle.write("AT+ISP=RCAL:9\nAT+ISP=RCAL:9\nAT+ESUO=3\n")
 
 
    nameList = list(targetOutFileName)
    #print(nameList)
    
    #print "\n".join(["00%X" %(n) for n in nameList])
    finalTargetOutfileName ="AT+EFSW=0, \""+"00" + "00".join([n.encode("hex") for n in nameList]) + "\"\n"
    outFileHandle.write(finalTargetOutfileName.upper())
    #print(finalTargetOutfileName)
        
    fileSize = os.path.getsize(inputFileName)
    print("filesize = %f" %(fileSize))
    
    #read file data and write to the script
    while True:
        words = inFileHandle.read(64)
        if not words:
            break
        writeLine = words.encode("hex")
        
        #print(writeLine)
        outFileHandle.write("AT+EFSW=2, 0, %d, \"%s\"\n" %(len(writeLine)/2, writeLine.upper()))
        
    outFileHandle.write("AT+EFSW=1\nAT+ESUO=4\n")
    
    outFileHandle.close()
    inFileHandle.close()
    
    print("ATCmdScript.txt created!\n")
    
    
    