import time
import os,socket
from time import sleep
import mmap
import struct
import numpy as np
import pickle
import re
import random
import subprocess
import sys
import shlex
import math
from smbus2 import SMBus
from datetime import datetime

seq_file = "seq.pkl"
wav_file = "wav.pkl"
SEP='::'
obj= [0]*100
seq = [0]*100
gen =[0]*10
UDB=1000
UDM=6

class Error():

    def __init__(self):



        ##### valeurs entre 0 et 99
        self.Command=['Command error','Invalid character','Syntax error','Invalid separator','Data type error','GET not allowed','Parameter not allowed','Missing parameter','Command header error'
        ,'Header separator error','Program mnemonic too long','Undefined error','Header suffix out of range','Unexpected number of parameters','Numeric data error'
        ,'Invalid character in number','Exponent too large','Too many digits','Numeric data not allowed','Suffix error','Invalid suffix'
        ,'Suffix too long','Suffix not allowed','Character data error','Invalid character data'
        ,'Character data not allowed','String data error','Invalid string data','String data not allowed'
        ,'Block data error','Invalid block data','Block data not allowed','Expression error'
        ,'Invalid expression','Expression data not allowed','Macro error'
        ,'Invalid outside macro definition','Invalid inside macro definition','Macro parameter error']

        ##### valeurs entre 100 et 199
        self.Execution=['Execution error','Invalid while in local','Settings lost due to rtl','Command protected','Trigger error','Trigger ignored','Arm ignored','Init ignored','Trigger deadlock'
        ,'Arm deadlock','Parameter error','Settings conflict','Data out of range','Too much data','Illegal parameter value','Out of memory','Lists not same length','Data corrupt or stale'
        ,'Invalid format','Invalid version','Hardware error','Hardware missing','Mass storage error','Missing mass storage','Missing media','Corrupt media','Media full','Directory full'
        ,'File name not found','File name error','Media protected','Expression error','Math error in expression','Macro error','Macro syntax error','Macro execution error'
        ,'Illegal macro label','Macro parameter error','Macro definition too long','Macro recursion error','Macro redefinition not allowed'
        ,'Macro header not found','Program error','Cannot create program','Illegal program name','Program currently running','Program syntax error'
        ,'Program runtime error','Memory use error','Out of memory','Referenced name does not exist','Referenced name already exists']

        ##### valeurs entre 200 et 299
        self.Device=['Device-specific error','System error','Memory error','PUD memory lost','Calibration memory lost','Save/recall memory lost','Configuration memory lost','Storage fault'
        ,'Out of memory','Self-test failed','Calibration failed','Queue overflow','Communication error','Parity error in program message','Framing error in program message','Input buffer overrun'
        ,'Time out error']

        ##### valeurs entre 300 et 399
        self.Query=['Query error','Query INTERRUPTED','Query UNTERMINATED','Query DEADLOCKED','Query UNTERMINATED after indefinite response']

        Current=0
        self.List = []
        
    def Err_Add(self,_code_):

        self.List.append(_code_)

    def Err_Get(self,index):

        return self.List[index]


    def Err_Clear(self):

        self.List.clear()

    def Err_Insert(self,index,_code_):

        self.List.insert(index,_code_)

    def Err_Del(self,index):

        self.List.pop(index)

    def Err_GetSize(self):

        return len(self.List)


    def Err_Message(self,_code_):

        if abs(_code_)<99  :

            return self.Command[int(abs(_code_))]


        if abs(_code_)<199 and abs(_code_)>100  :

            return self.Execution[int(abs(_code_)-100)]

        if abs(_code_)<299 and abs(_code_)>200  :

            return self.Device[int(abs(_code_)-200)]

        if abs(_code_)<399 and abs(_code_)>300  :

            return self.Query[int(abs(_code_)-300)]

class FGenBase(Error):
    

    
    def __init__(self):
        
        self.chanName = ["ch1","ch2","ch12"]
        self.chanEnable =[True,True,True]
        self.ClockSrc=["internal","external"]
        self.ClockVal=0
        Error.__init__(self)
        
    def set_ChName(self, chan,chanName):
        
        if(int(chan)==1 or int(chan)==2) : 
            
            self.chanName[int(chan)-1]=chanName
        else :
            self.Err_Add(102)
 
        
    def get_ChName(self,chan):
        
        if(int(chan)==1 or int(chan)==2) :        
            
            return self.chanName[int(chan)-1]
        else :
            self.Err_Add(102)            
             
        
    def set_ChEnable(self,chanName,chanEnable):
        
         
        try:
            index=self.chanName.index(chanName)
        except ValueError:
            self.Err_Add(102)
        else :
            
            if(int(chanEnable)==0 or int(chanEnable)==1) :

                self.chanEnable[self.chanName.index(chanName)]=int(chanEnable)
        
            else :

                self.Err_Add(102)
         
        
    def get_ChEnable(self,chanName):
        
        try:
            index=self.chanName.index(chanName)
        except ValueError:
            self.Err_Add(102)
        else :
            
            return self.chanEnable[self.chanName.index(chanName)]
    
     
    def set_RefClock(self,ClkVal):
        
                 
        if (float(ClkVal) <=500000000) and (float(ClkVal) > 0) :
            self.ClockVal=float(ClkVal)
        else : 
            self.Err_Add(102)
        
                
    def get_RefClockValue(self):
        
       
        return self.ClockVal


