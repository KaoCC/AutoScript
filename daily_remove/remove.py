
__author__ = "Chih-Chen Kao"
__copyright__ = "Copyright (C) 2018, Chih-Chen Kao"
__license__ = "GPL"


import sys
from apscheduler.schedulers.blocking import BlockingScheduler
import os
import time
import zipfile
import shutil

base_dir = os.getcwd()

tmp_dir = os.path.join(base_dir, "tmp_photos")
photo_dir = os.path.join(base_dir, "subdir")


def check_photo():
    if not os.path.exists(photo_dir):
        raise FileNotFoundError("Photo dir : {} not found ... ".format(photo_dir))
    else:
        print("Photo dir : {} ... ".format(photo_dir))
    
def get_all_file_paths(directory):
    file_paths = []
    for root, subdirs, files in os.walk(directory):
        for filename in files:
            filepath = os.path.relpath(os.path.join(root, filename), os.path.join(directory, '..'))
            file_paths.append(filepath)

    return file_paths

def create_tmp_dir():
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
        print("Directory " , tmp_dir ,  " Created ")
    else:    
        print("Directory " , tmp_dir ,  " already exists")

def archive_photos():
    photo_paths = get_all_file_paths(photo_dir)
    archive_name = "photos_" + time.strftime("%Y%m%d-%H%M%S") + ".zip"

    if len(photo_paths) > 0:
        with zipfile.ZipFile(archive_name,'w') as zip_ref:
            for file in photo_paths:
                print("Archiving file: {} ... ".format(file))
                zip_ref.write(file)
        
        print("Moving the archive ... ")
        shutil.move(archive_name, tmp_dir + '/' + archive_name)
    else:
        print("No photos in the dir ... ")
    


def purge_all_photos(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path): 
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)


# scheduled
def remove_photos():
    print("Start scheduled task ... {} ".format(time.strftime("%Y/%m/%d - %H:%M:%S")))

    print("Archiving Photos ... ")
    archive_photos()
    
    print("Removing photos ...")
    purge_all_photos(photo_dir)

    print("Done !!! ")

    
    


sched = BlockingScheduler()
sched.add_job(remove_photos, 'cron', day_of_week = 'mon-fri', hour = 6)

sched.add_job(remove_photos, 'interval', seconds = 10)



def main():

    print("Dirs: {} , {}".format(photo_dir, tmp_dir))

    print("Checking Photo folders")
    check_photo()

    print("Create tmp folders")
    create_tmp_dir()

    print("Starting scheduler to remove photos")
    sched.start()


if __name__ == "__main__":

    try:
        main()

    except:
        print(sys.exc_info()[0])
        import traceback
        print(traceback.format_exc())
    finally:
        print("Shutting down ... ")
        sched.shutdown()
        print("Press Enter to continue ... ") 
        input()
