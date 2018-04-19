
# Author: Chih-Chen Kao

import telnetlib
import sys
import re
import time


debug_flag = False

default_port = 23
default_connection_timeout = 10
default_read_timeout = 2

expected = b"Password"

default_password = "cisco"


default_twolevel_enable = b"enable"
default_twolevel_password = "2017@Tpn"


default_config_cmd = b"config terminal"
default_copy_cmd = b"copy run start"
default_exit_cmd = b"exit"


default_pause_timer = 5


# regex
ip_regex = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"


print("[INFO] : Read IPs ... ")
records = []

with open("target.txt") as ip_file:

    counter = 0

    for line in ip_file:
        counter += 1

        if line == "\n":
            print("[INFO] : Newline encountered")
            continue

        ip_match = re.match(ip_regex, line)

        if ip_match is None:
            print("[ERROR] : Illegal input at Line: " + str(counter))
            exit(-1)


        print("TARGET IP: [" + ip_match[0] + "]")
        records.append(ip_match[0])

print("[INFO] : IP Records constructed !! ")

current_pause_timer = default_pause_timer

for record in records:
    print("[INFO] : Connecting to {} with pause period set to {} seconds ....".format(record, current_pause_timer))
    time.sleep(current_pause_timer)

    try:

        host = record
        with telnetlib.Telnet(host.rstrip(), default_port, default_connection_timeout) as tel:

            if debug_flag:
                tel.set_debuglevel(1)

            try:
                data = tel.read_until(expected, default_read_timeout)

                print("[INFO] : READ DATA - 1: " + data.decode('ascii'))

            except:
                print("[ERROR] : Error While reading Entry !!")
                e = sys.exc_info()[0]
                print(e)
                break

            tel.write(default_password.encode('ascii') + b"\n")

            tel.write(b"\r\n")

            tel.write(default_twolevel_enable + b"\n")
            
            try:
                data = tel.read_until(expected, default_read_timeout)

                print("[INFO] : READ DATA - 2 : " + data.decode('ascii'))

            except:
                print("[ERROR] : Error While reading level two entry !!")
                e = sys.exc_info()[0]
                print(e)
                break


            tel.write(default_twolevel_password.encode('ascii') + b"\n")


            tel.write(default_copy_cmd + b"\n")
            tel.write(b"\r\n\r\n")

            tel.write(default_exit_cmd + b"\n") # exit


            # debug
            print("[DEBUG] : \n --- \n{}\n --- \n".format(tel.read_all().decode('ascii')))


    except KeyboardInterrupt:
        print("[INFO] : Stop !")
        break

    except:
        print("[ERROR] : Error while connecting to {} !!!".format(record))
        e = sys.exc_info()[0]
        print(e)
        break