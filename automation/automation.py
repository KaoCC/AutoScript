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

cisco_expected = b"Password"
cisco_password = "cisco"



cisco_data_regex = r"((All|\d+)\s+\w\w\w\w\.\w\w\w\w\.\w\w\w\w\s+(STATIC|DYNAMIC)\s+(CPU|\w+/\w+/?\w*))"
cisco_effective_regex = r"(\d+\s+(\w\w\w\w\.\w\w\w\w\.\w\w\w\w)\s+DYNAMIC\s+(\w+/\w+/?(\w*)))"
cisco_mac_query_cmd = b"sh mac address\n"



other_expected_user = b"User name:"
other_expected_password = b"Password"
other_user = b"admin"
other_password = "2017@Tpn"

other_data_regex = r"((\d+)\s+\w+\s+(\w\w:\w\w:\w\w:\w\w:\w\w:\w\w)\s+Dynamic[ \t]*)"
other_mac_query_cmd = b"sh mac address-table all\n"



date_str = datetime.datetime.now().strftime("%Y%m%d%H")

host_input_regex = r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}),(\d{1,3})\s*"



def write_output(read_data, host_ip, up_port, data_regex, effective_regex, group_index_list):
    print("[INFO] : Matching Regex from Raw Data")
    matching_list = re.findall(data_regex, read_data)
    #print(matching_list)

    print("[INFO] : Extra: Extract effective data from Raw Data")
    effective_list = re.findall(effective_regex, read_data)

    if debug_flag:
        for eff in effective_list:
            print(eff)

    skip_count = 0

    with open("raw_output_" + date_str + ".txt", "a", encoding="ascii") as output_file:
        output_file.write(read_data)

    with open("raw_result_" + date_str + ".txt", "a", encoding="ascii") as raw_file:
        raw_file.write(host_ip + "\n")
        for record_list in matching_list:
            raw_file.write(record_list[0] + "\n")

    with open("final_result_" + date_str + ".txt", "a", encoding = "ascii") as result_file:
        for result_list in effective_list:

            if int(result_list[group_index_list[2]]) == up_port:
                # print("[INFO] : Skipping the record with specific UP Port: {}".format(result_list[1] + ',' + result_list[2]))
                skip_count += 1
                continue

            result_str = result_list[group_index_list[0]] + ',' + result_list[group_index_list[1]] + ',' + host_ip
            result_file.write(result_str + "\n")

    if skip_count > 0:
        print("[INFO] : Number of records being skipped: {}, Host IP: {}".format(skip_count, host_ip))



def read_records_from_other(tel):
    if debug_flag:
        tel.set_debuglevel(1)

    try:
        data = tel.read_until(other_expected_user, default_read_timeout)
        print("Data Read ...")
        print(data)


    except:
        print("[ERROR] : Error While reading user string !!")
        e = sys.exc_info()[0]
        print(e)
        return ""

    tel.write(other_user + b"\n")

    try:
        data = tel.read_until(other_expected_password, default_read_timeout)
        print("Data Read ...")
        print(data)


    except:
        print("[ERROR] : Error While reading password string!!")
        e = sys.exc_info()[0]
        print(e)
        return ""

    tel.write(other_password.encode('ascii') + b"\n")

    try:
        data = tel.read_until(b"Taipei_Lan_SW", default_read_timeout)
        print("Data Read ...")
        print(data)

    except:
        print("[ERROR] : Error While reading starting string !!")
        e = sys.exc_info()[0]
        print(e)
        return ""

    tel.write(other_mac_query_cmd)

    read_data = str()

    while True:

        try:
            (idx, match, reads) = tel.expect([re.compile(b"Taipei_Lan_SW")], default_read_timeout)

            read_data += str(reads.decode("ascii"))

            if idx != -1:
                print("Last")
                break

            else:
                raise ValueError("No match !")

        except:
            print("[ERROR] : ERROR While reading data !!")
            e = sys.exc_info()[0]
            print(e)
            return ""


    tel.write(b"exit\r\n")

    return read_data
    



def read_records_from_cisco(tel):
    if debug_flag:
        tel.set_debuglevel(1)

    try:
        data = tel.read_until(cisco_expected, default_read_timeout)
        print("Data Read ...")
        print(data)
    except:
        print("[ERROR] : Error While reading !!")
        e = sys.exc_info()[0]
        print(e)
        return ""

    tel.write(cisco_password.encode('ascii') + b"\n")
    tel.write(cisco_mac_query_cmd)

    # print(tel.read_all().decode('ascii'))

    read_data = str()
    while True:

        try:
            (idx, match, reads) = tel.expect([re.compile(b"--More--")], default_read_timeout)

            read_data += str(reads.decode("ascii"))              

            if idx != -1:
                print("Got More... ", end="")
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


    return read_data





def main(host_file_list, function_list, data_regex_list, effective_data_list, group_index_list):

    for i in range(0, len(host_file_list)):

        with open(host_file_list[i]) as host_data :

            for host_str in host_data:

                host_match = re.match(host_input_regex, host_str)

                if host_match is None:
                    raise ValueError("[ERROR] Invalid input found: [{}]. Correct Form: IP,UP_PORT".format(host_str))

                host_ip = host_match[1]
                up_port = int(host_match[2])

                print("[INFO] : INPUT: Host IP: {}, Up Port: {}".format(host_ip, up_port))

                try:
                    print("[INFO] : Connecting to {} with timeout set to {}".format(host_ip, default_connection_timeout))
                    with telnetlib.Telnet(host_ip, default_port, default_connection_timeout) as tel:

                        # read_data = read_records_from_cisco(tel)

                        read_data = function_list[i](tel)

                        # process the data

                        write_output(read_data, host_ip, up_port, data_regex_list[i], effective_data_list[i], group_index_list[i])


                        print("[INFO] : Process completed: [{}]\n".format(host_ip))



                except KeyboardInterrupt:
                    print("Stop !")
                    break
                except:
                    print("[ERROR] : Error while connecting {} !!!".format(host_str))
                    e = sys.exc_info()[0]
                    print(e)
                    continue


    

if __name__ == "__main__":
    print(__copyright__)
    main(["hostlist_a.txt", "hostlist_b.txt"], [read_records_from_cisco, read_records_from_other], [cisco_data_regex, other_data_regex], [cisco_effective_regex, other_data_regex], [[1, 2, 3], [2, 1, 1]])

    












