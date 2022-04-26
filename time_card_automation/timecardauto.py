from tkinter import *
from tkinter import ttk, messagebox
import sys, json, time, getpass, re
from selenium import webdriver
from datetime import date, timedelta
import subprocess, os
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


project_max = 20  # maximum number display projects

# ================= Encryption ====================================
class Cryptopy:
   id_machine = subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip().replace('-','')
   key = id_machine.encode('UTF-8')
   def encrypt(self, orig_text):
      text_byte = orig_text.encode('UTF-8')
      cipher = AES.new(self.key, AES.MODE_CBC)   
      ct_bytes = cipher.encrypt(pad(text_byte, AES.block_size))
      iv = b64encode(cipher.iv).decode('utf-8')
      ct = b64encode(ct_bytes).decode('utf-8')
      result = json.dumps({'iv':iv, 'ciphertext':ct})
      self.encrypted_json = json.dumps({'iv':iv, 'ciphertext':ct})   
      return self.encrypted_json
   def decrypt(self, encrypted_json):
      b64 = json.loads(encrypted_json)
      iv = b64decode(b64['iv'])
      ct = b64decode(b64['ciphertext'])
      cipher = AES.new(self.key, AES.MODE_CBC, iv)
      self.decrypted = unpad(cipher.decrypt(ct), AES.block_size).decode('UTF-8')
      print(self.decrypted)
      return self.decrypted
      

# ================= TimeCard ====================================

class TimeCard: 
   data = {}
   data['projects'] = []
   browser = "firefox"
   passwd_plain = ""
  
   def __init__(self):
      self.passwd_encrypt = Cryptopy()
      for i in range(project_max):
         tmp = {}
         tmp['name'] = ""
         tmp['hour'] = 0
         tmp['desc'] = ""
         self.data['projects'].append(tmp)
      try:
         try:
            timepath = sys.argv[1].replace("\\","/")  # + "/timecard.json"
            os.chdir(timepath)
            print("======", "using path", timepath)
         except:
            pass
         with open( 'timecard.json' , 'r') as f:
            self.data = json.load(f)
            self.data.pop('passwd', None) #obsolete 'passwd', remove in the future
            try:
               self.data['encrypt_passwd']  # new one, remove in the future
               self.passwd_plain = self.passwd_encrypt.decrypt(self.data['encrypt_passwd'])
            except:
               pass               
      except:
         self.data['username'] = ""
      

# ================ Stop watch to record real-time timecard ============

class StopWatch():
    project_no = 0
    def __init__(self):        
        self._start = 0.0        
        self._elapsedtime = 0.0
        self._running = 0
        self.timestr = StringVar()
    def _update(self):
        if self._running > 0:
           self._elapsedtime = time.time() - self._start
           elapsedhour = self._elapsedtime / 3600.0
           entryHour[self.project_no].set("{0:.3f}".format(elapsedhour)) # time update
           self._setTime(self._elapsedtime)
           self._timer = master.after(3600, self._update)
    def _setTime(self, elap):
        minutes = int(elap/60)
        seconds = int(elap - minutes*60.0)
        hseconds = int((elap - minutes*60.0 - seconds)*100)                
        self.timestr.set('%02d:%02d:%02d' % (minutes, seconds, hseconds))
    def Start(self, projnum):
        self.Stop()
        self.project_no = projnum
        if not self._running:
            self._running = 1
            self._start = time.time() - float(entryHour[self.project_no].get()) * 3600 # self._elapsedtime
            self._update()
    def Stop(self):                                    
        if self._running:
            self._running = 0

# ================= Visible Projects Window =======================

def Save_visible_projects(vp):
   timeCard.data['visibleProjects'] = []
   for nn in range(len(vp)):
      if vp[nn].get():
         timeCard.data['visibleProjects'].append(project_list[nn])
   Save_project()
   Close_all()

def setvisProjects():
   visbox = []
   winVisibleProj = Toplevel(master)
   Button(winVisibleProj, text ="Close and Save Visible Projects",
          command = lambda:Save_visible_projects(visbox)).pack()
   visframes = []
   nvisframe = 6
   for nn in range(nvisframe):
      visframes.append(Frame(winVisibleProj))
      visframes[nn].pack(side=LEFT)
  
   project_list_count = 0
   for nn in range(len(project_list)):
      visbox.append(BooleanVar())
      try:
         visproj = timeCard.data['visibleProjects']
         for mm in range(len(visproj)):
            if visproj[mm] == project_list[nn]:
               visbox[nn].set(True)
      except:
         visbox[nn].set(True)
      
      frameno = project_list_count % nvisframe
      project_list_count = project_list_count + 1
      tt = Checkbutton(visframes[frameno],text=project_list[nn], variable=visbox[nn])
      tt.var = visbox[nn]  
      tt.pack()

# ================= Project Menu Widget ===========================

