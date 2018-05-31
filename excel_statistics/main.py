

import os
import pandas as pd

# configs & parameters

debug_flag = False

default_target_file = r'C:/Users/mojtpm/Downloads/test.xls'
default_sheet_name = "Sheet1"
# default_start_row_index = 3
# default_header_index = 0
# default_usecols = 21

default_usecols_list = [0, 7, 8, 12, 14]
default_name = ["編號", "弊端類型", "特殊貪瀆案件註記\n（非屬特殊貪瀆案件者，毋庸註記）", "公務員姓名", "性別"]

default_effective_offset = 4

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


# print(raw_df.axes)



# ----------------------

#table = {"1.工商監督管理": 0, "3.稅務" : 0, "4.關務" : 0, "6.公路監理" : 0, "7.運輸觀光氣象" : 0, "8.司法" : 0, "9.法務" : 0,  "10.警政" : 0, "11.消防" : 0, "12.營建" : 0, "13.民戶役地政" : 0,
# "14.入出國及移民與海岸巡防" : 0, "15.環保" : 0, "16.衛生醫療" : 0, "18.教育" : 0, "19.農林漁牧" : 0, "20.河川及砂石管理" : 0, "21.軍方事務" : 0, "23.國家安全情報" : 0, "24.國有財產事務" : 0, "26.行政事務" : 0, "27.其他" : 0}

table = {}

with open("type.txt", encoding = 'utf8') as type_file:
    for line in type_file:
        print("[{}]".format(line.rstrip()))
        table[line.rstrip()] = 0


# test the raw format 

# default_start_row_index = 35
# tmp_end_index = 70


# tmp_row_data = None
# for row_i in range(default_start_row_index, tmp_end_index):
#
#    # print(raw_df.iloc[row_i])
#    counter = 0
#    for data in raw_df.iloc[row_i] :
#        # print("data : {0} ".format(counter) + str(data))
#        counter = counter + 1
#
#    #for i in raw_df.iloc[row_i]:
#
#    print(" ---------------------- ")
#    tmp_row_data = raw_df.iloc[row_i]



#for data in raw_df["弊端類型"]:
#    print(data)



#------------------------
# test the format

print(" --- Test Data Print Out:")
for i in range(0,len(default_name)):
    print((raw_df[default_name[i]][247]))

print(" --- END")

#------------------------


for row_index in range(default_effective_offset, raw_df.index.size):
    num = raw_df[default_name[0]][row_index]
    record = raw_df[default_name[1]][row_index]

    if str(record) in table and str(num) != "nan":
        table[str(record)] += 1
    else:
        if str(record) != "nan" and str(num) == "nan":
            print("[WARNING]: Possible duplication found at index {} : {}".format(row_index, str(record)) )
        elif str(record) not in table and str(record) != "nan":
            print("[WARNING]: {} at index {} not found in the table !".format(row_index, str(record)))
        else:
            print("[WARNING]: Data at index {} have not been recorded due to unknown reasons, please check manually".format(row_index))


print(" === Result")
print(table)
print(" --- total: {} --- ".format(sum(table.values())))

print(" === Sorted Result:")
print(sorted(table.items(), key = lambda x: x[1]))


# -----