class StdFunc(FGenBase):
    
    def __init__(self):
        
        self.ChanStartFreq =[0.0,0.0,0.0,0.0]
        self.ChanStopFreq = [0.0,0.0,0.0,0.0]
        self.ChanPhase = [0.0,0.0,0.0,0.0]
        self.ChanAmplitude = [0.0,0.0,0.0,0.0]
        self.ChanDuration = [0.0,0.0,0.0,0.0]
        
        self.MRRC = [0,0,0,0]
        self.MDFW = [0,0,0,0]
        
        
        FGenBase.__init__(self)
        
    def set_ChStartFrequency(self,chanName,chanFrequency):
        
        
        try:
            index=self.chanName.index(chanName)
            
        except ValueError:
            self.Err_Add(102)
        else :

            if (float(chanFrequency) <= 2**31) and (float(chanFrequency) >0) :

                self.ChanStartFreq[self.chanName.index(chanName)]=float(chanFrequency)

            else :

                self.Err_Add(102)

        
        
    def get_ChStartFrequency(self,chanName):
        


        try:
            index=self.chanName.index(chanName)
        except ValueError:
            self.Err_Add(102)
        else :
            
            return self.ChanStartFreq[self.chanName.index(chanName)]

    
    def set_ChStartPhase(self,chanName,chanPhase):
        

        try:
            index=self.chanName.index(chanName)
        except ValueError:
            self.Err_Add(102)
        else :

            if (float(chanPhase) <= 360) and (float(chanPhase) > 0) :

                self.ChanPhase[self.chanName.index(chanName)]=float(chanPhase)
                
            else :

                self.Err_Add(102)

                
    def get_ChStartPhase(self,chanName):
        
  
        try:
            index=self.chanName.index(chanName)
        except ValueError:
            self.Err_Add(102)
        else :
           
            return self.ChanPhase[self.chanName.index(chanName)]

 
    def set_ChAmplitude(self,chanName,chanAmplitude):
        
        self.ChanAmplitude[self.chanName.index(chanName)]=float(chanAmplitude)
                
    def get_ChAmplitude(self,chanName):
        
        
        return self.ChanAmplitude[self.chanName.index(chanName)]

class Wfm(StdFunc):
    
    def __init__(self):
            
        StdFunc.__init__(self)
        self.SweepMode=["Single","Sweep"]
        self.chanMode = ["Single","Single","Single"]
        self.Modif=0        
    
      
    def set_ChStopFrequency(self,chanName,chanFrequency):
        

        try:
            index=self.chanName.index(chanName)
        except ValueError:
            self.Err_Add(102)
        else :

            if (float(chanFrequency) <= 2**31) and (float(chanFrequency) >0) :

                self.ChanStopFreq[self.chanName.index(chanName)]=float(chanFrequency)

            else :

                self.Err_Add(102)
        
    def get_ChStopFrequency(self,chanName):
        

        try:
            index=self.chanName.index(chanName)
        except ValueError:
            self.Err_Add(102)
        else :
            
            return self.ChanStopFreq[self.chanName.index(chanName)]
        
        
    def set_ChDuration(self,chanName,chanDuration):
        

        try:
            index=self.chanName.index(chanName)
        except ValueError:
            self.Err_Add(102)
        else :

            if (float(chanDuration) <= 2**31) and (float(chanDuration) > 0) :

                self.ChanDuration[self.chanName.index(chanName)]=float(chanDuration)

            else :

                self.Err_Add(102)
        
    def get_ChDuration(self,chanName):

        return self.ChanDuration[self.chanName.index(chanName)]
        #try:
            #index=self.chanName.index(chanName)
        #except ValueError:
            #self.Err_Add(102)
        #else :
            
            #return self.ChanDuration[self.chanName.index(chanName)] 
        
    def set_ChRRC(self,chanName,_RSRR_):


        try:
            index=self.chanName.index(chanName)
        except ValueError:
            self.Err_Add(102)
        else :

            if (int(_RSRR_) < 2**20) and (int(_RSRR_) > 0) :

                
                self.MRRC[self.chanName.index(chanName)]=int(_RSRR_)

            else :

                self.Err_Add(102)


    def set_ChDFW(self,chanName,_RDW_):


        try:
            index=self.chanName.index(chanName)
        except ValueError:
            self.Err_Add(102)
        else :

            if (int(_RDW_) < 2**48) and (int(_RDW_) > 0) :

                
                self.MDFW[self.chanName.index(chanName)]=int(_RDW_)

            else :

                self.Err_Add(102)


    def get_ChRRC(self,chanName):

        try:
            index=self.chanName.index(chanName)
        except ValueError:
            self.Err_Add(102)
        else :
            
            return self.MRRC[self.chanName.index(chanName)]


    def get_ChDFW(self,chanName):

        try:
            index=self.chanName.index(chanName)
        except ValueError:
            self.Err_Add(102)
        else :
        
            return self.MDFW[self.chanName.index(chanName)]

    
    def set_ChMode(self,chanName,Mode):
        
        try:
            index=self.SweepMode.index(Mode) #and index2=self.chanName.index(chanName) 
        except ValueError:
            self.Err_Add(102)
        else :
           
            self.chanMode[self.chanName.index(chanName)]=Mode
       
    
    def get_ChMode(self,Name):
        
        return  self.chanMode[self.chanName.index(Name)]

class Seq(Error) : 
    
    def __init__(self):
    
        Error.__init__(self)
        #Wfm.__init__(self)
        Current=0
        self.List = []
        self.Active=0

    
    
    def Seq_Add(self,obj):
    
        self.List.append(obj)
        
    def Seq_Get(self,index):
  
        if (index < len(self.List)) and  (index >=0) :

            return self.List[index]

        else :

            self.Err_Add(102)

    def Seq_Clear(self):
        
        self.List.clear()
    
    def Seq_Insert(self,index,obj):
        
        if (index < len(self.List)) and  (index >=0) :

            self.List.insert(index,obj)

        else :

            self.Err_Add(102)

        
    def Seq_Del(self,index):
        
        if (index < len(self.List)) and  (index >=0) :

            self.List.pop(index)

        else :

            self.Err_Add(102)

        
    def Seq_GetSize(self):
        
        return len(self.List)

    
           
    def Seq_Save(self,_FName_):  
        
        try:
            with open(_FName_,'wb') as f: 
                pickle.dump(self.List, f)
        
        except ValueError:
            self.Err_Add(102)
       
    
    def Seq_Read(self,_FName_):  
        
        try:
            with open(_FName_,'rb') as f:
                self.List.clear()
                self.List = pickle.load(f)
                
        except ValueError:
            self.Err_Add(102)


