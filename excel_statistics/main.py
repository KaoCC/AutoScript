

import os
import pandas as pd

# configs & parameters

target_file = r'C:/Users/mojtpm/Downloads/test.xls'
default_sheet_name = "Sheet1"
default_start_row_index = 3

raw_df = pd.read_excel(target_file, sheet_name = default_sheet_name)

# print(raw_df.head())

# print(raw_df["弊端類型"])


# print(raw_df.dtypes)

# print(raw_df.index)

#for index in raw_df.index:
#    print(index)

#print(raw_df.head(1))

# print(raw_df.iloc[0])
#print(raw_df.axes)

# print(raw_df[5])




# test the raw format 

default_start_row_index = 35

tmp_end_index = 70



for row_i in range(default_start_row_index, tmp_end_index):

    counter = 0
    for data in  raw_df.iloc[row_i] :
        print("data : {0} ".format(counter) + str(data))
        counter = counter + 1

    print(" ---------------------- ")


