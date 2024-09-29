
import log
from machine import Pin
from machine import I2C 
import utime as time

log.basicConfig(level=log.INFO)
i2c_log = log.getLogger("I2C")

ADDR_CM1103     =   0X48

REG_CONVERSION  =   0X00
REG_CONFIG      =   0X01
REG_THRESH_LO   =   0X02
REG_THRESH_HI   =   0X03


'''
note:The A0,A1,A2,A3 label on board didnot match the ADC chip's AINI0,AIN1,AIN2,AIN3 for batter layout
   | board label    |  CM1103 PIN
   |     A0         |      AIN3
   |     A1         |      AIN0
   |     A2         |      AIN1
   |     A3         |      AIN2
'''
A0  =  0
A1  =  1
A2  =  2
A3  =  3
mux_table = [0X07,0X04,0X05,0X06]

#first byte info in config register
BIT_OFFSET_OS   = 7
BIT_OFFSET_MUX  = 4
BIT_OFFSET_PGA  =   1
BIT_OFFSET_MODE =   0
#second byte info in config register
BIT_OFFSET_DR           =   5
BIT_OFFSET_COMP_MODE    =   4
BIT_OFFSET_POL          =   3
BIT_OFFSET_COMP_LAT     =   2
BIT_OFFSET_COMP_QUE     =   0

class OS:
    INVALID     = 0x00
    SINGLE_CONV = 0x01

class MUX:
    MUX_A0_A1   =   0x00
    MUX_A0_A3   =   0X01
    MUX_A1_A3   =   0X02
    MUX_A2_A3   =   0X03
    MUX_A0_GND  =   0X04
    MUX_A1_GND  =   0X05
    MUX_A2_GND  =   0X06
    MUX_A3_GND  =   0X07

class PGA:
    PGA_6144    =   0X00
    PGA_4096    =   0x01
    PGA_2048    =   0X02
    PGA_1024    =   0X03
    PGA_512     =   0X04
    PGA_256     =   0X05
    #PGA_256     =   0X06
    #PGA_256     =   0X07

class MODE:
    CONTINIOUS =   0X00
    SINGLE     =   0X01

class DR:
    DR_625  =   0X00
    DR_125  =   0X01
    DR_25   =   0X02
    DR_50   =   0X03
    DR_100  =   0X04
    DR_400  =   0X05
    DR_1000 =   0X06
    DR_2000 =   0X07

class COMP_MODE:
    NORMAL    =   0X00
    WINDOW    =   0X01

class COMP_POL:
    LOW        =   0X00
    HIGH       =   0X01

class COMP_LAT:
    ENABLE     =   0X01
    DISABLE    =   0X00

class COMP_QUE:
    SETUP1     =   0X00
    SETUP2     =   0X01
    SETUP4     =   0X02
    DISABLE    =   0X03

class CM1103():
    def __init__(self,i2c_obj):
        self._i2c = i2c_obj
        self._addr_reg_conversion = bytearray([REG_CONVERSION])
        self._addr_reg_config     = bytearray([REG_CONFIG])
        self._addr_reg_thresh_lo  = bytearray([REG_THRESH_LO])
        self._addr_reg_thresh_high= bytearray([REG_THRESH_HI])
        self._response = bytearray(2)

        self._convert           = None
        self._config            = None 
        self._lo_threshold      = None
        self._high_threshold    = None
        self._channel           = None

    @property
    def conversion(self):
        rsp = self._i2c.read(ADDR_CM1103,self._addr_reg_conversion,1,self._response,2,0) #reg address length is 1 and response datalength is 2 bytes
        if rsp==0:
            return self._response[0]*256+self._response[1]
        else:
            i2c_log.info("cm1103 read conversion register failed")
    
    @property
    def config(self):  # default value in this reg is :1000 0101 1000 0011
        rsp = self._i2c.read(ADDR_CM1103,self._addr_reg_config,1,self._response,2,0) #reg address length is 1 and response datalength is 2 bytes
        if rsp==0:
            self._config = self._response[0]*256+self._response[1] 
            return self._config
        else:
            i2c_log.error("cm1103 read config register failed")
           
    def write_config(self, os = OS.SINGLE_CONV, mux = MUX.MUX_A0_GND, pga = PGA.PGA_4096, mode = MODE.CONTINIOUS,
                     dr = DR.DR_100, comp_mode = COMP_MODE.WINDOW, comp_pol = COMP_POL.HIGH, comp_lat = COMP_LAT.DISABLE, comp_que = COMP_QUE.DISABLE):
        
        self._channel = mux #record the mux ad analogRead also need this info
        hsb = os<<BIT_OFFSET_OS|mux<<BIT_OFFSET_MUX|pga<<BIT_OFFSET_PGA|mode<<BIT_OFFSET_MODE
        lsb = dr<<BIT_OFFSET_DR|comp_mode<<BIT_OFFSET_COMP_MODE|comp_pol<<BIT_OFFSET_POL|comp_lat<<BIT_OFFSET_COMP_LAT|comp_que<<BIT_OFFSET_COMP_QUE
        config = bytearray([hsb,lsb])
        rsp = self._i2c.write(ADDR_CM1103,self._addr_reg_config,1,config,2)
        if rsp==0:
            return config
        else:
            i2c_log.error("cm1103 write config register failed")
            
    @property
    def lo_threshold(self):
        rsp = self._i2c.read(ADDR_CM1103,self._addr_reg_thresh_lo,1,self._response,2,0) #reg address length is 1 and response datalength is 2 bytes
        if rsp==0:
            return self._response[0]*256+self._response[1]

    @lo_threshold.setter
    def lo_threshold(self,val):
        pass 

    @property
    def high_threshold(self):
        rsp = self._i2c.read(ADDR_CM1103,self._addr_reg_thresh_high,1,self._response,2,0) #reg address length is 1 and response datalength is 2 bytes
        if rsp==0:
            return self._response[0]*256+self._response[1]
    
    @high_threshold.setter
    def high_threshold(self,val):
        pass
    
    #TODO,right now, this function only support single end ADC sample,A0,A1,A2,A3, which maps the physical feather board's pin map.
    def analogRead(self,ch):
        if ch<A0 and ch>A3:
            i2c_log.info("channel value is out of range, can only be between 0 and 3")
            return False
        if mux_table[ch]!= self._channel:
            self._channel = mux_table[ch]
            self.write_config(mux=self._channel)
        return self.conversion
    

if __name__=="__main__":

    #enable A0 to A3 
    analogSwitch = Pin(Pin.GPIO21,Pin.OUT,Pin.PULL_DISABLE,1)
    i2c_obj = I2C(I2C.I2C1, I2C.STANDARD_MODE)
    adc = CM1103(i2c_obj)
    adc.write_config(mode=MODE.CONTINIOUS,mux=MUX.MUX_A0_GND,pga=PGA.PGA_4096)
   
    retry =10
    while True:
        print(adc.analogRead(A3))
        time.sleep_ms(20)
        retry-=1
        if retry==0:
            break
    print("All done")  


