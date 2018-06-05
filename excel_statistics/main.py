

import os
import re
import pandas as pd

# configs & parameters

debug_flag = False


# KaoCC: change this to the actual location
default_target_file = r'C:/Users/mojtpm/Downloads/test.xls'
default_sheet_name = "Sheet1"

# --- unused ---
# default_start_row_index = 3
# default_header_index = 0
# default_usecols = 21

default_non_na_count = 2
default_usecols_case_list = [0, 7, 8, 12, 14, 16, 17]
default_case_name = ["編號", "弊端類型", "特殊貪瀆案件註記", "公務員姓名", "性別", "主管機關", "職務層級"]

default_usecols_law_list = [12, 17, 18, 19, 20]
default_law_name = ["公務員姓名", "職務層級", "貪污治罪條例", "刑法瀆職罪章", "其他"]


corruption_law_regex = "第(\d+)條第(\d+)項第(\d+)款"


default_effective_offset = 0

raw_df = pd.read_excel(default_target_file, sheet_name = default_sheet_name, header = None, usecols = default_usecols_case_list, names = default_case_name)

# print(raw_df.head())

#print(raw_df[default_case_name[0]])
#print(raw_df[default_case_name[1]])
#print(raw_df[default_case_name[2]])
#print(raw_df[default_case_name[3]])

# print(raw_df.dtypes)
# print(raw_df.index)



print(raw_df.axes)

# print(raw_df)


# ----------------------




#------------------------
# test the format

def print_row_data(reference_df, row_index):
    print("\n ------ Row Data with index {} Print Out: ------ \n".format(row_index))
    for i in range(0,len(default_case_name)):
        print((reference_df[default_case_name[i]][row_index]))

    print("\n ------ END ------ \n")






#-----------------------

def generate_complex_df(reference_df):

    complex_df = pd.DataFrame(reference_df, copy = True)
    complex_df.dropna(thresh = default_non_na_count, inplace = True)
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
            table[line.rstrip()] = 0

    for row_index in range(default_effective_offset, reference_df.index.size):
        num = reference_df[default_case_name[0]][row_index]
        record = str(reference_df[default_case_name[1]][row_index])

        if record in table and str(num) != "nan":
            table[record] += 1
        else:
            if record != "nan" and str(num) == "nan":
                print("[WARNING]: Possible duplication found at index {} : {}".format(row_index, record) )
            elif record == "nan" and str(num) == "nan":
                print("[WARNING]: Possibly belong to the prevoius case at index {}".format(row_index) )
            elif record not in table and record != "nan":
                print("[WARNING]: {} at index {} not found in the table !".format(row_index, record))
            else:
                print("[WARNING]: Data at index {} have not been recorded due to unknown reasons, please check manually".format(row_index))
                print_row_data(reference_df, row_index)


    print(" === Case Result")
    print(table)
    print(" --- total: {} --- ".format(sum(table.values())))

    print(" === Sorted Result:")
    print(sorted(table.items(), key = lambda x: x[1]))


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
                print_row_data(reference_df, row_index)
        except ValueError:
            print("[EXCEPTION]: People at index {} causes an exception, please check manually".format(row_index))
            print_row_data(reference_df, row_index)




    print(" === People Result")
    print(level_table)
    print(gender_table)

    total_count = sum(level_table.values())
    print(" --- total: {} --- ".format(total_count))

    level_percentage = [0] * len(level_table)
    for (key, value) in level_table.items():
        level_percentage[key - 1] = value / total_count

    print(level_percentage)
    




    



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
    

    


# KaoCC: the parameters should be changed in the future patches..
def case_analysis(reference_df, out_df, row_file, col_file):

    # these should be merged into "create_output_dataform" 
    row_set = set()
    col_set = set()

    with open(row_file, encoding = 'utf8') as row_label_file:
        for label in row_label_file:
            if debug_flag is True:
                print("row label: [{}]".format(label.rstrip()))
            
            if label.strip() and label.strip(u"\ufeff").strip():
                row_set.add(label.strip().rstrip().strip(u"\ufeff"))

    with open(col_file, encoding = 'utf8') as col_label_file:
        for label in col_label_file:
            if debug_flag is True:
                print("col label: [{}]".format(label.rstrip()))

            if label.strip() and label.strip(u"\ufeff").strip():
                col_set.add(label.strip().rstrip().strip(u"\ufeff"))

    for row_index in range(default_effective_offset, reference_df.index.size):

        try:
            case = str(reference_df[default_case_name[1]][row_index])
            level = str(int(reference_df[default_case_name[6]][row_index]))


            if case != "nan" and level != "nan" and case in row_set and level in col_set:


                if str(out_df.at[case, level]) == "nan":
                    out_df.at[case, level] = 1
                else:
                    out_df.at[case, level] += 1

            else:
                print("Possible Error found at index {} with data: {}, {}".format(row_index, case, level))
                print_row_data(reference_df, row_index)

        except ValueError:
            print("[EXCEPTION]: People at index {} causes an exception, please check manually".format(row_index))
            print_row_data(reference_df, row_index)




    col_list = list(out_df)

    out_df.insert(0, "總計", out_df[col_list].sum(axis = 1))

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


    if debug_flag is True:
        print(out_df)


    return out_df