class Gen (Seq): 
    
    def __init__(self):
        
        #Error.__init__(self)
        Seq.__init__(self)
        
        self.temp = [0]*10
        self.POWER=["On","Off"]
        self.POWER_MODE='On'
        self.SOFT=0
        self.TTL=1
        self.IP_RAZ=2
        self.QSPI=3
        self.UPDT=4
        self.UPDT_SOFT=5
        self.DDS_RAZ=7
        self.DDS_RAZ_SOFT=8
        self.TTL_SOFT=9
        self.TXB_ON=10
        self.DDS_POWER_OFF=11
        self.READWRITE=12
        self.IPRAZ=13
        self.TTLTRIG=14
        self.SYNCCRTL=15
        self.SYNCRESET=16
        self.COUNT_STEP=32
        self.Trig=["Up","Down"]
        self.TrigMode='Up'
        self.UPDT_DURATION=64
        self.v0=0
        self.spi_clk=0
        self.updt_clk=0
        self.NbPts=0
        self.Sign1=0
        self.Sign2=0
        self.Sign=0
        self.Mem_Offset=0
        self.Optimize=["On","Off"]
        self.Optimize_Mode='On'
        self.SPI=["Spi","Qspi"]
        self.UPD=["external","internal"]
        self.UPD_Mode='internal'
        self.SPI_Mode='Spi'
        self.MemAccess=["Rd","Wr"]# registres de la DDS
        self.MemAccess_Mode='Wr'
              
        self.PAR1=0x0
        self.PAR2=0x0
        self.FTW1=0x00
        self.FTW2=0x00
        self.SDFW=0x0
        self.UC=0
        self.SRRC=0
        self.CR=0x00000100
        self.OSKM=0
        self.OSKRR=0
        self.CDAC=0
        self.COUNT=0
        self.cfg_offset= 0x60000000 
        self.axi_bram_reader=0x43C10000
        self.axi_bram_writer=0x43C00000
    
    def IP_Reset(self):
    
        fd0=os.open('/dev/mem',os.O_RDWR)
        cfg0=mmap.mmap(fileno=fd0,length=mmap.PAGESIZE,offset=self.cfg_offset)
        
        self.v0=struct.unpack("<L",cfg0[0:4])[0]
        self.v0= self.v0 & ~(1<< self.IPRAZ)
        cfg0[0:4]=struct.pack("L",self.v0)
        sleep(0.01)
        self.v0= self.v0 | (1 << self.IPRAZ)
        cfg0[0:4]=struct.pack("L",self.v0)
        sleep(0.01)
        self.v0= self.v0 & ~(1<< self.IPRAZ)
        cfg0[0:4]=struct.pack("L",self.v0)
        sleep(0.01)
        
        os.close(fd0)
    
    
    
    
    ###############################################################################
    # prends le controle du bus et effectue un reset de la DDS 
    # TXB_ON : active les drivers de bus de la carte
    # DDS_RAZ_SOFT :  aiguille le switch et envoie raz soft et non IP sur raz DDS bit 
    # DDS_RAZ : effectue un pulse sur le bit 7  du registre cfg0
    ###############################################################################

    def Reset(self):

        self.set_TXB(0)
        
        fd0=os.open('/dev/mem',os.O_RDWR)
        cfg0=mmap.mmap(fileno=fd0,length=mmap.PAGESIZE,offset=self.cfg_offset)
        
        self.v0=struct.unpack("<L",cfg0[0:4])[0]
        
        self.v0= self.v0 & ~(1<< self.DDS_RAZ)
        self.v0= self.v0 | (1 << self.DDS_RAZ_SOFT)
        
        cfg0[0:4]=struct.pack("L",self.v0)
       
        sleep(0.01)
        self.v0= self.v0 | (1 << self.DDS_RAZ)
        self.v0= self.v0 | (1 <<  self.DDS_RAZ_SOFT)
        
        cfg0[0:4]=struct.pack("L",self.v0)
        
        sleep(0.01)
        self.v0= self.v0 & ~(1<< self.DDS_RAZ)
        
        self.v0= self.v0 & ~(1 <<  self.DDS_RAZ_SOFT)
        cfg0[0:4]=struct.pack("L",self.v0)
        
        sleep(0.01)
        
        os.close(fd0)
        
        self.SPI_Mode ='Spi'
        
        




   
    
    def Run(self):
    
        fd0=os.open('/dev/mem',os.O_RDWR)
        cfg0=mmap.mmap(fileno=fd0,length=mmap.PAGESIZE,offset=self.cfg_offset)
        
        self.v0=struct.unpack("<L",cfg0[0:4])[0]
        
        self.v0= self.v0 & ~(1 << self.TTL)
        self.v0= self.v0  | (1 << self.TTL_SOFT)   
        cfg0[0:4]=struct.pack("L",self.v0)
        #sleep(0.01)
        self.v0= self.v0 | (1 << self.TTL) | (1 << self.TTL_SOFT)  
        cfg0[0:4]=struct.pack("L",self.v0)
        #sleep(0.01)
        self.v0= self.v0 & ~(1 << self.TTL)
        self.v0= self.v0 & ~(1 << self.TTL_SOFT)
        
        cfg0[0:4]=struct.pack("L",self.v0)
        #sleep(0.01)
    
        os.close(fd0)
    
    
    
    
    def Run2(self):
    
        fd0=os.open('/dev/mem',os.O_RDWR)
        cfg0=mmap.mmap(fileno=fd0,length=mmap.PAGESIZE,offset=self.cfg_offset)
        
        self.v0=struct.unpack("<L",cfg0[0:4])[0]
        self.v0= self.v0 & ~(1 << self.TTL_SOFT)
        self.v0= self.v0 & ~(1 << self.SOFT)
        
        cfg0[0:4]=struct.pack("L",self.v0)
        
        sleep(0.01)
        self.v0= self.v0 | (1 << self.SOFT)
        
        cfg0[0:4]=struct.pack("L",self.v0)
       
        sleep(0.01)
        self.v0= self.v0 & ~(1 << self.SOFT)
        self.v0= self.v0 & ~(1 << self.TTL_SOFT)
        
              
       
        cfg0[0:4]=struct.pack("L",self.v0)
        
        sleep(0.01)
    
        os.close(fd0)
    
    ###############################################################################
    # prends le controle du bus et effectue un update soft de la DDS 
    # TXB_ON : active les drivers de bus de la carte
    # UPDT_SOFT : aiguille le switch et envoie updt soft et non IP sur updt de la DDS 
    # UPDT : effectue un pulse sur le bit 4  du registre cfg0
    ###############################################################################
       
    
    def Update(self):


        self.set_TXB(1)

    
        fd0=os.open('/dev/mem',os.O_RDWR)
        cfg0=mmap.mmap(fileno=fd0,length=mmap.PAGESIZE,offset=self.cfg_offset)
        
        self.v0=struct.unpack("<L",cfg0[0:4])[0]
        
        self.v0= self.v0  & ~ (1<<self.UPDT)
        self.v0= self.v0 | (1 << self.UPDT_SOFT)
        
        cfg0[0:4]=struct.pack("L",self.v0)
        
        sleep(0.01)
        self.v0= self.v0 | (1 << self.UPDT)
        self.v0= self.v0 | (1 << self.UPDT_SOFT)
       
        cfg0[0:4]=struct.pack("L",self.v0)
        
        sleep(0.01)
        self.v0= self.v0 & ~(1 << self.UPDT_SOFT)
        
        self.v0= self.v0 & ~(1<< self.UPDT)
        cfg0[0:4]=struct.pack("L",self.v0)
        
        sleep(0.01)

        self.set_TXB(0)

        
        os.close(fd0)

   


    ###############################################################################
    # mets en veille ou en fonctionnement la puce DDS 
    # TXB_ON : active les drivers de bus de la carte
    # DDS_POWER_OFF : niveau 0 ou 1  sur le bit 11 du registre cfg0
    ###############################################################################


    def set_PowerUp(self,power):
            
        fd0=os.open('/dev/mem',os.O_RDWR)
        cfg0=mmap.mmap(fileno=fd0,length=mmap.PAGESIZE,offset=self.cfg_offset)
       
        self.v0=struct.unpack("<L",cfg0[0:4])[0]
    
    
        try:
            index=self.POWER.index(power)
        except ValueError:
             self.Err_Add(102)
    
        else :
            self.POWER_MODE =power
        
        if self.POWER_MODE=='On':
            
             self.v0= self.v0 & ~(1 << self.DDS_POWER_OFF)  
        else :
            
            self.v0= self.v0 | (1 << self.DDS_POWER_OFF) 
         
        cfg0[0:4]=struct.pack("L",self.v0)
        
        sleep(0.01)
        
        os.close(fd0)
        
        
        
    def get_Power(self):
            
        return self.POWER_MODE
        


    def set_UpdateCtrl(self,mode):
            
        fd0=os.open('/dev/mem',os.O_RDWR)
        cfg0=mmap.mmap(fileno=fd0,length=mmap.PAGESIZE,offset=self.cfg_offset)
       
        self.v0=struct.unpack("<L",cfg0[0:4])[0]
            
        if int(mode)==1:
            
             self.v0= self.v0 & ~(1 << self.UPDTCRTL)  
        else :
            
            self.v0= self.v0 | (1 << self.UPDTCRTL) 
         
        cfg0[0:4]=struct.pack("L",self.v0)
        
        sleep(0.01)
        
        os.close(fd0)
        


        
    ###############################################################################
    # fixe le rapport de division de l'horloge du protocole spi 
    # cfg0[15:19] : valeur sur 32 bits 
    ###############################################################################


    def set_SpiClock(self,clock):
        
        if (int(clock) <=2**31) and (int(clock) >0):
        
            fd0=os.open('/dev/mem',os.O_RDWR)
            cfg0=mmap.mmap(fileno=fd0,length=mmap.PAGESIZE,offset=self.cfg_offset)
            self.spi_clk=clock
            cfg0[12:16]=struct.pack("L",self.spi_clk)
            sleep(0.01)
        
            os.close(fd0)

        else :
 
            self.Err_Add(102)        

    ###############################################################################
    # renvoie le rapport de division de l'horloge du protocole spi 
    ###############################################################################  

    def get_SpiClock(self):
        
        
        fd0=os.open('/dev/mem',os.O_RDWR)
        cfg0=mmap.mmap(fileno=fd0,length=mmap.PAGESIZE,offset=self.cfg_offset)
        return struct.unpack("<L",cfg0[12:16])[0]
        sleep(0.01)
        os.close(fd0)
        
     
        
    def set_UpdtClock(self,clock):

        if (int(clock) <=2**31) and (int(clock) >=10):
        
            fd0=os.open('/dev/mem',os.O_RDWR)
            cfg0=mmap.mmap(fileno=fd0,length=mmap.PAGESIZE,offset=self.cfg_offset)
            self.updt_clk=clock
            cfg0[8:12]=struct.pack("L",self.updt_clk)
            sleep(0.01)
            os.close(fd0)

        else :

            self.Err_Add(102)

    
        
    def get_UpdtClock(self):
        
        fd0=os.open('/dev/mem',os.O_RDWR)
        cfg0=mmap.mmap(fileno=fd0,length=mmap.PAGESIZE,offset=self.cfg_offset)
        return struct.unpack("<L",cfg0[8:12])[0]
        sleep(0.01)
        os.close(fd0)
    
        
    
    
    def set_UpdtDelay(self,clock):

        if (int(clock) <=2**31) and (int(clock) >0):

            fd0=os.open('/dev/mem',os.O_RDWR)
            cfg0=mmap.mmap(fileno=fd0,length=mmap.PAGESIZE,offset=self.cfg_offset)
            self.updt_clk=clock
            cfg0[4:8]=struct.pack("L",self.updt_clk)
            sleep(0.01)
            os.close(fd0)

        else :

            self.Err_Add(102)

    
    def set_SYNC(self,clock):

        if (int(clock) <=2**31) and (int(clock) >0):
            
            fd0=os.open('/dev/mem',os.O_RDWR)
            cfg0=mmap.mmap(fileno=fd0,length=mmap.PAGESIZE,offset=self.cfg_offset)
            cfg0[16:20]=struct.pack("L",int(clock))
            sleep(0.01)
            os.close(fd0)

        else :

            self.Err_Add(102)

    def set_SYNCCRTL(self,ctrl):

        if (int(ctrl) <2 and int(ctrl) >=0):
            
            fd0=os.open('/dev/mem',os.O_RDWR)
            cfg0=mmap.mmap(fileno=fd0,length=mmap.PAGESIZE,offset=self.cfg_offset)
       
            self.v0=struct.unpack("<L",cfg0[0:4])[0]
            
            if int(ctrl)==0:
            
                 self.v0= self.v0 & ~(1 << self.SYNCCRTL)
            else :
            
                self.v0= self.v0 | (1 << self.SYNCCRTL) 
         
            cfg0[0:4]=struct.pack("L",self.v0)
        
            sleep(0.01)

        else :

            self.Err_Add(102)  
            
    def set_SYNCReset(self,ctrl):        
        
        if (int(ctrl) <2 and int(ctrl) >=0):
            
            fd0=os.open('/dev/mem',os.O_RDWR)
            cfg0=mmap.mmap(fileno=fd0,length=mmap.PAGESIZE,offset=self.cfg_offset)
       
            self.v0=struct.unpack("<L",cfg0[0:4])[0]
            
            if int(ctrl)==0:
            
                 self.v0= self.v0 & ~(1 << self.SYNCRESET)
            else :
            
                self.v0= self.v0 | (1 << self.SYNCRESET) 
         
            cfg0[0:4]=struct.pack("L",self.v0)
        
            sleep(0.01)

        else :

            self.Err_Add(102)
        
        
        
        
    def get_UpdtDelay(self):
        
        fd0=os.open('/dev/mem',os.O_RDWR)
        cfg0=mmap.mmap(fileno=fd0,length=mmap.PAGESIZE,offset=self.cfg_offset)
        return struct.unpack("<L",cfg0[4:8])[0]
        sleep(0.01)
        os.close(fd0)
    

    def set_TXB(self,_state_):

        """Documentation for a function.
 
        More details.
        """
        
        fd0=os.open('/dev/mem',os.O_RDWR)
        cfg0=mmap.mmap(fileno=fd0,length=mmap.PAGESIZE,offset=self.cfg_offset)
        self.v0=struct.unpack("<L",cfg0[0:4])[0]
        if (int(_state_) <2 and int(_state_) >=0):
        
            if (int(_state_)==0):
                self.v0= self.v0 & ~(1 << self.TXB_ON)
            if (int(_state_)==1): 
                self.v0= self.v0 | (1 << self.TXB_ON)
        
            cfg0[0:4]=struct.pack("L",self.v0)
            sleep(0.01)
            os.close(fd0)

        else :

            self.Err_Add(102)    
    
    
    
    
    
          
    def set_Optimize_Mode(self,opt):
    
           
        try:
            index=self.Optimize.index(opt)
        except ValueError:
            self.Err_Add(102)
    
        else :
            self.Optimize_Mode=opt
        
    
 
    
    def get_Optimize_Mode(self):
        
        return self.Optimize_Mode
    
    
    
   
    
    
    def Set_Memory_Access(self,mode): 
        
        fd0=os.open('/dev/mem',os.O_RDWR)
        cfg0=mmap.mmap(fileno=fd0,length=mmap.PAGESIZE,offset=self.cfg_offset)
       
        self.v0=struct.unpack("<L",cfg0[0:4])[0]
    
    
        try:
            index=self.MemAccess.index(mode)
        except ValueError:
            self.Err_Add(102)
    
        else :
            self.MemAccess_Mode =mode
        
        if self.MemAccess_Mode=='Wr':
            
            self.v0= self.v0 & ~(1 << self.READWRITE)
            
            cfg0[0:4]=struct.pack("L",self.v0)
        else :
            
            self.v0= self.v0 | (1 << self.READWRITE)
            
            cfg0[0:4]=struct.pack("L",self.v0)
         
        
        
        sleep(0.01)
        os.close(fd0)    
        
    
    ###############################################################################
    # pilote le BRAM switch pour un lecture ou ecriture dans la bram
    ######################################################################### 
    
    
    def Get_Memory_Access(self): 
    
        return self.MemAccess_Mode
    
    
	###############################################################################
    # envoi d'une simple frequence
    ###############################################################################
    
    def set_Freq(self,opt,opt1,opt2,opt3,opt4):
	
        
        tmp=seq[0].Seq_Get(int(opt))


        self.Calc_Ramp(tmp.get_ChStartFrequency(tmp.get_ChName(1)),tmp.get_ChStopFrequency(tmp.get_ChName(1)),tmp.get_ChDuration(tmp.get_ChName(1)),tmp.get_RefClockValue(),tmp.get_ChMode(tmp.get_ChName(1)),tmp.get_ChDFW(tmp.get_ChName(1)),tmp.get_ChRRC(tmp.get_ChName(1)))
        self.Sign1=self.Sign

        self.RAM_Write(0, 0xC040002 | (self.Sign1 << 16))
        self.RAM_Write(1, 300000000)
        self.RAM_Write(2, 0)
        self.RAM_Write(3, 0)

        self.RAM_Write(4, 0xC040003 | (self.Sign1 << 16))
        self.RAM_Write(5,9000000000)
        self.RAM_Write(6,0)
        self.RAM_Write(7, 0)

        self.RAM_Write(8,0xC040004 | (self.Sign1 << 16) )
        #self.RAM_Write(9,int(opt2)>>16)
        #self.RAM_Write(10, (int(opt2)-(( int(opt2) >>16)<<16)))
        self.RAM_Write(9, 0x1)
        self.RAM_Write(10,0x0000)
        self.RAM_Write(11,0)
        print(hex(self.RAM_Read(10)))

        self.RAM_Write(12,0x6040006 | (self.Sign1 <<16))
        self.RAM_Write(13,int(opt3)<<8)
        self.RAM_Write(14,0)
        self.RAM_Write(15,0)



        self.RAM_Write(16,0x4040008 | (self.Sign1 <<16))
        self.RAM_Write(17,int(0xFFFF)<<16)
        self.RAM_Write(18,0)
        self.RAM_Write(19,0)

        self.CR = self.CR & ~ (3 << 9)
        self.CR=self.CR | 3 << 9 #ramped FSK
        self.CR = self.CR | (1 << 8)  # internal update

        self.RAM_Write(20,0x8040007 | (self.Sign1 <<16)) ####registre CSR
        self.RAM_Write(21,int(self.CR))
        self.RAM_Write(22,0)
        self.RAM_Write(23,0)

        self.RAM_Write(24, 0x100000)


        self.Run2()

        time.sleep(4)

        self.RAM_Write(0, 0xC040002 | (self.Sign1 << 16))
        self.RAM_Write(1, 600000000)
        self.RAM_Write(2,0)
        self.RAM_Write(3, 0)

        self.RAM_Write(4, 0x100000)

        self.Run2()

        #self.CR = self.CR & ~ (3 << 9)
        #self.CR = self.CR | 0 << 9  # ramped FSK
        #self.CR = self.CR | (1 << 8)  # internal update
        #self.CR = self.CR & ~ (1 << 15)  # ACC1

        #self.RAM_Write(0, 0x8040007 | (self.Sign1 << 16))  ####registre CSR
        #self.RAM_Write(1, int(self.CR))
        #self.RAM_Write(2, 0)
        #self.RAM_Write(3, 0)

        #self.RAM_Write(4, 0x100000)

        #self.Run2()

        #self.CR = self.CR & ~ (3 << 9)
        #self.CR = self.CR | 3 << 9  # ramped FSK
        #self.CR = self.CR | (1 << 8)  # internal update
        #self.CR = self.CR & ~ (1 << 15)  # ACC1

        #self.RAM_Write(0, 0x8040007 | (self.Sign1 << 16))  ####registre CSR
        #self.RAM_Write(1, int(self.CR))
        #self.RAM_Write(2, 0)
        #self.RAM_Write(3, 0)

        #self.RAM_Write(4, 0x100000)

        #self.Run2()



        self.CR = self.CR & ~ (3 << 9)
        self.CR = self.CR | 3 << 9  # ramped FSK
        self.CR = self.CR | (1 << 8)  # internal update
        self.CR = self.CR | (1 << 14)  # ACC2

        self.RAM_Write(0, 0x8040007 | (self.Sign1 << 16))  ####registre CSR
        self.RAM_Write(1, int(self.CR))
        self.RAM_Write(2, 0)
        self.RAM_Write(3, 0)

        self.RAM_Write(4, 0x100000)

        self.Run2()

        self.CR = self.CR & ~ (3 << 9)
        self.CR = self.CR | 3 << 9  # ramped FSK
        self.CR = self.CR | (1 << 8)  # internal update
        self.CR = self.CR & ~ (1 << 14)  # ACC2

        self.RAM_Write(0, 0x8040007 | (self.Sign1 << 16))  ####registre CSR
        self.RAM_Write(1, int(self.CR))
        self.RAM_Write(2, 0)
        self.RAM_Write(3, 0)

        self.RAM_Write(4, 0x100000)

        self.Run2()

    ###############################################################################
    # update interne ou externe
    ###############################################################################
    
    def set_UPDT_Mode(self,opt):
	
        try:
            index=self.UPD.index(opt)
        except ValueError:
            self.Err_Add(102)
        else :
		
            if self.get_UPDT_Mode()!=opt :
                self.UPD_Mode =opt
                bus = SMBus(0)
                #bus.write_byte_data(0x41, 3, 0)

                if (self.UPD_Mode=='internal'):
                    self.CR=self.CR | (1 << 8)
                    self.CR=self.CR | (1 << 21) # bypass PLL
                else :
                    self.CR=self.CR & ~(1 << 8)
                    self.CR=self.CR | (1 << 21) # bypass PLL  
                
                ##################################################
                # on sauvegarde ce qui est au debut de la RAM
                ##################################################
        
                for i in range(10):
        
                    self.temp[i]= self.RAM_Read(i)		
	
                self.RAM_Write(0,0x8040007 ) ####registre CSR    
                self.RAM_Write(1,int(self.CR))  
                self.RAM_Write(2,0)
                self.RAM_Write(3,0)
               
                self.RAM_Write(4,0x100000)
                
                if (self.UPD_Mode=='internal'):
                    
                    
                    self.Run2()
                    sleep(0.16)
                    self.Update()                    
                    bus.write_byte_data(0x41, 0x1, 0)
                    
                else :
                    
                    
                    self.Run2()
                    sleep(0.16)
                    bus.write_byte_data(0x41, 0x1, 4)
				
                ##################################################
                # on restaure ce qui est au debut de la RAM
                ##################################################
        
                for i in range(10):
        
                    self.RAM_Write(i, self.temp[i])
					
                bus.close()
				
    ###############################################################################
    # renvoie le mode update 
    ############################################################################### 
    
    def get_UPDT_Mode(self): 
            
        return  self.UPD_Mode				
				
				
    ###############################################################################
    # active ou pas le protocole QSPI
    ############################################################################### 
    
          
    def set_QSPI_Mode(self,opt):
    
        
       
        try:
            index=self.SPI.index(opt)
        except ValueError:
            self.Err_Add(102)
    
        else :
            if self.get_QSPI_Mode()!=opt :
                self.SPI_Mode =opt
				
         
        
        
        fd0=os.open('/dev/mem',os.O_RDWR)
        cfg0=mmap.mmap(fileno=fd0,length=mmap.PAGESIZE,offset=self.cfg_offset)
       
        self.v0=struct.unpack("<L",cfg0[0:4])[0]
        
        if  self.SPI_Mode =='Qspi':
            
            self.v0= self.v0 | (1 << self.QSPI) 
            cfg0[0:4]=struct.pack("L",self.v0)
        else : 
            
            self.v0= self.v0 & ~(1 << self.QSPI) 
            cfg0[0:4]=struct.pack("L",self.v0)
        
        
        sleep(0.01)
        os.close(fd0)
       
       
            
    
    ###############################################################################
    # renvoie le mode QSPI 
    ############################################################################### 
    
    def get_QSPI_Mode(self): 
            
        return  self.SPI_Mode



    ###############################################################################
    # determine si trig sur front montant (1) ou descendant (0)
    ###############################################################################
    

    def set_Trig_Mode(self,mode) : 

        if mode=='Up' or mode=='Down' : 

            self.TrigMode = mode

        fd0=os.open('/dev/mem',os.O_RDWR)
        cfg0=mmap.mmap(fileno=fd0,length=mmap.PAGESIZE,offset=self.cfg_offset)

        self.v0=struct.unpack("<L",cfg0[0:4])[0]

        if  self.TrigMode =='Up':

            self.v0= self.v0 | (1 << self.TTLTRIG) 
            cfg0[0:4]=struct.pack("L",self.v0)
        else :

            self.v0= self.v0 & ~(1 << self.TTLTRIG) 
            cfg0[0:4]=struct.pack("L",self.v0)


        sleep(0.01)
        os.close(fd0)

 

    def Get_Trig_Mode(self) :

        return self.TrigMode



    
    
    def RAM_Write(self,addr,val):
    
        self.Set_Memory_Access('Wr')
        fd0=os.open('/dev/mem',os.O_RDWR | os.O_SYNC)
        ram0=mmap.mmap(fileno=fd0,length=mmap.PAGESIZE,offset=self.axi_bram_writer)
        
        ram0[(int(addr)*4)+16:(int(addr)*4)+4+16]=struct.pack("L", int(val))
        #sleep(0.01)
        os.close(fd0) 
        
    
    
    def RAM_Read(self,addr):
        
        self.Set_Memory_Access('Rd')
        fd0=os.open('/dev/mem',os.O_RDWR | os.O_SYNC)
        ram0=mmap.mmap(fileno=fd0,length=mmap.PAGESIZE,offset=self.axi_bram_reader)
        struct.unpack("<L", ram0[int(addr+3)*4:(int(addr+3)*4)+4])[0]
        return struct.unpack("<L", ram0[(int(addr)*4)+16:(int(addr)*4)+20])[0]
        
        os.close(fd0)
    

    def Optimal_Ramp(self,low,high,Time,RefClock): 


        SYNC_CLK=RefClock 
    
    
        RSRRArray=np.array([])
        RDWArray=np.array([])
        COUNTArray=np.array([])
        
        figureOfMeritArray=np.array([])
    
        for RSRR in range (0x1,0xFFFF):
        
            timeStep=(1+RSRR)/SYNC_CLK
            NTimeSteps=np.ceil(Time/timeStep)
       
            S0=int(np.ceil(low/RefClock*2**48))
            E0=int(np.ceil(high/RefClock*2**48))
            RDW=int((np.ceil(abs(E0-S0)/NTimeSteps)))
    
            if RDW>0:
                slope=abs((E0-S0)/(Time))
                NDACSteps=np.floor(abs(E0-S0)/RDW)
                NDACStepsCeil=np.ceil(abs(E0-S0)/RDW)
            
                figureOfMerit=0
                
                figureOfMerit+=1/6 *NDACSteps *timeStep *(RDW**2* (1 + NDACSteps)* (1 + 2 *NDACSteps) - RDW *slope *(1 + NDACSteps) *(-1 + 4* NDACSteps)* timeStep +  2 *slope**2 *NDACSteps**2 *timeStep**2)
                figureOfMerit+=1/3* slope**2 *(Time - NDACSteps*timeStep)**3
               
                
                if (RDW*NDACStepsCeil+S0)<2**48: 
                    RDWArray=np.append(RDWArray,[RDW])
                    RSRRArray=np.append(RSRRArray,[RSRR])
                    COUNTArray=np.append(COUNTArray,[NTimeSteps])
                    figureOfMeritArray=np.append(figureOfMeritArray,[figureOfMerit])
                    
        
        try:
            minIndex=np.where(figureOfMeritArray==np.min(figureOfMeritArray))[0][0]
            self.SRRC=RSRRArray[minIndex]
            self.SDFW=RDWArray[minIndex]
                        
            self.COUNT=COUNTArray[minIndex]
            
           
        except:
            
            return [0,0,0,0]

      
      

        
        
    def Calc_Ramp(self,_low_,_high_,_Time_,_RefClock_,_Mode_,_DFW_,_RRC_):     
        
                 
        self.FTW1= int(round((2**(48))*_low_/_RefClock_))
        self.FTW2= int(round((2**(48))*_high_/_RefClock_))
        
