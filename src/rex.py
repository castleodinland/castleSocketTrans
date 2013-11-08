import re
import os
from os.path import join, getsize, abspath

if __name__=="__main__":
    #rexWriteIMEI = "\bWriteIMEI\b\w*.ini"
    #rexWriteIMEI = "*.ini"
    """
    p = re.compile("\d{15}.cal")
    matchit = p.match("359094024029453.cal")
    if matchit:
        print matchit.group()
    """
    
    """
    all_the_file = []
    for root, dirs, files in os.walk("123456-98530"):
        print root, "consumes",
        print sum([getsize(join(root, name)) for name in files]),
        print "bytes in", len(files), "non-directory files"
        
        for fname in [abspath(join(root,name)) for name in files]:
            all_the_file.append(fname)
        
    print "\n".join(all_the_file)
    """
    theStr = "35909402402945 "
    p1 = ""
    p2 = ""
    p3 = ""
    p = re.compile("\d{14} ")
    matchit = p.match(theStr)
    if matchit:
        print matchit.group()
    else:
        print ("not match")
        
    
     
        