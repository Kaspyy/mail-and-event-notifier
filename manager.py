import time
import readEvent
import readEmail

while True:
   try:
      readEvent.main()
      readEmail.main()
      time.sleep(30)
   except:
      time.sleep(30)