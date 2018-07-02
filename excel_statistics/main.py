#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Copyright (C) 2018, Chih-Chen Kao

__author__ = "Chih-Chen Kao"
__copyright__ = "Copyright (C) 2018, Chih-Chen Kao"
__license__ = "GPL"

import re
import sys
import os

# configs & parameters

debug_flag = False


# KaoCC: change this to the actual location
default_target_file = r'target.xlsx'
default_sheet_name = "Sheet1"

# --- unused ---
# default_start_row_index = 3
# default_header_index = 0
# default_usecols = 21

default_case_non_na_count = 4
default_law_non_na_count = 3
default_usecols_case_list = [0, 7, 8, 12, 14, 16, 17]
default_case_name = ["編號", "弊端類型", "特殊貪瀆案件註記", "公務員姓名", "性別", "主管機關", "職務層級"]

default_usecols_law_list = [12, 17, 18, 19, 20]
default_law_name = ["公務員姓名", "職務層級", "貪污治罪條例", "刑法瀆職罪章", "其他"]

person_column_name = default_law_name[0]
level_column_name = default_law_name[1]

corruption_law_column_name = default_law_name[2]
criminal_law_column_name = default_law_name[3]
other_law_column_name = default_law_name[4]


corruption_law_regex = r"第([4-6]|1[1-5])\s*條(?:之\d{1})?(?:第(\d{1,2})\s*項)?(?:第(\d{1,2})\s*款)?"
criminal_law_regex = r"(?:刑法)?第([1-2]\d{2})\s*(?:條)?"
other_law_regex = r"第?(\d{3})\s*(?:條)?"



corruption_law_regex_inst = re.compile(corruption_law_regex)
criminal_law_regex_inst = re.compile(criminal_law_regex)
other_law_regex_inst = re.compile(other_law_regex)


law_regex_list = [corruption_law_regex_inst, criminal_law_regex_inst, other_law_regex_inst]

default_effective_offset = 0

# raw_df = pd.read_excel(default_target_file, sheet_name = default_sheet_name, header = None, usecols = default_usecols_case_list, names = default_case_name)




def sanity_check(target_df, header, check_index_list):
    for index in check_index_list:
        if target_df[header[index]].hasnans:
            print("[FATAL ERROR]: Sanity Check failed in {}".format(header[index]))

            error_index = 0
            for i in range(0, len(target_df[header[index]])):
                if pd.isna(target_df[header[index]][i]):
                    error_index = i
                    break

            raise ValueError("Data Cannot be NaN in {} at index {}".format(header[index], error_index))
        else:
            print("[INFO] Pass Sanity Check in {}".format(header[index]))


# ----------------------


def create_raw_df(target_file, input_sheet_name, usecols_case_list, case_name):
    raw_df = pd.read_excel(target_file, sheet_name = input_sheet_name, header = None, usecols = usecols_case_list, names = case_name)

    if debug_flag:
        print(raw_df.axes)

    return raw_df


def create_row_col_sets(row_file, col_file):

    row_set = set()
    col_set = set()

    with open(row_file, encoding = 'utf8') as row_label_file:
        for label in row_label_file:
            if debug_flag is True:
                print("original row label: [{}]".format(label.rstrip()))
            
            if label.strip() and label.strip(u"\ufeff").strip():
                row_set.add(label.strip().rstrip().strip(u"\ufeff"))

    with open(col_file, encoding = 'utf8') as col_label_file:
        for label in col_label_file:
            if debug_flag is True:
                print("original col label: [{}]".format(label.rstrip()))

            if label.strip() and label.strip(u"\ufeff").strip():
                col_set.add(label.strip().rstrip().strip(u"\ufeff"))


    return row_set, col_set


#------------------------
# test the format

def print_row_data(reference_df, col_name_list, row_index):
    print("\n ------ Row Data with index {} Print Out: ------".format(row_index))
    for i in range(0, len(col_name_list)):
        print(" | [{}]".format(reference_df[col_name_list[i]][row_index]))

    print("------ END ------ \n")