## si pas optimisation : on prend les valeurs fournies par user
  


        if(_Mode_=='Sweep') :

            
				
			
            if (_low_>_high_ ):

                if _RRC_==0 : #### eviter le diviser par 0
                    _RRC_=1
 
                self.SDFW=int(_DFW_)
                self.SRRC=int(_RRC_)
                self.NbPts=int(np.ceil(_Time_*_RefClock_/(self.SRRC+1)))
                self.COUNT=self.NbPts
                self.Sign=0
                
                
            else : 

                if _RRC_==0 : #### eviter le diviser par 0
                    _RRC_=1
                    
                self.SDFW=int(_DFW_)
                self.SRRC=int(_RRC_)
                self.NbPts=int(np.ceil(_Time_*_RefClock_/(self.SRRC+1)))
                self.COUNT=self.NbPts
                self.Sign=1

                
            if self.get_Optimize_Mode()=='On' :
        
                self.Optimal_Ramp(_low_,_high_,_Time_,_RefClock_)
            
                        
        else : 
            
            self.SDFW=0
            self.SRRC=0
            self.Sign=1
	    
            self.COUNT =int(round( _Time_/ ( 4*(self.get_UpdtDelay()+1)*10**(-9))))
            self.FTW2=self.FTW1
    
        print('DFW',self.SDFW)
        print('RRC',self.SRRC)
        print('self.FTW1 : ', self.FTW1)
        print('self.FTW2 : ', self.FTW2)
        print(' sign : ', self.Sign)
        


