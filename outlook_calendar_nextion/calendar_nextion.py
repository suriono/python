import win32com.client, datetime, time, serial

# =================================================

class MySerial:
   ser = serial.Serial()
   
   def __init__(self, portcom):
      self.ser.port = portcom
   
   def serWrite(self, message):
      if self.ser.isOpen():
         time.sleep(1)
         try:
            self.ser.flushInput() #flush input buffer, discarding all its contents
            self.ser.flushOutput()
            time.sleep(0.5)
            self.ser.write(str.encode(message))  
         except Exception as e:
            print ("Error to write communication ...")
      else:
         print("Cannot open serial port")
   
   def serOpen(self):
      try: 
         self.ser.open()
      except Exception as e:
         print ("error open serial port: " , str(e))
         exit()
   
   def serClose(self):
      self.ser.close()
      time.sleep(1)
	  
# ========================================================

class MyOutlook:
   myApp = win32com.client.Dispatch("Outlook.Application")
   nameSpace = myApp.GetNamespace("MAPI")
   Appts = nameSpace.GetDefaultFolder(9).Items
   Appts.IncludeRecurrences = True
   Appts.Sort("[Start]")
   
   def convert_OutlookTime_to_ISO8601(self, outlooktime):
      timestr = outlooktime.strftime("%Y-%m-%d %H:%M:%S.%f")
      return datetime.datetime.strptime(timestr, '%Y-%m-%d %H:%M:%S.%f')
   
   
   def get_Appointment(self, checkstarttime):
      now    = datetime.datetime.now()
      nowtimestamp   = datetime.datetime.timestamp(now)
      begin  = checkstarttime.strftime("%m/%d/%Y %H:%M")
      oneweek= checkstarttime + datetime.timedelta(days=7)
      end    = oneweek.date().strftime("%m/%d/%Y")
      appts  = self.Appts.Restrict("[Start] >= '" +begin+ "' AND [END] <= '" +end+ "'")
     
      event1 = None
      event1start = 0
      event2 = None
      firsteventNotfound = True
      
      for a in appts:
         starttime = self.convert_OutlookTime_to_ISO8601(a.Start) # datetime.datetime.strptime(startstr, '%Y-%m-%d %H:%M:%S.%f')
         starttimestamp = datetime.datetime.timestamp(starttime)
         
         endtime = self.convert_OutlookTime_to_ISO8601(a.End) # datetime.datetime.strptime(startstr, '%Y-%m-%d %H:%M:%S.%f')
         endtimestamp = datetime.datetime.timestamp(endtime)
         
         #print(a.Start, a.End, a.Subject, a.BusyStatus,endtimestamp) #, a.Duration a.Organizer) # , a.End)
         # show appointment up to 10 minutes before it ends
         if nowtimestamp < (endtimestamp-600) and a.BusyStatus > 0:
            if firsteventNotfound:
               event1 = a
               event1start = starttimestamp
               event1end   = endtimestamp
               firsteventNotfound = False
            else:
               event2 = a
               return event1, event1start, event1end, a, starttimestamp
      return None

# =====================================


myOutlook = MyOutlook()
myserial = MySerial("COM10")   
myserial.serOpen()

counter = 0
while counter < 5:
  
   nowtime = datetime.datetime.now()
   todaymidnight = datetime.datetime(nowtime.year, nowtime.month, nowtime.day)

   event1, event1start, event1end, event2, event2start = myOutlook.get_Appointment(todaymidnight)
   
   print("   =========== First next or current appointment ===========")
   nexttime1 = int(event1start - datetime.datetime.timestamp(nowtime))
   time1end  = int(event1end   - datetime.datetime.timestamp(nowtime))
   print("Current appointment:", event1.Subject , event1.Location, " in", nexttime1, "seconds")
   
    
   print("   =========== After that the next appointment ===========")
   nexttime2 = int(event2start - datetime.datetime.timestamp(nowtime))
   print("After that appointment:", event2.Subject, event2.Location, " in", nexttime2, "seconds")
   
    # 1st appointment
   myserial.serWrite("1>" + event1.Subject + "<")
   # Delete the "SKY " in my particular case
   location = event1.Location.replace("SKY B1.2 ","").replace(" Room","")
   myserial.serWrite("2>" + location + "<")
   myserial.serWrite("3>" + str(nexttime1) + "<")
   myserial.serWrite("4>" + str(time1end)  + "<")
   
    
   # 2nd appointment after the 1st one
   myserial.serWrite("5>" + event2.Subject + "<")
   # Delete the "SKY " in my particular case
   location = event2.Location.replace("SKY B1.2 ","").replace(" Room","")
   myserial.serWrite("6>" + location + "<")
   myserial.serWrite("7>" + str(nexttime2) + "<")
   
   #myserial.serClose()
   #break
   
   time.sleep(6)
   counter = counter + 1
   
myserial.serClose()