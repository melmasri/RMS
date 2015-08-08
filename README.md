# Regional Module processing software


## Installation (on windows)
### Required packages:

* Python 3.4 64 bit. 
* [xlsxWriter](https://xlsxwriter.readthedocs.org/), tested under version 0.7.3.
* [xlrd](https://pypi.python.org/pypi/xlrd), tested under version 0.9.4. However, xlrd has some issues in processing comments. A fix patch is submitted to the maintainer, but has not beed integrated yet. Therefore, until the patch is integrated please use the xlrd 0.9.4 version in the following github [repo](https://github.com/python-excel/xlrd).

All those packages could be installed using [Pip](https://pypi.python.org/pypi/pip), which could be installed by downloading the [get-pip.py](get-pip.py) and run the following in the terminal where `get-pip.py` exist. (for more details see [this](https://pip.pypa.io/en/stable/installing.html#install-pip))

```
python get-pip.py
```
Once Pip is installed run the following in your terminal

```
pip install xlsxwriter
pip install https://github.com/melmasri/xlrd.zip
```

### Installation of the main package
download or clone this repository

* **To download**: click on the download link on the left, or   [here](https://github.com/melmasri/RMS/archive/master.zip).
* **To clone**: in your terminal run `git clone https://github.com/melmasri/RMS`


Move the downloaded/cloned folder to your desired destination and then create a shortcut to `RM_GUI.py`.

To start double-click on the `RM_GUI.py` shortcut.

For more details please see the 