obj[0]=Wfm()
obj[0].set_ChName(1,'V1')
obj[0].set_ChEnable('V1',1)
obj[0].set_ChName(2,'V2')
obj[0].set_ChEnable('V2',0)
obj[0].set_RefClock(300000000)
obj[0].set_ChStartFrequency('V1',10000000)
obj[0].set_ChStopFrequency('V1',  15000000)
obj[0].set_ChStartFrequency('V2', 6000000)
obj[0].set_ChStopFrequency('V2',  14000000)
obj[0].set_ChDuration('V1',2)
obj[0].set_ChDuration('V2',0.00004)
obj[0].set_ChMode('V1','Sweep')
obj[0].set_ChMode('V2','Sweep')

obj[1]=Wfm()
obj[1].set_ChName(1,'V1')
obj[1].set_ChEnable('V1',1)
obj[1].set_ChName(2,'V2')
obj[1].set_ChEnable('V2',0)
obj[1].set_RefClock(300000000)
obj[1].set_ChStartFrequency('V1',20000000)
obj[1].set_ChStopFrequency('V1',30000000)
obj[1].set_ChStartFrequency('V2',30000000)
obj[1].set_ChStopFrequency('V2',40000000)
obj[1].set_ChDuration('V1',2)
obj[1].set_ChDuration('V2',0.00002)
obj[1].set_ChMode('V1','Sweep')
obj[1].set_ChMode('V2','Sweep')

