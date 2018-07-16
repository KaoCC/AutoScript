#!/usr/bin/env python3


__author__ = "Chih-Chen Kao"
__copyright__ = "Copyright (C) 2018, Chih-Chen Kao"
__license__ = "GPL"

import telnetlib
import sys
import re
import datetime

debug_flag = False

default_port = 23
default_connection_timeout = 5
default_read_timeout = 2

expected = b"Password"


# check this ...
default_password = "cisco"



data_regex = r"((All|\d+)\s+\w\w\w\w\.\w\w\w\w\.\w\w\w\w\s+(STATIC|DYNAMIC)\s+(CPU|\w+/\w+/?\w*))"

effective_regex = r"(\d+\s+(\w\w\w\w\.\w\w\w\w\.\w\w\w\w)\s+DYNAMIC\s+(\w+/\w+/?\w*))"

default_mac_query_cmd = b"sh mac address\n"


date_str = datetime.datetime.now().strftime("%Y%m%d%H")

with open("hostlist.txt") as host_data :

    for host in host_data:

        try:
            print("[INFO] : Connecting to {} with timeout set to {}".format(host.rstrip(), default_connection_timeout))
            with telnetlib.Telnet(host.rstrip(), default_port, default_connection_timeout) as tel:

                if debug_flag:
                    tel.set_debuglevel(1)


                try:
                    data = tel.read_until(expected, default_read_timeout)
                    print("Data Read ...\n")
                    print(data)
                    print("----\n")
                except:
                    print("[ERROR] : Error While reading !!")
                    e = sys.exc_info()[0]
                    print(e)
                    break

                tel.write(default_password.encode('ascii') + b"\n")

                tel.write(default_mac_query_cmd)

                # print(tel.read_all().decode('ascii'))


                read_data = str()
                while True:

                    try:
                        (idx, match, reads) = tel.expect([re.compile(b"--More--")], default_read_timeout)

                        read_data += str(reads.decode("ascii"))              

                        if idx != -1:
                            print("Got More...")
                            tel.write(b"\r\n")
                        else:
                            print("Last")
                            break
                    except EOFError:
                        print("[ERROR] : EOF Error")
                        break

                print("[INFO] : READ DATA Completed")
                # tel.write(b"\r\n")
                tel.write(b"exit\r\n")


                #print(read_data)

                # process the data


                print("[INFO] : Matching Regex from Raw Data")
                matching_list = re.findall(data_regex, read_data)
                #print(matching_list)

                print("[INFO] : Extra: Extract effective data from Raw Data")
                effective_list = re.findall(effective_regex, read_data)



                with open("raw_output_" + date_str + ".txt", "a", encoding="ascii") as output_file:
                    output_file.write(read_data)

                with open("raw_result_" + date_str + ".txt", "a", encoding="ascii") as raw_file:
                    raw_file.write(host.rstrip() + "\n")
                    for record_list in matching_list:
                        raw_file.write(record_list[0] + "\n")

                with open("final_result_" + date_str + ".txt", "a", encoding = "ascii") as result_file:
                    for result_list in effective_list:
                        result_str = result_list[1] + ',' + result_list[2] + ',' + host.rstrip()
                        result_file.write(result_str + "\n")




        except KeyboardInterrupt:
            print("Stop !")
            break
        except:
            print("[ERROR] : Error while connecting !!!")
            e = sys.exc_info()[0]
            print(e)
            continue


    

    