def Save_project():
   timeCard.data['username']       = userwid.get()
   timeCard.passwd_plain           = passwid.get()
   timeCard.data['encrypt_passwd'] = timeCard.passwd_encrypt.encrypt(passwid.get())

   for nn in range(project_max):
      timeCard.data['projects'][nn]['name'] = menusProj[nn].get()
      timeCard.data['projects'][nn]['hour'] = entryHour[nn].get()
      timeCard.data['projects'][nn]['desc'] = entryDesc[nn].get()

   with open('timecard.json', 'w') as outfile:
      json.dump(timeCard.data, outfile, indent=3)
      
def Reset_hours():
   for nn in range(project_max):
      entryHour[nn].set(0)
      
def Reset_project():
   for nn in range(project_max):
      menusProj[nn].set("")
      entryHour[nn].set(0)
      entryDesc[nn].set("")
# --------------
def Open_web():
   global project_list, driver
   try:
      driver = webdriver.Chrome('chromedriver')  # Optional argument, if not specified will search path.
      timeCard.browser = "chrome"
   except:
      try:
         driver = webdriver.Firefox()  # Optional argument, if not specified will search path.
      except:
         messagebox.showerror("Browser driver Error", "Try download the latest Chromedriver or Firefox Geckodriver")
         master.destroy()
         sys.exit(0)
   driver.get('http://fab4www.cmi.cypress.com/cgi-bin/foundry_time.cgi');
   page_source = str(driver.page_source.encode('utf-8'))
   webprojlist = re.search(".* name=\"project_filter\"><option>(.*)</select>",page_source).group(1).split("<option>")
   project_list = []
   for eachp in webprojlist:
      eachproj = re.search("(.*)</option>", eachp).group(1)
      if len(eachproj)>2:
         project_list.append(eachproj)
   search_box = driver.find_element_by_name('who_filter')
   search_box.send_keys(timeCard.data['username'])
   search_box = driver.find_element_by_id('from_week')
   fromweek = int(search_box.get_attribute('value'))-1
   search_box.clear()
   search_box.send_keys(fromweek)
   search_box = driver.find_element_by_name('submity')
   search_box.submit()

# ----------------
def Close_web():
   global driver
   try:
      driver.quit()
   except:
      print ("No Web interface opened, ignored")
# ---------------
def Close_all():
   Close_web()
   master.destroy()
# ---------------
def Display_date(val):
   today = date.today()
   if val == "Yesterday":
      today = date.today() - timedelta(1)
   elif val == "2 Days Ago":
      today = date.today() - timedelta(2)
   elif val == "3 Days Ago":
      today = date.today() - timedelta(3)
   elif val == "4 Days Ago":
      today = date.today() - timedelta(4)
   elif val == "5 Days Ago":
      today = date.today() - timedelta(5)
   elif val == "6 Days Ago":
      today = date.today() - timedelta(6)
   elif val == "7 Days Ago":
      today = date.today() - timedelta(7)
   calendar_display['text'] = today.strftime('%b %d, %Y')  
# ---------------
def Total_hours():
   Save_project()
   sum_hr = 0.0
   for nn in range(project_max):
      sum_hr += float(timeCard.data['projects'][nn]['hour']) 
   Display_totalHours['text'] = "Total Hours: " + "{0:.1f}".format(sum_hr)

# ========================== Submit Time Card ===================

def Submit_timecard():
   global driver
   Save_project()

   if menuCalendar.get() == "Today":
      today = date.today()
   elif menuCalendar.get() == "Yesterday":
      today = date.today() - timedelta(1)
   elif menuCalendar.get() == "2 Days Ago":
      today = date.today() - timedelta(2)
   elif menuCalendar.get() == "3 Days Ago":
      today = date.today() - timedelta(3)
   elif menuCalendar.get() == "4 Days Ago":
      today = date.today() - timedelta(4)
   elif menuCalendar.get() == "5 Days Ago":
      today = date.today() - timedelta(5)
   elif menuCalendar.get() == "6 Days Ago":
      today = date.today() - timedelta(6)
   elif menuCalendar.get() == "7 Days Ago":
      today = date.today() - timedelta(7) 
   date_card = str(today.month)+'/'+ str(today.day)+'/'+str(today.year)

   search_box = driver.find_element_by_name('login')
   search_box.send_keys('12')
   search_box = driver.find_element_by_name('username')
   search_box.send_keys(timeCard.data['username']) # getpass.getuser())
   search_box = driver.find_element_by_name('password')
   search_box.send_keys(timeCard.passwd_plain + '\n')
   
   for nn in range(project_max):
      if float(timeCard.data['projects'][nn]['hour']) > 0:
         if timeCard.data['projects'][nn]['name'] != "":    
            search_box = driver.find_element_by_name('day')
            search_box.send_keys(date_card)
            search_box = driver.find_element_by_name('project')
            search_box.send_keys(timeCard.data['projects'][nn]['name'])
            search_box = driver.find_element_by_name('hours')
            search_box.clear()
            search_box.send_keys(timeCard.data['projects'][nn]['hour'])
            search_box = driver.find_element_by_name('description')
            search_box.clear()
            search_box.send_keys(str(timeCard.data['projects'][nn]['desc']))
            search_box = driver.find_element_by_name('submitx')
            search_box.submit()
            time.sleep((timeCard.browser == "firefox") * 5) # 5 sec delay for Firefox
   Reset_hours()
   Save_project()
   statusid['text'] = "STATUS: time card has been submitted"
   
            