#-----------------------

def generate_complex_df(reference_df):

    complex_df = pd.DataFrame(reference_df, copy = True)
    complex_df.dropna(thresh = default_case_non_na_count, inplace = True)
    complex_df.fillna(method='ffill', inplace = True)
    complex_df.reset_index(drop = True, inplace = True)

    #print_row_data(reference_df, 11)
    #print_row_data(complex_df, 11)


    return complex_df


#------------------------
# For Case Recording


def calculate_case_records(reference_df):

    table = {}

    with open("type.txt", encoding = 'utf8') as type_file:
        for line in type_file:
            if debug_flag is True:
                print("[{}]".format(line.rstrip()))

            if line.strip() and line.strip(u"\ufeff").strip():
                table[line.strip().rstrip().strip(u"\ufeff")] = 0

    for row_index in range(default_effective_offset, reference_df.index.size):
        num = reference_df[default_case_name[0]][row_index]
        record = str(reference_df[default_case_name[1]][row_index])

        if record in table and str(num) != "nan":
            table[record] += 1
        else:
            if record != "nan" and str(num) == "nan":
                print("[WARNING]: Possible duplication found at index {} : {}".format(row_index, record) )
            elif record == "nan" and str(num) == "nan":
                print("[INFO]: Possibly belong to the prevoius case at index {}".format(row_index) )
            elif record not in table and record != "nan":
                print("[WARNING]: {} at index {} not found in the table !".format(record, row_index))
            else:
                print("[WARNING]: Data at index {} have not been recorded due to unknown reasons, please check manually".format(row_index))
                print_row_data(reference_df, default_case_name, row_index)



    if debug_flag:
        print(table)
        print(" --- total: {} --- ".format(sum(table.values())))

        print(" === Sorted Result ===")
        print(sorted(table.items(), key = lambda x: x[1]))

    case_record_df = pd.DataFrame(data = table, index = ["Count"])
    case_record_df = case_record_df.T

    case_record_df.sort_values(by=["Count"], inplace=True, ascending = False)

    return case_record_df




# --------
# For People

def calculate_people_records(reference_df):

    gender_table = {"男" : 0, "女" : 0}
    level_table = {1 : 0, 2 : 0, 3 : 0, 4 : 0, 5 : 0}


    for row_index in range(default_effective_offset, reference_df.index.size):

        try :
            num = reference_df[default_case_name[0]][row_index]
            name = str(reference_df[default_case_name[3]][row_index])
            gender = str(reference_df[default_case_name[4]][row_index])
            level = int(reference_df[default_case_name[6]][row_index])

            if str(num) != "nan" and level in level_table and gender in gender_table and name != "nan":
                # print("{}, {}, {}".format(row_index, str(name), int(level)))
                level_table[level] += 1
                gender_table[gender] += 1
            elif name == "nan" and str(reference_df[default_case_name[6]][row_index]) == "nan" and gender == "nan":
                print("[WARNING]: Possible invalid data or null at index {}, skipping ...".format(row_index))
            else:
                print("[WARNING]: People at index {} have not been recorded due to unknown reasons, please check manually".format(row_index))
                print_row_data(reference_df, default_case_name,row_index)
        except ValueError:
            print("[EXCEPTION]: People at index {} causes an exception, please check manually".format(row_index))
            print_row_data(reference_df, default_case_name, row_index)




    if debug_flag:

        print(" === People Result")
        print(level_table)
        print(gender_table)

        total_count = sum(level_table.values())
        print(" --- total: {} --- ".format(total_count))

        level_percentage = [0] * len(level_table)
        for (key, value) in level_table.items():
            level_percentage[key - 1] = value / total_count

        print(level_percentage)

    gender_record_df = pd.DataFrame(data = gender_table, index = ["Count"])
    gender_record_df = gender_record_df.T

    return gender_record_df
    