def parse_template(template_string):

    selected_flag = False
    line_count = 0
    for line in template_string.splitlines():

        if not line.strip() or (line_count == 0 and line[0] != '1'):
            continue

        line_count += 1

        if debug_flag is True:
            print("line: [{}]".format(line.rstrip()))

        if line[0] == u'■' or line[0] == u'▓':      # check the special char ?!?
            selected_flag = True
            break
    
    if selected_flag is True:

        if line_count <= 7:
            return 1
        elif line_count == 8:
            return 2
        elif line_count >= 9 and line_count <= 11:
            return 3
        elif line_count == 12:
            return 4
        elif line_count == 13 :
            return 5
        else:
            print("[ERROR]: Error while parsing string: {}".format(template_string))
            return -2   # Error
    else:
        return -1
                



def extract_agency_info(agencies_regex_list, target_df):

    agency_column_name = default_case_name[5]

    insert_df = pd.DataFrame(data = target_df[agency_column_name])

    # print(insert_df)

    for row_index in range(default_effective_offset, target_df[agency_column_name].index.size):

        # print(target_df[row_index])

        error_flag = True
        for i in range(0, len(agencies_regex_list)):
            input_str = str(target_df[agency_column_name][row_index])
            found_flag = is_found_in(agencies_list[i], input_str)

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

        # print("[{}]".format(input_str))

        insert_df[special_case_column_name][row_index] = parse_template(input_str)
        
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





# main logic here



fill_df = generate_complex_df(raw_df)

# print(fill_df.head())

print(" ==== calculate_case_records ===== ")
calculate_case_records(raw_df)
#calculate_people_records(raw_df)


calculate_case_records(fill_df)
calculate_people_records(fill_df)


print(" ==== Case Analysis ===== ")
out_df = create_output_dataform("case_row.txt", "level_col.txt")
out_df = case_analysis(fill_df, out_df, "case_row.txt", "level_col.txt")


# raw_df.to_excel("raw.xls")
# fill_df.to_excel("fill.xls")
# out_df.to_excel("tmp.xls")


print(out_df)


# read agency lists

agencies_list = []
central_admin_regex_list = create_agency_regex_list("central_admin.txt")
local_admin_regex_list = create_agency_regex_list("local_admin.txt")
central_council_regex_list = create_agency_regex_list("central_council.txt")
local_council_regex_list = create_agency_regex_list("local_council.txt")


agencies_list = [central_admin_regex_list, local_admin_regex_list, central_council_regex_list, local_council_regex_list]

    
result = extract_agency_info(agencies_list, fill_df)
result_df = extract_special_case_info(result)

print(result_df)


# output to excel

out_df.to_excel("out.xls")
result_df.to_excel("result.xls")




# law analysis test

law_df = pd.read_excel(default_target_file, sheet_name = default_sheet_name, header = None, usecols = default_usecols_law_list, names = default_law_name)
print(law_df)
print(law_df.axes)


corruption_law_regex_inst = re.compile(corruption_law_regex)


corruption_law_column_name = default_law_name[2]
for row_index in range(default_effective_offset, law_df[corruption_law_column_name].index.size):
    print(law_df[corruption_law_column_name][row_index])


    law_match = re.match(corruption_law_regex_inst, str(law_df[corruption_law_column_name][row_index]))

    if law_match is not None:
        print("{}-{}-{}".format(law_match[1], law_match[2], law_match[3]))
    else:
        print("{} has no match".format(str(law_df[corruption_law_column_name][row_index])))



    

    



# --- debug ---
#print_row_data(raw_df, 213)
#print_row_data(raw_df, 214)
#print_row_data(raw_df, 215)