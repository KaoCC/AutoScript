

import sys
import click
import requests
import threading
import shutil
import os



def download_handler(url, start, end, filename, part):

    segment_file = filename + ".part" + str(part)

    try:
        previous_download = os.path.getsize(segment_file)
        start += previous_download
    except:
        print("MISSING PART")

    print("file: {} START: {}, END: {}".format(segment_file, start, end))

    if start >= end:
        print("Already exist")
        return



    headers = {'Range': 'bytes={}-{}'.format(start, end)}
    r = requests.get(url, headers = headers, stream = True)
    print("Download size:{}".format(len(r.content)))
    print(r.headers)
    print(r.status_code)

    if r.status_code != 206:
        print("Error !!!!")
        return

    with open(segment_file, "ab") as download_file:
        for chunk in r.iter_content(chunk_size = 128):
            download_file.write(chunk)




def main(url):
    r = requests.head(url)
    if r.status_code != 200:
        print("Recieved Error Code: " + r.status_code)
        return

    file_name = url.split('/')[-1]

    print(r.headers)

    # test
    if r.headers['Accept-Ranges'] is "none":
        return
    else:
        print(r.headers['Accept-Ranges'])

    try:
        file_size = int(r.headers['content-length'])

    except:
        print("Invalid URL")
        return


    print("File Name: {}, Total file size: {}".format(file_name, file_size))

    n = 7
    segment_size = int(file_size / n)

    print("seg size: {}".format(segment_size))

    if file_size % n != 0:
        print("REM: {}".format(file_size % n))
        n += 1
    

    threads = []

    for i in range(n):
        start = segment_size * i
        effective_size = min(segment_size, file_size - start)
        end = start + effective_size - 1
        print("Download part {}, start: {}, end : {}".format(i, start, end))
        download_handler(url, start, end, file_name, i)

        #download_thread = threading.Thread(target = download_handler, kwargs={'start': start, 'end': end, 'url': url, 'filename': file_name, 'part' : i})
        #threads.append(download_thread)
        #download_thread.setDaemon(True)
        #download_thread.start()

    for tmp_thread in threads:
        tmp_thread.join()


    # merge files
    tmp_files = []
    for i in range(n):
        tmp_files.append(file_name + ".part" + str(i))

    with open(file_name, "wb") as fout:
        for tmp_file in tmp_files:
            with open(tmp_file, "rb") as fin : fout.write(fin.read())
    
    



if __name__ == "__main__":
    try:

        main("http://fileadmin.cs.lth.se/graphics/research/papers/2016/rayacc/rayacc.pdf")
        #main("http://williampatino.com/2015/wp-content/uploads/2016/12/William_Patino_Photography_NewZealand_Norwest_Lakes-copy.jpg")
        #main("http://127.0.0.1:8000/chih-chen-kao_cv_EU_3.pdf")
        #main("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Stadtbild_M%C3%BCnchen.jpg/640px-Stadtbild_M%C3%BCnchen.jpg")

    except:
        print(sys.exc_info()[0])
        import traceback
        print(traceback.format_exc())

    