def create_output_dataform(row_file, col_file):

    row_labels = []
    col_labels = []

    with open(row_file, encoding = 'utf8') as row_label_file:
        for label in row_label_file:
            if debug_flag is True:
                print("row label read: [{}]".format(label.rstrip()))
            if label.strip() and label.strip(u"\ufeff").strip():
                row_labels.append(label.rstrip())

    with open(col_file, encoding = 'utf8') as col_label_file:
        for label in col_label_file:
            if debug_flag is True:
                print("col label read: [{}]".format(label.rstrip()))
            if label.strip() and label.strip(u"\ufeff").strip():
                col_labels.append(label.rstrip())

    # create df

    out_df = pd.DataFrame(index = row_labels, columns = col_labels)
    
    if debug_flag is True:
        print(out_df)

    return out_df
    

def generate_ratio_df(out_df):

    col_list = list(out_df)


    ratio_df = pd.DataFrame(data = out_df[col_list], copy = True )
    ratio_df = ratio_df.apply(lambda x: x / (x.sum() + 0.0000001), axis=1)

    return ratio_df



# KAOCC: add flag to determine which parts should be added
def append_statistic_cells(out_df):
    col_list = list(out_df)

    out_df.insert(0, "總計", out_df[col_list].sum(axis = 1))

    total = out_df["總計"].sum()
    out_df.insert(0, "比率", out_df[col_list].sum(axis = 1) / total)
    out_df_sum = pd.DataFrame(data = out_df[list(out_df)].sum())

    # print(out_df_sum)

    out_df_sum_row = out_df_sum.T

    # print(out_df_sum_row)

    out_df_sum_row = out_df_sum_row.reindex( columns = out_df.columns)
    out_df_sum_row = out_df_sum_row.rename(index = {0 : "總計"})

    # print(out_df_sum_row)

    out_df_percentage = pd.DataFrame(out_df_sum_row, copy = True)
    out_df_percentage = out_df_percentage.rename(index = {"總計" : "比率"})
    out_df_percentage = out_df_percentage / out_df_percentage.at["比率", "總計"]


    # print(out_df_percentage)
    # print(out_df_sum_row)
    
    out_df = out_df.append(out_df_sum_row,  verify_integrity  = True)
    out_df = out_df.append(out_df_percentage, verify_integrity  = True)

    # recover the total percentage
    out_df.at["比率", "比率"] = out_df.at["比率", "總計"]



    if debug_flag is True:
        print(out_df)

    return out_df


def row_col_analysis(reference_df, out_df, row_file, col_file, row_target_label, col_target_label, ratio_flag):

    row_set, col_set = create_row_col_sets(row_file, col_file)

    for row_index in range(default_effective_offset, reference_df.index.size):

        try:
            row_target = str(reference_df[row_target_label][row_index])
            col_target = str(int(reference_df[col_target_label][row_index]))


            if row_target != "nan" and col_target != "nan" and row_target in row_set and col_target in col_set:


                if str(out_df.at[row_target, col_target]) == "nan":
                    out_df.at[row_target, col_target] = 1
                else:
                    out_df.at[row_target, col_target] += 1

            else:
                print("Possible Error found at index {} with data: {}: {}, {}: {}".format(row_index, row_target_label, row_target, col_target_label, col_target))
                print_row_data(reference_df, default_case_name, row_index)

        except ValueError:
            print("[EXCEPTION]: Data at index {} causes an exception, please check manually".format(row_index))
            print_row_data(reference_df, default_case_name, row_index)


    if ratio_flag:
        ratio_df = generate_ratio_df(out_df)


    out_df = append_statistic_cells(out_df)


    if ratio_flag:
        return out_df, ratio_df
    else:
        return out_df


