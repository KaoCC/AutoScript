

import sys
import subprocess

try:
    subprocess.call(['pip', 'install', "pandas", "xlrd", "openpyxl"])
    print("Installing modules ... ")

except:
    print(sys.exc_info()[0])
    import traceback
    print(traceback.format_exc())
    print("Press Enter to continue ...") 
    input()

