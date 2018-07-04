



try:
    import subprocess
    subprocess.call(['pip', 'install', "pandas", "xlrd", "openpyxl", "colorama"])
    print("Installing modules ... ")

except:
    import sys
    print(sys.exc_info()[0])
    import traceback
    print(traceback.format_exc())
    print("Press Enter to continue ...") 
    input()

