
__author__ = "Chih-Chen Kao"
__copyright__ = "Copyright (C) 2018, Chih-Chen Kao"
__license__ = "GPL"


import sys
import zipfile

zip_file_path = "moj-bipartite_backup.zip"
default_target_path = "."

def main(target_path):

    try:

        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(target_path)

    except:
        print("Error while extracting the zip")
        e = sys.exc_info()[0]
        print(e)

    print("Extract zip file {} to path {} ".format(zip_file_path, target_path))



if __name__ == "__main__":

    target_path = default_target_path
    print(len(sys.argv))
    if (len(sys.argv) > 1):
        target_path = sys.argv[1]

    main(target_path)