def partial_row_col_analysis(reference_df, out_df, row_file, col_file, row_target_label, col_target_label, partial_target_label, ratio_flag):

    row_set, col_set = create_row_col_sets(row_file, col_file)


    for row_index in range(default_effective_offset, reference_df.index.size):

        id_target = str(reference_df[partial_target_label][row_index])
        if id_target == "nan":
            if debug_flag:
                print("[INFO] Bypass empty case in partial analysis at index {}".format(row_index))

            continue

        try:

            row_target = str(reference_df[row_target_label][row_index])
            col_target = str(int(reference_df[col_target_label][row_index]))


            if row_target != "nan" and col_target != "nan" and id_target != "nan" and row_target in row_set and col_target in col_set:


                if str(out_df.at[row_target, col_target]) == "nan":
                    out_df.at[row_target, col_target] = 1
                else:
                    out_df.at[row_target, col_target] += 1

            else:
                print("Possible Error found at index {} with data: {}: {}, {}: {}".format(row_index, row_target_label, row_target, col_target_label, col_target))
                print_row_data(reference_df, default_case_name, row_index)

        except ValueError:
            print("[EXCEPTION]: Data at index {} causes an exception, please check manually".format(row_index))
            print_row_data(reference_df, default_case_name, row_index)



    if ratio_flag:
        ratio_df = generate_ratio_df(out_df)


    out_df = append_statistic_cells(out_df)


    if ratio_flag:
        return out_df, ratio_df
    else:
        return out_df
                

template_regex = r"1\.採購案件\(以下六小項擇一\)\s+([□■])a\.重大工程採購\(2\s*億元以上\)\s+([□■])b\.一般工程採購\(未達2\s*億元\)\s+([□■])c\.鉅額財物採購\(1\s*億元以上\)\s+([□■])d\.一般財物採購\(未達1\s*億元\)\s+([□■])e\.鉅額勞務採購\(2\s*千萬元以上\)\s+([□■])f\.一般勞務採購\(未達2\s*千萬元\)\s+([□■])2\.破壞國土\s+3\.補助款\(以下二小項擇一\)\s+([□■])a\.社福補助款\s+([□■])b\.其他補助款\s+([□■])4\.公款詐領\(事務費--差旅費或加班費、業務費\)\s+([□■])5\.替代役\s*"
template_regex_inst = re.compile(template_regex)

def parse_template_regex(template_string):

    result = re.match(template_regex_inst, template_string)

    if result is None:
        return -1


    groups = result.groups()


    for i in range(0, len(groups)):
        if groups[i] == '■':
            if i <= 5:
                return 1
            elif i == 6:
                return 2
            elif i == 7 or i == 8:
                return 3
            elif i == 9:
                return 4
            elif i == 10:
                return 5
            else:
                return -1  # error

    return 0


def extract_agency_info(agencies_regex_list, target_df):

    agency_column_name = default_case_name[5]

    insert_df = pd.DataFrame(data = target_df[agency_column_name])

    # print(insert_df)

    for row_index in range(default_effective_offset, target_df[agency_column_name].index.size):

        # print(target_df[row_index])

        error_flag = True
        for i in range(0, len(agencies_regex_list)):
            input_str = str(target_df[agency_column_name][row_index])
            found_flag = is_found_in(agencies_regex_list[i], input_str)

            if found_flag is True:
                if debug_flag is True:
                    print("Agency [{}] at index {} Found in {}".format(input_str, row_index, i))

                error_flag = False
                insert_df[agency_column_name][row_index] = (i + 1)

                break

        if error_flag is True:
            print("[ERROR]: Agency [{}] at index {} cannot be found in all the regex lists".format(str(target_df[agency_column_name][row_index]), row_index))
            insert_df[agency_column_name][row_index] = -1

    
    
    # print(insert_df)

    target_df["Agency"] = insert_df

    return target_df


