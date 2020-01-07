#include "NexText.h"
#include "NexButton.h"
#include "NexNumber.h"

// Use by Nextion
SoftwareSerial HMISerial(10, 11);//RX,TX Change the nexConfig.h file otherwise Mega is required (Serial2)
NexText Tappt      = NexText  (0, 1, "tAppointment");
NexNumber Nleft    = NexNumber(0, 6, "nTimeLeft");
NexText Tloc       = NexText  (0, 3, "tLocation");
NexButton Bdismiss = NexButton(0, 4, "tDismiss");
char subject1[50];
char subject2[50];
char location1[50];
char location2[50];
long time1, time2, time1end;
boolean is_Dismiss = false;

NexTouch *nexListenList[] = 
{
    &Bdismiss,
    NULL
};

void b0PopCallback(void *ptr) {
  Tappt.setText("Dismissing ....");
  delay(2000);
  Tappt.setText(subject2);
  Tloc.setText(location2);
  Nleft.setValue(time2);

  // delay until the current appt ends
  unsigned long curtime = millis();
  while ( (millis() - curtime) < time1end*1000) {
    while (dbSerial.available()) {
      dbSerial.read();
    }
    // delay(time1end*1000); 
    delay(500);
  }
}

// ========================================

void setup() {
  dbSerial.begin(9600);
  nexInit();
  Bdismiss.attachPop(b0PopCallback, &Bdismiss);

  // Initial values for debugging
  Tappt.setText("Uz is not here yet");
  Tloc.setText("(somewhere)");
  Nleft.setValue(50);
}

void loop() {
  static String cstr;
  
  if (dbSerial.available()) {
    char head;
    char cc[100] = "";  
    byte index=0;
    char ce;
    bool startcc = false;
    while (dbSerial.available()) {
      ce = dbSerial.read();
      if (ce == '>') {  // beginning of the content
        cc[0] = '\0';
        cstr  = "";
        startcc = true;
      } else if (startcc) {
        if (ce == '<') {  // update the display
          switch (head) {
            case '1':                          // subject
              cstr.toCharArray(subject1, cstr.length()+1);  break; 
            case '2':                          // location
              cstr.toCharArray(location1, cstr.length()+1); break;
            case '3':                          // time
              time1 = atol(cc);   break; // time
            case '4':                          // time1 end
              time1end = atol(cc);   break; // time
            case '5':                          // subject
              cstr.toCharArray(subject2, cstr.length()+1);  break; 
            case '6':                          // location
              cstr.toCharArray(location2, cstr.length()+1); break;
            case '7':                          // time
              time2 = atol(cc);   break; // time
          }
          
        } else {
           cc[index++] = ce;
           cstr += ce;
        }
      } else if (!startcc) {
        head = ce;
      }
    }
    Tappt.setText(subject1);
    Tloc.setText(location1);
    Nleft.setValue(time1);           
  }
 
  nexLoop(nexListenList);
  delay(500);
}
