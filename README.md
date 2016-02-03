# Regional Module processing software
A Regional Module data management system created using Python and SQLite. Using the simply designed graphical user interface(GUI) `RM_GUI.py`, users are able to:

* import filled Excel questionnaires to the SQLite database;
* export country specific data points and complete questionnaire tables back to Excel;
* modify and clean the data in Excel and re-import then back in the SQLite database;
* create different copies of country specific data, one to hold the original data, one for cleaning and one for dissemination.
* calculate specific data indicators.

**For more information see the complete [User Manual](Documentation/user-manual.html)**.

![](Documentation/img/RM_GUI.png "Regional model user interface")

## Installation (on windows)
### Required packages:

* Python `>=3.4`. 
* [xlsxWriter](https://xlsxwriter.readthedocs.org/) version 0.7.3.
* [xlrd](https://pypi.python.org/pypi/xlrd) version 0.9.4. However
  xlrd has some issues in processing comments. A fix patch is submitted to the maintainer, but has not been integrated yet. Therefore, until the patch is integrated please use the xlrd 0.9.4 version in the following GitHub [repo](https://github.com/melmasri/xlrd).

All those packages could be installed using
[PIP](https://pypi.python.org/pypi/pip). On Windows PIP is bundled
with Python, if not, install it by downloading  [get-pip.py](get-pip.py) and running the following command in the terminal where `get-pip.py` exist. (for more details see [this](https://pip.pypa.io/en/stable/installing.html#install-pip))

```
python get-pip.py
```

Once PIP is installed run the following in your terminal to install all required packages.

```
pip install xlsxwriter
pip install https://github.com/melmasri/xlrd/archive/master.zip
```

### Installation of the main package
Two installation options are available:

* **Downloading**: download and extract the following [zip file.](https://github.com/melmasri/RMS/archive/master.zip).
* **Git cloning**: in your terminal run `git clone https://github.com/melmasri/RMS`

Move the downloaded/cloned folder to your desired destination and then create a shortcut to `RM_GUI.py`.

To start double-click on the `RM_GUI.py` shortcut and the GUI should pop-up.

**For more details refer to**

* A complete [User Manual](Documentation/user-manual.html) in HTML format.
* A complete [User Manual](Documentation/user-manual.org) in git markdown format.
* Python [help files](Documentation/Python help/).

## Issues and extra features <sup>[1](#myfootnote1)</sup>
Report issues and suggest features and improvements on the [GitHub issue tracker.](https://github.com/melmasri/RMS/issues)


<a name="myfootnote1">1</a>: The addition of new features are at the developers discretion.

## Folder tree


``` sh
10 directories, 42 files

RMS/
├── Database
│   ├── Inserted data
│   │   ├── ADM_table.csv
│   │   ├── All AC CODES.csv
│   │   ├── Country.csv
│   │   ├── EDU_INDICATOR_AID.csv
│   │   ├── EDU_INDICATOR_AID_full.xlsx
│   │   ├── EDU_METER_AID(data).csv
│   │   ├── Magnitude(data).csv
│   │   ├── NEW AC CODES inserted in EDU_METER_AID.csv
│   │   ├── Qualifier.csv
│   │   ├── RM_Mapping.csv
│   │   └── RM_Mapping_NonNumeric.csv
│   ├── create_database.bat
│   ├── create_tables.sql
│   ├── insert_data.sql
│   ├── insert_indic_labels.sql
│   ├── library.sql
│   ├── main.sql
│   ├── migration_to_DB_with_indic.sql
│   ├── Prod.db
│   └── README.md
├── Documentation
│   ├── css
│   ├── img
│   ├── Python help
│   │   ├── rmExcelWriter.html
│   │   ├── rmfunctions.html
│   │   ├── RM_GUI.html
│   │   ├── rmindicators.html
│   │   └── rmsqlfunctions.html
│   ├── user-manual.html
│   └── user-manual.org
├── Export
│   └── README.md
├── Import
│   └── README.md
├── Libraries
│   ├── algebra-div.csv
│   ├── algebra-prod.csv
│   ├── algebra-sum.csv
│   ├── Pip install.md
│   ├── rmExcelWriter.py
│   ├── rmfunctions.py
│   ├── rmindicators.py
│   ├── rmquestionnaire.py
│   ├── rmsqlfunctions.py
│   └── variables_for_preprocessing.json
├── Log
│   └── README.md
├── README.md
└── RM_GUI.py
```
