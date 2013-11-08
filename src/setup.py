# setup.py

from distutils.core import setup
import py2exe

includes = ["encodings", "encodings.*"]

options = {"py2exe":
            {"compressed"   : 1,
             "optimize"     : 2,
             #"ascii"       : 1,
             "includes"     : includes,
             "dll_excludes" : None,#["MSVCR71.dll"]
             #"bundle_files": 1
            }
           }

setup(options = options,
      description = "DualTransServer",
      name = "DualTransServer",
      zipfile = None,  
      console = [{"script": "imei_cal_match_it_50_gui.pyw", "icon_resources": [(1, "Scanners.ico")]}]  
      )

#setup(console=['DualTransServer.py'])


#run >>python setup.py py2exe