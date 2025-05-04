

from misc import PowerKey
import utime

'''
pk = PowerKey()

def pwk_callback(status):
    if status == 0:
        print('powerkey release.------------')
    elif status == 1:
    	print('powerkey press.--------------')
    else :
        print("WTF-------------")



if __name__=="__main__":
    if pk.powerKeyEventRegister(pwk_callback)==0: # 只有按键释放时才会触发回调
        print("pwk register succeed")
    retry = 20
    while retry:
        if pk.powerKeyEventRegister(pwk_callback)==0: # 只有按键释放时才会触发回调
            print("pwk register succeed")
        retry-=1
        utime.sleep(0.5)
        print("Hello world")
'''

from misc import PowerKey
import osTimer

class Pwrkey(object):
    def __init__(self, time_threshold):   
        self.pk = PowerKey()
        self.time_threshold = time_threshold
        self.timer = osTimer()
        self.is_long_press = 0
        self.pk.powerKeyEventRegister(self.pwk_callback)

    def long_press_cb(self):
        print('powerkey long press.')

    def short_press_cb(self):
        print('powerkey short press.')        

    def pwk_timer_cb(self, arg): 
        self.is_long_press = 1

    def pwk_callback(self, status):
        if status == 0:
            print('powerkey release.')
            self.timer.stop()
            if self.is_long_press:
                self.long_press_cb()
            else:
                self.short_press_cb()

        elif status == 1:
            print('powerkey press.')
            self.is_long_press = 0
            self.timer.start(self.time_threshold, 0, self.pwk_timer_cb)


if __name__ == "__main__":

    
    retry=10
    while retry:
        pwrkey = Pwrkey(1000)
        retry-=1
        utime.sleep(1)