obj[2]=Wfm()
obj[2].set_ChName(1,'V1')
obj[2].set_ChEnable('V1',1)
obj[2].set_ChName(2,'V2')
obj[2].set_ChEnable('V2',0)
obj[2].set_RefClock(300000000)
obj[2].set_ChStartFrequency('V1',30000000)
obj[2].set_ChStopFrequency('V1',10000000)
obj[2].set_ChStartFrequency('V2',40000000)
obj[2].set_ChStopFrequency('V2',50000000)
obj[2].set_ChDuration('V1',2)
obj[2].set_ChDuration('V2',0.50002)
obj[2].set_ChMode('V1','Sweep')
obj[2].set_ChMode('V2','Sweep')

obj[3]=Wfm()
obj[3].set_ChName(1,'V1')
obj[3].set_ChEnable('V1',1)
obj[3].set_ChName(2,'V2')
obj[3].set_ChEnable('V2',0)
obj[3].set_RefClock(300000000)
obj[3].set_ChStartFrequency('V1',10000000)
obj[3].set_ChStopFrequency('V1',10000000)
obj[3].set_ChStartFrequency('V2',40000000)
obj[3].set_ChStopFrequency('V2',50000000)
obj[3].set_ChDuration('V1',2)
obj[3].set_ChDuration('V2',0.50002)
obj[3].set_ChMode('V1','Single')
obj[3].set_ChMode('V2','Sweep')

