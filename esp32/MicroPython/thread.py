import _thread
import time
 
def testThread():
  while True:
    print("Hello from thread")
    time.sleep(2)
 
_thread.start_new_thread(testThread, ())
