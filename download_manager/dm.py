

import sys
import click
import requests
import threading
import shutil
import os

import concurrent.futures
import time

tmp_dir_prefix = "tmp_"

def download_handler(url, start, end, filename, part):

    segment_file = os.path.join(tmp_dir_prefix + filename, filename + ".part" + str(part))

    try:
        previous_download = os.path.getsize(segment_file)
        start += previous_download
    except:
        # print("MISSING PART {}".format(part))
        pass

    #print("file: {} START: {}, END: {}".format(segment_file, start, end))

    if start > end:
        print("Already exist")
        return



    headers = {'Range': 'bytes={}-{}'.format(start, end), 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}
    with requests.get(url, headers = headers, stream = True) as r:
        #print("Download size:{}".format(len(r.content)))
        # debug
        #print(r.headers)
        #print(r.status_code)

        if r.status_code != 206 or int(r.headers['Content-Length']) != end - start + 1:
            print("Get Length: {}".format(r.headers['Content-Length']))
            print("Error !!!! File: {}".format(segment_file))
            return

        #print("Write to file [{}]".format(segment_file))
        with open(segment_file, "ab") as download_file:
            for chunk in r.iter_content(chunk_size = 256):
                download_file.write(chunk)




def main(url):

    print("URL: {}".format(url))

    with requests.head(url) as r:
        if r.status_code != 200:
            print("Recieved Error Code: " + str(r.status_code))
            return

        file_name = url.split('/')[-1]

        print(r.headers)

        # test
        if r.headers['Accept-Ranges'] is "none":
            print("Do not accept ranges")
            return
        else:
            print("Accept Ranges")

        try:
            file_size = int(r.headers['content-length'])
        except:
            print("Invalid URL")
            return


    print("File Name: {}, Total file size: {}".format(file_name, file_size))
    os.makedirs(tmp_dir_prefix + file_name, exist_ok = True)

    n = 20
    segment_size = int(file_size / n)

    print("seg size: {}".format(segment_size))

    if file_size % n != 0:
        print("REM: {}".format(file_size % n))



    start_time = time.time()
 
    with concurrent.futures.ThreadPoolExecutor() as executor:

        futures_of_downloads = []

        for i in range(n):
            start = segment_size * i
            effective_size = segment_size

            if i == n - 1:
                effective_size += (file_size % n)
            end = start + effective_size - 1
            print("Download part {}, start: {}, end : {}".format(i, start, end))
            # download_handler(url, start, end, file_name, i)

            futures_of_downloads.append(executor.submit(download_handler, url, start, end, file_name, i))

        for future in concurrent.futures.as_completed(futures_of_downloads):
            future.result()

    # merge files
    tmp_files = []
    for i in range(n):
        tmp_files.append(os.path.join(tmp_dir_prefix + file_name, file_name + ".part" + str(i)))

    # check file validation here ...
    # currently missing ..


    # merge into one
    print("Merge into the file: {}".format(file_name))
    with open(file_name, "wb") as fout:
        for tmp_file in tmp_files:
            with open(tmp_file, "rb") as fin : fout.write(fin.read())
    
    print("Time Elapsed: {}".format(time.time() - start_time))


if __name__ == "__main__":
    try:

        with open("hosts.txt") as input_file:

            for url in input_file:

                main(url.rstrip())
                #main("http://williampatino.com/2015/wp-content/uploads/2016/12/William_Patino_Photography_NewZealand_Norwest_Lakes-copy.jpg")
                #main("http://127.0.0.1:8000/chih-chen-kao_cv_EU_3.pdf")
                #main("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Stadtbild_M%C3%BCnchen.jpg/640px-Stadtbild_M%C3%BCnchen.jpg")
                # http://fileadmin.cs.lth.se/graphics/research/papers/2016/rayacc/rayacc.pdf

    except:
        print(sys.exc_info()[0])
        import traceback
        print(traceback.format_exc())

    