seq[0]=Seq()
seq[0].Seq_Add(obj[0])
seq[0].Seq_Add(obj[1])
seq[0].Seq_Add(obj[2])
#seq[0].Seq_Add(obj[3])

titi=Gen()
titi.IP_Reset()
titi.cfg_offset= 0x60000000 
titi.axi_bram_reader=0x43C10000
titi.axi_bram_writer=0x43C00000
titi.set_SpiClock(10)
titi.set_UpdtClock(20)
titi.set_UpdtDelay(1)
titi.set_TXB(0)
titi.Reset()
titi.set_Optimize_Mode('Off')

#toto.Gen()
#toto.IP_Reset()
#toto.cfg_offset= 0x60000000 
#toto.axi_bram_reader=0x43C10000
#toto.axi_bram_writer=0x43C00000
#toto.set_SpiClock(10)
#toto.set_UpdtClock(20)
#toto.set_UpdtDelay(1)
#toto.set_TXB(0)
#toto.Reset()
#toto.set_Optimize_Mode('Off')

#fd0=os.open('/dev/mem',os.O_RDWR)
#cfg0=mmap.mmap(fileno=fd0,length=mmap.PAGESIZE,offset=titi.cfg_offset)
       
#v0=struct.unpack("<L",cfg0[0:4])[0]
#v0= v0 & ~(1 << titi.QSPI)
#cfg0[0:4]=struct.pack("L",v0)
#sleep(0.01)
#os.close(fd0)

