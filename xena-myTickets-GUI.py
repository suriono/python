from bs4 import BeautifulSoup  # from pip install beautifulsoup4
from tkinter import *
import re
from selenium import webdriver

username = 'usman.suriono@skywatertechnology.com'
password = 'xxxxxxxx'

# ==============================================================================

class Xena_Parser:
   
   def __init__(self, username, password):
      self.username = username
      self.password = password
   
   def Find_Tickets(self):
      self.Open_Browser(False)
      self.myOpenTickets = []
      page_source = str(self.driver.page_source.encode('utf-8'))
      hparser = BeautifulSoup(page_source, 'html.parser')
      html = list(hparser.children)[1]
      body = list(html.children)[2]
      ptag = list(body.children)[1]
      taglist = ptag.find_all('a', class_="xena-title")
      self.myOpenTickets = []
      self.myOpenTicket_titles = []
      for tag in taglist:
         self.myOpenTickets.append(tag['href'])
         self.myOpenTicket_titles.append(tag.text)
      
   def Open_Browser(self, isheadless):
      if isheadless:
         chrome_options = webdriver.chrome.options.Options()
         chrome_options.add_argument("headless")
         chrome_options.add_argument("disable-gpu")
         self.driver = webdriver.Chrome('chromedriver', options=chrome_options)
      else:
         self.driver = webdriver.Chrome('chromedriver')
      
      self.driver.get('https://xena.skywatertechnology.com');
      page_source = str(self.driver.page_source.encode('utf-8'))

      # -------- password -----------
      search_box = self.driver.find_element_by_name('username')
      search_box.send_keys(self.username)
      search_box = self.driver.find_element_by_name('password')
      search_box.send_keys(self.password)
      search_box.submit()
      
   def Open_Ticket(self, ticketnumber):
      self.driver.get('https://xena.skywatertechnology.com' + str(ticketnumber));
  
   def Xena_Details(self, assigned_name):
      xenadetails = self.hparser.find_all('table', class_='xena-details')
      if re.search('State:</th><td>Closed</td>', str(xenadetails[0])):
         return False
      for eachlink in xenadetails[0].find_all('a'):
         if re.search("<a href=\"/account/user.*>" + assigned_name, str(eachlink)):
            return True
      return False
   
   def Quit(self):
      self.driver.quit()
      
# ==============================================================================

class GUI:
   
   def __init__(self):
      self.myTicket = Xena_Parser(username, password)
      
      self.master = Tk() 
      self.master.title("Xena My Tickets GUI by Usman Suriono, May 21 2022")
      topframe = Frame(self.master)
      topframe.pack(side=TOP, fill=X, padx=5, pady=5)
      botframe = Frame(self.master)
      botframe.pack(side=BOTTOM, fill=X, padx=5, pady=5)
      Button(topframe, text ="Find my tickets",  command = self.Find_Tickets_Button).pack(side=LEFT)
      Button(topframe, text ="CLOSE",  command = self.Close).pack(side=RIGHT)
      
      self.listTickets = Listbox(botframe, height=40, width=100)
      self.listTickets.pack(side=LEFT)
      scrollbar = Scrollbar(botframe)
      scrollbar.pack(side=RIGHT, fill=BOTH)
         
      self.listTickets.config(yscrollcommand = scrollbar.set)
      scrollbar.config(command = self.listTickets.yview) 
      self.listTickets.bind("<<ListboxSelect>>", self.listTicket_callback)
      
   def listTicket_callback(self,event):
      selection = event.widget.curselection()
      if selection:
         ticketindex = selection[0]
         ticketlink = self.myTicket.myOpenTickets[ticketindex]
         print("Select ticket: " , ticketlink, selection[0])
         self.myTicket.Open_Ticket(ticketlink)
      
   def Find_Tickets_Button(self):
      print("finding tickets, please wait ........")
      self.listTickets.delete(0,END)
     
      self.myTicket.Find_Tickets()
      for ticketno in self.myTicket.myOpenTicket_titles:
         self.listTickets.insert(END,ticketno)

   def Close(self):
      try:
         self.myTicket.Quit()
      except:
         pass
      self.master.destroy()
           
# ==============================================================================
XenaGUI = GUI()
# ========================= MAIN LOOP ==================================
mainloop()
      