# ======================== End of Submit Time Card ================


# ======================== Main Window Widgets ====================

master = Tk()
master.title("Time Card Submission. App version April 2022 by Usman Suriono")
timeCard = TimeCard()
stopWatch = StopWatch()
driver = None

import pathlib

current_dir = pathlib.Path(__file__).parent
current_file = pathlib.Path(__file__)
print(current_dir)
print(current_file)

# -- Open the web time card -------------------
Open_web()
try:
   visibleProj = timeCard.data['visibleProjects']
except:
   visibleProj = project_list

# ----- top widgets ------
entryUsername = StringVar()
entryPass     = StringVar()
menuCalendar  = StringVar()
menuCalendar.set("Today")

rowframe = Frame(master)
rowframe.pack(side=TOP, fill=X, padx=5, pady=5)
Label(rowframe,text="User Name").pack(side=LEFT)
userwid = Entry(rowframe, textvariable=entryUsername, width=5)
userwid.pack(side=LEFT)
Label(rowframe,text="Password  ").pack(side=LEFT)
passwid = Entry(rowframe,show="*", textvariable=entryPass,width=6)
passwid.pack(side=LEFT)
calendar_entry = OptionMenu(rowframe, menuCalendar, "Today", "Yesterday",
                            "2 Days Ago", "3 Days Ago", "4 Days Ago",
                            "5 Days Ago", "6 Days Ago", "7 Days Ago",
                            command=Display_date).pack(side=LEFT)
calendar_display = Label(rowframe,text=date.today().strftime('%b %d, %Y'))
calendar_display.pack(side=LEFT)
Button(rowframe, text ="Close Web Interface",  command = Close_web).pack(side=RIGHT)

rowframe = Frame(master)
rowframe.pack(side=TOP, fill=X, padx=5, pady=5)
statusid = Label(rowframe,text="STATUS: No Submission", font=("Courier", 14),fg="red")
statusid.pack(side=LEFT)
Button(rowframe, text ="Close All",  command = Close_all).pack(side=RIGHT)

rowframe = Frame(master)
rowframe.pack(side=TOP, fill=X, padx=5, pady=5)
Button(rowframe, text ="Save"  , command = Save_project).pack(side=LEFT)
Button(rowframe, text ="Reset All",  command = Reset_project).pack(side=LEFT)
Button(rowframe, text ="Reset Hours",  command = Reset_hours).pack(side=LEFT)
Button(rowframe, text ="Check Total Hours",  command = Total_hours).pack(side=LEFT)
Display_totalHours = Label(rowframe,text="Total Hours: ")
Display_totalHours.pack(side=LEFT)

Button(rowframe, text ="Submit", command = Submit_timecard).pack(side=RIGHT)

rowframe = Frame(master)
rowframe.pack(side=TOP, fill=X, padx=5, pady=5)
Button(rowframe, text ="Visible Projects",  command = setvisProjects).pack(side=LEFT)
Label(rowframe, text="Enter project, hours, and description below").pack(side=LEFT)
Button(rowframe, text ="Stop Recording",  command = stopWatch.Stop).pack(side=LEFT)

entryUsername.set( timeCard.data['username'] ) # set username
entryPass.set( timeCard.passwd_plain )

canvas = Canvas(master, width=600,height=4)
canvas.create_line(0, 2, 600, 2)
canvas.pack(fill=BOTH, expand=1)

menusProj = []
entryHour = []
entryDesc = []
buttonStw = []
for nn in range(project_max):
   rowframe = Frame(master)
   rowframe.pack(side=TOP, fill=X, padx=5, pady=5)

   menusProj.append(StringVar())
   entryHour.append(StringVar())
   entryDesc.append(StringVar())
   
   proj_entry = OptionMenu(rowframe, menusProj[nn], *(visibleProj))
   hour_entry = Entry(rowframe, width=10, textvariable=entryHour[nn])
   desc_entry = Entry(rowframe, width=40, textvariable=entryDesc[nn])
   buttonStw.append(Button(rowframe, text="Start Record",
                        command= lambda c=nn : stopWatch.Start(c)))
   
   proj_entry.pack(side=LEFT)
   desc_entry.pack(side=RIGHT)
   buttonStw[nn].pack(side=RIGHT)
   hour_entry.pack(side=RIGHT)

   # in case the project name change
   menusProj[nn].set("")
   entryHour[nn].set(0)
   entryDesc[nn].set("")
   for eproj in project_list:
      if eproj == timeCard.data['projects'][nn]['name']:
         menusProj[nn].set(timeCard.data['projects'][nn]['name'])
         entryHour[nn].set(float(timeCard.data['projects'][nn]['hour']))
         entryDesc[nn].set(timeCard.data['projects'][nn]['desc'])

# ========================= MAIN LOOP ==================================
mainloop()