titi.set_SYNCCRTL(0)
titi.set_SYNCReset(1)
titi.set_SYNCReset(0)
titi.set_SYNC(70)# freq=20 MHZ/(n+1)
titi.set_SYNCCRTL(1)

titi.CR = titi.CR & ~ (3 << 9)
titi.CR = titi.CR & ~(1 << 8)  # external update
titi.CR = titi.CR | (1 << 21) #pll diseable
titi.RAM_Write(0,0x8040007 | (titi.Sign1 <<17)) ####registre CSR
titi.RAM_Write(1,int(titi.CR))
titi.RAM_Write(2,0)
titi.RAM_Write(3,1)
titi.RAM_Write(4, 0x100000 | (titi.Sign1 <<17) )
titi.Run2()

#toto.CR = toto.CR & ~ (3 << 9)
#toto.CR = toto.CR & ~(1 << 8)  # external update
#toto.CR = toto.CR | (1 << 21) #pll diseable
#toto.RAM_Write(0,0x8040007 | (toto.Sign1 <<17)) ####registre CSR
#toto.RAM_Write(1,int(toto.CR))
#toto.RAM_Write(2,0)
#toto.RAM_Write(3,2)
#toto.RAM_Write(4, 0x100000 | (toto.Sign1 <<17))
#toto.Run2()

#titi.set_TXB(1)
#toto.set_TXB(1)


#tmp=seq[0].Seq_Get(0)


#toto.Calc_Ramp(tmp.get_ChStartFrequency(tmp.get_ChName(1)),tmp.get_ChStopFrequency(tmp.get_ChName(1)),tmp.get_ChDuration(tmp.get_ChName(1)),tmp.get_RefClockValue(),tmp.get_ChMode(tmp.get_ChName(1)),tmp.get_ChDFW(tmp.get_ChName(1)),tmp.get_ChRRC(tmp.get_ChName(1)))
#toto.Sign1=toto.Sign

#toto.RAM_Write(0, 0xC040002 | (toto.Sign1 << 17))
#toto.RAM_Write(1, (toto.FTW1) >>16)
#toto.RAM_Write(2, (toto.FTW1-((toto.FTW1 >>16)<<16))<<16)
#toto.RAM_Write(3, 0)

#toto.RAM_Write(4, 0xC040003 | (toto.Sign1 << 17))
#toto.RAM_Write(5, (toto.FTW2) >>16)
#toto.RAM_Write(6, (toto.FTW2-((toto.FTW2 >>16)<<16))<<16)
#toto.RAM_Write(7, 0)

#toto.RAM_Write(8, 0xC040004 | (toto.Sign1 << 17))
#toto.RAM_Write(9, 0x1000)
#toto.RAM_Write(10,0)
#toto.RAM_Write(11, 0)

#toto.RAM_Write(12,0x6040006 | (toto.Sign1 <<17))
#toto.RAM_Write(13,int(10000)<<8)
#toto.RAM_Write(14,0)
#toto.RAM_Write(15,0)

#toto.CR = toto.CR & ~ (3 << 9)
#toto.CR = toto.CR | (2 << 9) #modulation

#toto.RAM_Write(16,0x8040007 | (toto.Sign1 <<17)) ####registre CSR
#toto.RAM_Write(17,int(toto.CR))
#toto.RAM_Write(18,0)
#toto.RAM_Write(19,0)

#toto.RAM_Write(20,0x80000 | (toto.Sign1 <<17)) ####registre CSR
#toto.RAM_Write(21,0)
#toto.RAM_Write(22,0)
#toto.RAM_Write(23,3000)

#toto.RAM_Write(24,0x6040006 | (toto.Sign1 <<17))
#toto.RAM_Write(25,int(200000)<<8)
#toto.RAM_Write(26,0)
#toto.RAM_Write(27,0)

#toto.RAM_Write(28,0x80000 & ~(toto.Sign1 <<17)) ####registre CSR
#toto.RAM_Write(29,0)
#toto.RAM_Write(30,0)
#toto.RAM_Write(31,50000000)

#toto.RAM_Write(32, 0x100000 & ~ (toto.Sign1 <<17)) ####registre CSR

#toto.Run2()
#titi.Run()