def extract_special_case_info(target_df):

    special_case_column_name = default_case_name[2]

    insert_df = pd.DataFrame(data = target_df[special_case_column_name])

    for row_index in range(default_effective_offset, target_df[special_case_column_name].index.size):
        input_str = str(target_df[special_case_column_name][row_index])

        if input_str == "nan":
            if debug_flag:
                print("[WARNING] Special Case String is null at index {}".format(row_index))

            continue

        # print("[{}]".format(input_str))

        trial = parse_template_regex(input_str)

        insert_df[special_case_column_name][row_index] = trial

        if trial < 0:
            print("[FATAL ERROR] ERROR WHILE MATCHING REGEX at index {} !!".format(row_index))
            print_row_data(target_df, default_case_name, row_index)

        if debug_flag is True:
            print("Special Case at index {} is marked as {}".format(row_index, insert_df[special_case_column_name][row_index]))


    target_df["Special"] = insert_df

    return target_df 



def create_agency_regex_list(agency_file):
    agency_regex_list = []
    with open(agency_file, encoding = 'utf8') as agencies:
        for line in agencies:
            if debug_flag is True:
                print("regex: {}".format(line.rstrip()))

            if line.strip() and line.strip(u"\ufeff").strip(): 
                agency_regex_list.append(re.compile(line.strip().rstrip().strip(u"\ufeff")))

    if debug_flag is True:
        print(agency_regex_list)

    return agency_regex_list



def is_found_in(regex_list, test_str):

    # print("test_str: [{}]".format(test_str))

    for regex in regex_list:
        trial = re.search(regex, test_str)
        if trial is not None:
            return True
    
    return False






# {400 - 700 || 1000 - 1600} => A , {120 - 134} => B, { <0 , other} => C
# Note: Other: 0, National Security: -2, Error: -1, NO_Match : -3

# this is a simple version
def law_filter(law_key):

    if (law_key > 40000 and law_key <= 70000) or (law_key >= 110000 and law_key <= 150000) or (law_key >=120 and law_key <= 134) or (law_key == 213) or (law_key < 0):
        return law_key
    else:
        return 0



def extract_law_info(law_df, target_df, law_column_name_list):


    # tmp
    tmp_law_col_name = "Law"
    
    insert_df = pd.DataFrame(index = target_df.index, columns= [tmp_law_col_name])

    if debug_flag:
        insert_raw_df = pd.DataFrame(index = target_df.index, columns= [tmp_law_col_name])

    # print(insert_df)

    for row_index in range(default_effective_offset, law_df[corruption_law_column_name].index.size):

        if str(law_df[level_column_name][row_index]) == "nan":
            print("[WARNING] index {} is null ... skip".format(row_index))
            print_row_data(law_df, default_law_name, row_index)
            continue
        #else:
        #    print("Person: {} level: {}".format(law_df[person_column_name][row_index], str(law_df[level_column_name][row_index])))


        law_result = match_laws(law_df, row_index, law_regex_list, law_column_name_list)

        if debug_flag:
            print("Result law string: {}".format(law_result))

        # filtering and insert to the df
            
        insert_df[tmp_law_col_name][row_index] = law_filter(law_result)

        if debug_flag:
            insert_raw_df[tmp_law_col_name][row_index] = law_result


    
    target_df["Law"] = insert_df

    if debug_flag:
        target_df["Law_Raw"] = insert_raw_df

    return target_df



# law matching !

default_max_key_val = 10000000      # tmp value
default_national_security_key = -2

