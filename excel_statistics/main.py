

import os
import pandas as pd

# configs & parameters

default_target_file = r'/Users/CCKao/Downloads/test.xls'
default_sheet_name = "Sheet1"
# default_start_row_index = 3
# default_header_index = 0
# default_usecols = 21

default_usecols_list = [7, 8, 12, 14]
default_name = ["弊端類型", "特殊貪瀆案件註記\n（非屬特殊貪瀆案件者，毋庸註記）", "公務員姓名", "性別"]


raw_df = pd.read_excel(default_target_file, sheet_name = default_sheet_name, header = None, usecols = default_usecols_list, names = default_name)

# print(raw_df.head())

#print(raw_df["弊端類型"])
#print(raw_df[default_name[1]])
#print(raw_df[default_name[2]])
#print(raw_df[default_name[3]])

# print(raw_df.dtypes)
# print(raw_df.index)

#for index in raw_df.index:
#    print(index)

#print(raw_df.head(1))

# print(raw_df.iloc[0])
print(raw_df.axes)

# print(raw_df[5])



# ----------------------

#table = {"1.工商監督管理": 0, "3.稅務" : 0, "4.關務" : 0, "6.公路監理" : 0, "7.運輸觀光氣象" : 0, "8.司法" : 0, "9.法務" : 0,  "10.警政" : 0, "11.消防" : 0, "12.營建" : 0, "13.民戶役地政" : 0,
# "14.入出國及移民與海岸巡防" : 0, "15.環保" : 0, "16.衛生醫療" : 0, "18.教育" : 0, "19.農林漁牧" : 0, "20.河川及砂石管理" : 0, "21.軍方事務" : 0, "23.國家安全情報" : 0, "24.國有財產事務" : 0, "26.行政事務" : 0, "27.其他" : 0}

table = {}

with open("type.txt") as type_file:
    for line in type_file:
        print("[{0}]".format(line.rstrip()))
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


count = 0
for record in raw_df[default_name[0]]:
    if str(record) in table:
        table[str(record)] += 1
    else:
        if str(record) != "nan":
            print("{} not found in the table !".format(str(record)))

print(count)
print(table)
print(sum(table.values()))

print(sorted(table.items(), key = lambda x: x[1]))


