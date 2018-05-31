

import os
import pandas as pd

# configs & parameters

debug_flag = False

default_target_file = r'C:/Users/mojtpm/Downloads/test.xls'
default_sheet_name = "Sheet1"
# default_start_row_index = 3
# default_header_index = 0
# default_usecols = 21

default_non_na_count = 2
default_usecols_list = [0, 7, 8, 12, 14, 17]
default_name = ["編號", "弊端類型", "特殊貪瀆案件註記\n（非屬特殊貪瀆案件者，毋庸註記）", "公務員姓名", "性別", "職務層級\n1.簡任(相當)\n2.薦任(相當)\n3.委任(相當)\n4.約聘僱等\n5.其他"]

default_effective_offset = 0

raw_df = pd.read_excel(default_target_file, sheet_name = default_sheet_name, header = None, usecols = default_usecols_list, names = default_name)

# print(raw_df.head())

#print(raw_df["弊端類型"])
#print(raw_df[default_name[0]])
#print(raw_df[default_name[1]])
#print(raw_df[default_name[2]])
#print(raw_df[default_name[3]])

# print(raw_df.dtypes)
# print(raw_df.index)

#for index in raw_df.index:
#    print(index)


print(raw_df.axes)



# ----------------------




#------------------------
# test the format

def print_row_data(reference_df, row_index):
    print(" --- Row Data Print Out: --- ")
    for i in range(0,len(default_name)):
        print((reference_df[default_name[i]][row_index]))

    print(" --- END --- ")






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
            print("[{}]".format(line.rstrip()))
            table[line.rstrip()] = 0

    for row_index in range(default_effective_offset, reference_df.index.size):
        num = reference_df[default_name[0]][row_index]
        record = reference_df[default_name[1]][row_index]

        if str(record) in table and str(num) != "nan":
            table[str(record)] += 1
        else:
            if str(record) != "nan" and str(num) == "nan":
                print("[WARNING]: Possible duplication found at index {} : {}".format(row_index, str(record)) )
            elif str(record) == "nan" and str(num) == "nan":
                print("[WARNING]: Possibly belong to the prevoius case at index {}".format(row_index) )
            elif str(record) not in table and str(record) != "nan":
                print("[WARNING]: {} at index {} not found in the table !".format(row_index, str(record)))
            else:
                print("[WARNING]: Data at index {} have not been recorded due to unknown reasons, please check manually".format(row_index))


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
        name = reference_df[default_name[3]][row_index]
        gender = reference_df[default_name[4]][row_index]
        level = reference_df[default_name[5]][row_index]

        if isinstance(level, int) and int(level) in level_table and str(gender) in gender_table and str(name) != "nan":
            # print("{}, {}, {}".format(row_index, str(name), int(level)))
            level_table[int(level)] += 1
            gender_table[str(gender)] += 1
        elif str(name) == "nan" and str(level) == "nan" and str(gender) == "nan":
            print("[WARNING]: Possible invalid data or null at index {}, skipping ...".format(row_index))
        else:
            print("[WARNING]: People at index {} have not been recorded due to unknown reasons, please check manually".format(row_index))


    print(" === People Result")
    print(level_table)
    print(gender_table)

    total_count = sum(level_table.values())
    print(" --- total: {} --- ".format(total_count))

    level_percentage = [0] * len(level_table)
    for (key, value) in level_table.items():
        level_percentage[key - 1] = value / total_count

    print(level_percentage)
    




    


    







# main logic here


# print_row_data(raw_df, 11)


fill_df = generate_complex_df(raw_df)

calculate_case_records(raw_df)
#calculate_people_records(raw_df)

calculate_case_records(fill_df)
calculate_people_records(fill_df)


print_row_data(fill_df, 2)

print_row_data(fill_df, 153)