def match_laws(law_df, row_index, regex_list, column_name_list):

    error_flag = False
    no_match_flag = True
    national_security_flag = False

    final_key = int(default_max_key_val)           # tmp number 

    for i in range(0, len(column_name_list)):

        if debug_flag is True:
            print("index: {}, input string:[{}]".format(row_index, str(law_df[column_name_list[i]][row_index])))


        # kaocc: we should find all the matches here ..
        #law_match = re.search(regex_list[i], str(law_df[column_name_list[i]][row_index]))

        law_match = None
        law_matches = re.finditer(regex_list[i], str(law_df[column_name_list[i]][row_index]))

        for law_match in law_matches:

            # print(law_match)

            result = int(0)
            for group in law_match.groups():
                # print(group)
                
                if group is not None:
                    result = result * 100 + int(group)
                else:
                    result = result * 100

            # result = "{}-{}-{}".format(law_match[1], law_match[2], law_match[3])        # check this one !
            
            #print(result)

            if result < final_key:
                final_key = result

            # return result


        if law_match is None:

            if (str(law_df[column_name_list[i]][row_index]) != "nan") and str(law_df[column_name_list[i]][row_index]).strip():

                # exception fo national security
                if re.search("國安", str(law_df[column_name_list[i]][row_index])) is not None:
                    national_security_flag = True
                    print("Data at row index {} indicate a national security issue".format(row_index))
                    break

                print("[ERROR] Data at row index {} causes an error while matching {} ! Data : [{}] ".format(row_index, column_name_list[i] ,str(law_df[column_name_list[i]][row_index])))
                print_row_data(law_df, default_law_name, row_index)
                error_flag = True

            else:
                if debug_flag:
                    print("[INFO] [{}] has no match in {}".format(str(law_df[column_name_list[i]][row_index]), column_name_list[i]))
        else:
            no_match_flag = False
            break

    
    if error_flag:
        return -1
    elif national_security_flag:
        print("[INFO] Data at row index {} indicate a national security issue".format(row_index))
        return default_national_security_key
    elif no_match_flag:
        print("[ERROR] Data at row index {} have no matching at all, this might be an Error !".format(row_index))
        print_row_data(law_df, default_law_name, row_index)
        return -3

    else:

        return final_key







