
===================================================
INSTALLATION INSTRUCTION
===================================================
Install Python 3.x : https://www.python.org/downloads/
	Check the box to add to the "Environment Variable"

Download and save the chromedriver in the same folder as the timecardauto.py:
	 https://chromedriver.chromium.org/downloads

Install Selenium (source: https://pypi.org/project/selenium/)
	pip install selenium 

Install encryption:
	pip install pycryptodome

====================================================
To Run the Time Card program manually
====================================================
Click the timecardauto.py to start the time card.

====================================================
To run the Time Card program by schedule
====================================================
Go to this link for a general instruction:
	https://datatofish.com/python-script-windows-scheduler/

Similar to the instruction except for the *.bat file adjustment:
	<your python.exe path> <your timecardouto.py path> <the directory of the timecardauto.py>

For example, you create a file named "TimeCard.bat", edit the file and put the following line:
	"C:\Python\python.exe" "E:\mytimecard\timecardauto.py" "E:\mytimecard"

