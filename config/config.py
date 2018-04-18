# Version 1.0
# Author: Chih-Chen Kao

import telnetlib
import sys
import re
import time


# list of default variables

debug_flag = False

default_port = 23
default_connection_timeout = 10
default_read_timeout = 2

expected = b"Password"

default_password = "cisco"


default_twolevel_enable = b"enable"
default_twolevel_password = "2017@Tpn"


default_config_cmd = b"config terminal"

default_change_hostname_cmd = "hostname {}\n"

default_inerface_selection_cmd = b"interface vlan 1"
default_change_ip_cmd = "ip address {} 255.255.255.0\n"


default_copy_cmd = b"copy run start"

default_exit_cmd = b"exit"


default_pause_timer = 2
default_pause_timer_for_ip_changes = 90

# regex

config_regex = r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+(PASS|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+(PASS|Taipei_Lan_SW_\S+)[ \t]*"
comment_regex = r"[ \t]*#[ \t]*(\S.*)[ \t]*$"

# ---- Main Logic Below  ---

print("[INFO] : Read Configurations ... ")
records = []
with open("input.txt") as input_file:

    counter = 0

    for line in input_file:
        counter += 1

        if line == "\n":
            print("[INFO] : Newline encountered")
            continue

        config_match = re.match(config_regex, line)

        if config_match is None:
            comment_match = re.match(comment_regex, line)

            if comment_match is None:
                print("[ERROR] : Illegal input at Line: " + str(counter))
                exit(-1)

            print(comment_match)
            print("COMMENT: [" + comment_match[1]+ "]")
            continue


        # print(config_match)

        print("ORIGINAL IP: [" + config_match[1] + "]")
        print("NEW IP: [" + config_match[2] + "]")
        print("NEW HOSTNAME: [" + config_match[3] + "]\n")


        if config_match[1] == "PASS" and config_match[2] == "PASS":
            print("[INFO] : PASS ALL...  Nothing to do .... ")
            continue


        records.append([config_match[1], config_match[2], config_match[3]])

        # connect to switch via telnet


print("[INFO] : Configuration constructed !! ")

if debug_flag:
    print(records)

current_pause_timer = default_pause_timer

for record in records:

    # print(record)

    print("[INFO] : Connecting with pause period set to {} ....".format(current_pause_timer))
    time.sleep(current_pause_timer)

    try:

        host = record[0]
        with telnetlib.Telnet(host.rstrip(), default_port, default_connection_timeout) as tel:
            

            if debug_flag:
                tel.set_debuglevel(1)

            try:
                data = tel.read_until(expected, default_read_timeout)

                print("[INFO] : READ DATA - 1 : " + data.decode('ascii'))

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
            tel.write(default_config_cmd + b"\n")


            # hostname must go first !!!
            if record[2] != "PASS":
                tel.write(default_change_hostname_cmd.format(record[2]).encode('ascii'))
                current_pause_timer = default_pause_timer

                #print(tel.read_all().decode('ascii'))


            if record[1] != "PASS":

                tel.write(default_inerface_selection_cmd + b"\n")       # config-if

                try:
                    print(tel.read_until(b"config-if", default_read_timeout).decode('ascii'))
                except:
                    e = sys.exc_info()[0]
                    print(e)

                tel.write(default_change_ip_cmd.format(record[1]).encode('ascii'))

                try:
                    print(tel.read_until(b"config-if", default_read_timeout).decode('ascii'))
                    tel.write(default_exit_cmd + b"\n") # exit config-if
                    tel.write(default_exit_cmd + b"\n") # exit config
                    tel.write(default_exit_cmd + b"\n") # exit

                    tel.close()


                    #Prolong the pause period since we have changed the IP 
                    print("[INFO] : Prolong the pause period since we have changed the IP")
                    current_pause_timer = default_pause_timer_for_ip_changes

                    continue

                except:
                    e = sys.exc_info()[0]
                    print(e)

                    tel.close()
                    continue


            tel.write(default_exit_cmd + b"\n") # exit config

#            tel.write(default_copy_cmd + b"\n")
#            tel.write(b"\r\n\r\n")

            tel.write(default_exit_cmd + b"\n") # exit


            # debug
            print("[DEBUG] : \n --- \n{}\n --- \n".format(tel.read_all().decode('ascii')))


    except KeyboardInterrupt:
        print("[INFO] : Stop !")
        break

    except:
        print("[ERROR] : Error while connecting !!!")
        e = sys.exc_info()[0]
        print(e)
        continue

        



        



