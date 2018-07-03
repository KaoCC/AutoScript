# AutoScript
A set of handy scripts that helps to automate routine tasks.


----


## Excel

Parse and extract the information from excel files and perform a wide viarity of analysis on them.

### Requirements

- [Python 3.6 +](https://www.python.org/)
- [Pandas 0.32 +](https://pandas.pydata.org/)
- [xlrd](http://www.python-excel.org/)
- [OpenPyXL](https://openpyxl.readthedocs.io/en/stable/)


### Preliminary

Execute or double-click the script click_me_first.py to install the required packages

### Usage

`python main.py path/to/excel_file`


### Notes

- The default file name for the excel file is 'target.xlsx' with sheet name 'Sheet1'. On windows system, one can put the target file in the same folder that contains the python script and double click the script to execute it in order to simplify the process.

- One should remove unnecessary cells such as the header and the comments before processing.