# main logic here
def main():

    print(__copyright__)

    if len(sys.argv) > 2:
        print("[ERROR] : too many arguments ... {} in total".format(len(sys.argv)))
        print("Argument list: {}\n".format(sys.argv))
        print("Program Usage: python [Excel file loaction]")
        return

    target_file = default_target_file

    if len(sys.argv) == 2:
        target_file = sys.argv[1]
        

    raw_df = create_raw_df(target_file, default_sheet_name, default_usecols_case_list, default_case_name)
    raw_df.to_excel("raw_df.xlsx")

    sanity_check(raw_df, default_case_name, [3, 4, 5, 6])

    fill_df = generate_complex_df(raw_df)

    # print(fill_df.head())

    print(" ==== Calculate the number of cases ===== ")

    num_case_record_df = calculate_case_records(raw_df)
    num_case_record_df = append_statistic_cells(num_case_record_df)
    num_case_record_df.to_excel("num_case_record.xlsx")


    print(" ==== Calculate the number of people ===== ")
    num_people_record_df = calculate_case_records(fill_df)
    num_people_record_df = append_statistic_cells(num_people_record_df)
    num_people_record_df.to_excel("num_people_record.xlsx")

    print(" ==== People Records ===== ")
    num_gender_record_df = calculate_people_records(fill_df)
    num_gender_record_df = append_statistic_cells(num_gender_record_df)
    num_gender_record_df.to_excel("num_gender_record.xlsx")


    print(" ==== Case Analysis ===== ")
    case_level_out_df = create_output_dataform("case_row.txt", "level_col.txt")
    case_level_out_df = row_col_analysis(fill_df, case_level_out_df, "case_row.txt", "level_col.txt", default_case_name[1] , default_case_name[6], False)

    print(" ==== Case Analysis Finished =====")


    # print(case_level_out_df)

    # read agency lists

    agencies_list = []
    central_admin_regex_list = create_agency_regex_list("central_admin.txt")
    local_admin_regex_list = create_agency_regex_list("local_admin.txt")
    central_council_regex_list = create_agency_regex_list("central_council.txt")
    local_council_regex_list = create_agency_regex_list("local_council.txt")


    agencies_list = [central_admin_regex_list, local_admin_regex_list, central_council_regex_list, local_council_regex_list]

        
    result = extract_agency_info(agencies_list, fill_df)
    result_df = extract_special_case_info(result)

    # print(result_df)


    # create agency df


    print(" ==== Agency Analysis ===== ")
    case_agency_out_df = create_output_dataform("case_row.txt", "agency_col.txt")
    case_agency_out_df = row_col_analysis(fill_df, case_agency_out_df, "case_row.txt", "agency_col.txt", default_case_name[1], "Agency", False)

    print(" ==== Agency Analysis Finished ===== ")




    print(" ==== Law Analysis ===== ")


    # law analysis test

    law_df = create_raw_df(target_file, default_sheet_name, default_usecols_law_list, default_law_name)

    # law_df = pd.read_excel(default_target_file, sheet_name = default_sheet_name, header = None, usecols = default_usecols_law_list, names = default_law_name)

    law_df.to_excel("law_df.xlsx")
    sanity_check(law_df, default_law_name, [0, 1])

    law_df.dropna(thresh = default_law_non_na_count, inplace = True)
    law_df.reset_index(drop = True, inplace = True)

    # print(law_df)
    # print(law_df.axes)



    law_column_name_list = [corruption_law_column_name, criminal_law_column_name, other_law_column_name]


    result_df = extract_law_info(law_df, result_df, law_column_name_list) # to be removed or changed


    law_level_out_df = create_output_dataform("law_row.txt", "level_col.txt")
    law_level_out_df, law_level_ratio_df = row_col_analysis(result_df, law_level_out_df, "law_row.txt", "level_col.txt", "Law", default_case_name[6], True)


    law_agency_out_df = create_output_dataform("law_row.txt", "agency_col.txt")
    law_agency_out_df, law_agency_ratio_df  = row_col_analysis(result_df, law_agency_out_df, "law_row.txt", "agency_col.txt", "Law", "Agency", True)


    print(" ==== Law Analysis Finished ===== ")


    print(" === Special Case Analysis === ")

    special_agency_out_df = create_output_dataform("special_row.txt", "agency_col.txt")
    special_agency_out_df, special_agency_ratio_df = row_col_analysis(result_df, special_agency_out_df, "special_row.txt", "agency_col.txt", "Special", "Agency", True)

    special_level_out_df = create_output_dataform("special_row.txt", "level_col.txt")
    special_level_out_df, special_level_ratio_df = row_col_analysis(result_df, special_level_out_df, "special_row.txt", "level_col.txt", "Special", default_case_name[6], True)

    case_special_out_df = create_output_dataform("case_row.txt", "special_row.txt")
    raw_df = extract_special_case_info(raw_df)
    case_special_out_df, case_special_ratio_df = partial_row_col_analysis(raw_df, case_special_out_df, "case_row.txt", "special_row.txt", default_case_name[1], "Special", default_case_name[0], True)



    print(" === Special Case Analysis Finish ===")




    print(" ==== Output to Excel ===== ")

    # output to excel


    case_level_out_df.to_excel("case_level_out.xlsx")
    case_agency_out_df.to_excel("case_agency_out.xlsx")
    law_level_out_df.to_excel("law_level_out.xlsx")
    law_agency_out_df.to_excel("law_agency_out.xlsx")
    special_agency_out_df.to_excel("special_agency_out.xlsx")
    special_level_out_df.to_excel("special_level_out.xlsx")
    case_special_out_df.to_excel("case_special_out.xlsx")

    special_agency_ratio_df.to_excel("special_agency_ratio.xlsx")
    special_level_ratio_df.to_excel("special_level_ratio.xlsx")
    case_special_ratio_df.to_excel("case_special_ratio.xlsx")

    law_level_ratio_df.to_excel("law_level_ratio.xlsx")
    law_agency_ratio_df.to_excel("law_agency_ratio_df.xlsx")


    result_df.to_excel("result.xlsx")


    print(" ==== Output Finished ===== ")

        
    print(" -------------- End of the Story --------------")



    # --- debug ---


    # print(fill_df.axes)
    # print(law_df.axes)




if __name__ == "__main__":
    try:
        import pandas as pd
        main()
    except:
        print(sys.exc_info()[0])
        import traceback
        print(traceback.format_exc())
    finally:
        print("Press Enter to continue ...") 
        input()


