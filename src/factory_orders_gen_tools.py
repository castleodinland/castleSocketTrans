#!/usr/bin/python
#factory_orders_gen_tools.py

import os
from os.path import walk, join, normpath, isdir, isfile, abspath
import sys
import re
#import copy
import filecmp
import time
import thread
import ConfigParser as cparser
import shutil
import zipfile 

#DefaultButton = 0 -->Write
#DefaultButton = 1 -->Check

keys_need_check = ['SDS', 'METADB']

def error_and_pause():
    if(os.path.isdir('temp')):
        shutil.rmtree('temp')
    print "Error and not finished!"
    os.system('pause')

def zip_dir(dirname,zipfilename):
    filelist = []
    if os.path.isfile(dirname):
        filelist.append(dirname)
    else :
        for root, dirs, files in os.walk(dirname):
            for name in files:
                filelist.append(os.path.join(root, name))
         
    zf = zipfile.ZipFile(zipfilename, "w", zipfile.zlib.DEFLATED)
    for tar in filelist:
        arcname = tar[len(dirname):]
        #print arcname
        zf.write(tar,arcname)
    zf.close()

if __name__=="__main__":
    
    #check files and dirs
    if(not os.path.isfile('factory_config.ini') ):
        print "factory_config.ini not existed."
        error_and_pause()
        sys.exit(0)

    if(not os.path.isdir('WriteIMEI')):
        print "WriteIMEI not existed."
        error_and_pause()
        sys.exit(0)
    """
    if(not os.path.isfile('WriteIMEI\\WriteIMEI.ini') ):
        print "WriteIMEI.ini not existed for WriteIMEI."
        error_and_pause()
        sys.exit(0)
    """    
        
    if(os.path.isdir('WriteIMEI\\cal')):
        print 'has WriteIMEI\\cal'
        if len(os.listdir('WriteIMEI\\cal')) == 0:#no file under cal
            print 'no file in WriteIMEI\\cal'
            donotdel = open("WriteIMEI\\cal\\DONOTDEL",'w')
            donotdel.write('DO NOT DEL FOR ZIP\n')
            donotdel.close()
 
    config = cparser.ConfigParser()
    config.read("factory_config.ini")
    for section in config.sections():
        print "In section [%s]" % section
        config_ini_data = dict()
        sorted_key = []
        for (key, value) in config.items(section):
            print "Key '%s' has value '%s'" % (key, value)
            config_ini_data[key] = value
            sorted_key.append(key)
        
        for tKey in keys_need_check:
            if tKey not in sorted_key:
                print tKey + " not existed for parameter."
                error_and_pause()
                sys.exit(0)
        
        need_sds_str = ''
        if(config_ini_data['SDS'] == '0'):
            need_sds_str = '_NoSDS'
        zipfile_name_write = section + need_sds_str + '_WriteIMEI.zip'
        zipfile_name_check = section + need_sds_str + '_CheckIMEI.zip'
        
        #temp dir
        if(os.path.exists('temp')):
            shutil.rmtree('temp')
        os.mkdir('temp')
        
        print 'processing' + '[' + zipfile_name_write + ']'
        #write package
        current_dir = 'temp\\WriteIMEI\\'
        shutil.copytree('WriteIMEI', 'temp\\WriteIMEI')
        if(os.path.isfile(current_dir + "WriteIMEI.ini")):
            os.remove(current_dir + "WriteIMEI.ini")
        configg = cparser.ConfigParser()
        configg.read(current_dir + "WriteIMEI.ini")
        
        configg.add_section('IMEIRange')
        for key in sorted_key:
            configg.set('IMEIRange', key, config_ini_data[key])
        configg.set('IMEIRange', 'DefaultButton', '0')
        
        configg.write(open(current_dir + "WriteIMEI.ini", "w"))
        
        if(not os.path.isfile("database_dir\\"+config_ini_data['METADB'])):
            print "database_dir\\" + config_ini_data['METADB'] +' not existed!!!'
            error_and_pause()
            sys.exit(0)
        shutil.copyfile("database_dir\\"+config_ini_data['METADB'], current_dir + config_ini_data['METADB'])
        zip_dir('temp', zipfile_name_write)
        
        shutil.rmtree('temp\\WriteIMEI')
        
        #check package
        current_dir = 'temp\\WriteIMEI\\'
        shutil.copytree('WriteIMEI', 'temp\\WriteIMEI')
        if(os.path.isfile(current_dir + "WriteIMEI.ini")):
            os.remove(current_dir + "WriteIMEI.ini")
        configg = cparser.ConfigParser()
        configg.read(current_dir + "\\WriteIMEI.ini")
        
        configg.add_section('IMEIRange')
        for key in sorted_key:
            configg.set('IMEIRange', key, config_ini_data[key])
        configg.set('IMEIRange', 'DefaultButton', '1')
        
        configg.write(open(current_dir + "WriteIMEI.ini", "w"))
        
        if(not os.path.isfile("database_dir\\"+config_ini_data['METADB'])):
            print "database_dir\\" + config_ini_data['METADB'] +' not existed!!!'
            error_and_pause()
            sys.exit(0)
        shutil.copyfile("database_dir\\"+config_ini_data['METADB'], current_dir + config_ini_data['METADB'])
  
        #total zip them!!!
        zip_dir('temp', zipfile_name_check)
        print section + ' DONE!'
    
    if(os.path.isdir('temp')):
        shutil.rmtree('temp')
    print "ALL DONE!"
    os.system('pause')


