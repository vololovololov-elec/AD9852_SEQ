# Imports
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
import time
from smbus2 import SMBus
from datetime import datetime

seq_file = "seq.pkl"
wav_file = "wav.pkl"
# Global Constants
## Séparateur pour extraire les données de l'utilisateur du buffer.
SEP='::'
## Séparateur pour extraire les données de l'utilisateur du buffer.
obj= [0]*100
## Chaque pente ou fréquence fixe est un objet obj.
seq = [0]*100
## Un ensemble de pentes ou fréquences fixes est une séquence seq.
gen =[0]*10

UDB=1000
UDM=6

class Error():

    def __init__(self):

        """! Initialise la classe Error."""
        """! Les erreurs numérotées de 0 à 99 sont des erreurs dans une commande."""
        """! Les erreurs numérotées de 100 à 199 sont des erreurs dans l'execution d'une commande."""
        """! Les erreurs numérotées de 200 à 299 sont des erreurs internes au systeme."""
        """! Les erreurs numérotées de 300 à 399 sont des erreurs dans une requete."""

        
        self.Command=['Command error','Invalid character','Syntax error','Invalid separator','Data type error','GET not allowed','Parameter not allowed','Missing parameter','Command header error'
        ,'Header separator error','Program mnemonic too long','Undefined error','Header suffix out of range','Unexpected number of parameters','Numeric data error'
        ,'Invalid character in number','Exponent too large','Too many digits','Numeric data not allowed','Suffix error','Invalid suffix'
        ,'Suffix too long','Suffix not allowed','Character data error','Invalid character data'
        ,'Character data not allowed','String data error','Invalid string data','String data not allowed'
        ,'Block data error','Invalid block data','Block data not allowed','Expression error'
        ,'Invalid expression','Expression data not allowed','Macro error'
        ,'Invalid outside macro definition','Invalid inside macro definition','Macro parameter error']

        
        self.Execution=['Execution error','Invalid while in local','Settings lost due to rtl','Command protected','Trigger error','Trigger ignored','Arm ignored','Init ignored','Trigger deadlock'
        ,'Arm deadlock','Parameter error','Settings conflict','Data out of range','Too much data','Illegal parameter value','Out of memory','Lists not same length','Data corrupt or stale'
        ,'Invalid format','Invalid version','Hardware error','Hardware missing','Mass storage error','Missing mass storage','Missing media','Corrupt media','Media full','Directory full'
        ,'File name not found','File name error','Media protected','Expression error','Math error in expression','Macro error','Macro syntax error','Macro execution error'
        ,'Illegal macro label','Macro parameter error','Macro definition too long','Macro recursion error','Macro redefinition not allowed'
        ,'Macro header not found','Program error','Cannot create program','Illegal program name','Program currently running','Program syntax error'
        ,'Program runtime error','Memory use error','Out of memory','Referenced name does not exist','Referenced name already exists']

        
        self.Device=['Device-specific error','System error','Memory error','PUD memory lost','Calibration memory lost','Save/recall memory lost','Configuration memory lost','Storage fault'
        ,'Out of memory','Self-test failed','Calibration failed','Queue overflow','Communication error','Parity error in program message','Framing error in program message','Input buffer overrun'
        ,'Time out error']

        self.Query=['Query error','Query INTERRUPTED','Query UNTERMINATED','Query DEADLOCKED','Query UNTERMINATED after indefinite response']

        Current=0
        self.List = []
        
    def Err_Add(self,_code_):
"""! Ajoute à la pile le code correspondant à une erreur donnée.
        @param code   Le numéro correspondant à l'erreur.
        @param code_max   399.
        @param code_min   0.
        @return  
        """
        self.List.append(_code_)

    def Err_Get(self,index):
"""! Renvoie le code correspondant à l'élement n de la pile.
        @param index   index de l'élément de la pile.
        @return  renvoie le code d'erreur de l'élément n de la pile.
        """
        return self.List[index]


    def Err_Clear(self):
"""! Efface la totalité de la pile.
        @return  
        """
        self.List.clear()

    def Err_Insert(self,index,_code_):
"""! Ajoute à la pile le code correspondant à une erreur donnée à une position n.
        @param index  position dans la pile.
        @param code   le numéro correspondant à l'erreur.
        @return  
        """
        self.List.insert(index,_code_)

    def Err_Del(self,index):
"""! Supprime de la pile le code se trouvant à la position n de la pile.
        @param index   position dans la pile.
        @return  
        """
        self.List.pop(index)

    def Err_GetSize(self):
"""! Renvoie la taille actuelle de la pile.
        @return  renvoie le nombre d'éléments de la pile.
        """
        return len(self.List)


    def Err_Message(self,_code_):
"""! Retourne l'intitulé d'un code.
        @param code   le numéro correspondant à l'erreur.
        @param code_max   399.
        @param code_min   0.
        @return       intitulé du code dans une chaîne ASCII.
        """
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
         """! Initialise la classe FGenBase."""
        """! "ch1" et "ch2" sont les noms par defaut des voies."""
        """! Les sorties sont actives."""
        self.chanName = ["ch1","ch2","ch12"]
        self.chanEnable =[True,True,True]
        self.ClockSrc=["internal","external"]
        self.ClockVal=0
        Error.__init__(self)
        
    def set_ChName(self, chan,chanName):
        """! Nomme une voie par une chaîne de caractères.
        @param chan   Le numéro de la voie de sortie.
        @param chan_max   2.
        @param chan_min   1.
        @param chanName   chaîne de caractères.
        @return  
        """
        if(int(chan)==1 or int(chan)==2) : 
            
            self.chanName[int(chan)-1]=chanName
        else :
            self.Err_Add(102)
 
        
    def get_ChName(self,chan):
        """! Retourne le nom d'une voie.
        @param chan   Le numéro de la voie de sortie.
        @param chan_max   2.
        @param chan_min   1.
        @return  nom sous forme d'une chaîne de caractères.
        """
        if(int(chan)==1 or int(chan)==2) :        
            
            return self.chanName[int(chan)-1]
        else :
            self.Err_Add(102)            
             
        
    def set_ChEnable(self,chanName,chanEnable):
        
         """! Pas implémenté.""" 
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
        """! Pas implémenté.""" 
        try:
            index=self.chanName.index(chanName)
        except ValueError:
            self.Err_Add(102)
        else :
            
            return self.chanEnable[self.chanName.index(chanName)]
    
     
    def set_RefClock(self,ClkVal):
        
          """! Renseigne la fréquence de l'horloge présente à l'entrée du dispositif.
        @param ClkVal   Fréquence en Hz.
        @param ClkVal_max   300000000 Hz.
        @param ClkVal_min   0.
        @return  
        """               
        if (float(ClkVal) <=500000000) and (float(ClkVal) > 0) :
            self.ClockVal=float(ClkVal)
        else : 
            self.Err_Add(102)
        
                
    def get_RefClockValue(self):
        
        """! Retourne la fréquence système définie par l'utilisateur.
        @return  Fréquence en Hz.
        """  
        return self.ClockVal


class StdFunc(FGenBase):
    
    def __init__(self):
         """! Initialise la classe StdFunc."""
        """! Gestion des parametres généraux d'une fréquence."""
        self.ChanStartFreq =[0.0,0.0,0.0,0.0]
        self.ChanStopFreq = [0.0,0.0,0.0,0.0]
        self.ChanPhase = [0.0,0.0,0.0,0.0]
        self.ChanAmplitude = [0.0,0.0,0.0,0.0]
        self.ChanDuration = [0.0,0.0,0.0,0.0]
        
        self.MRRC = [0,0,0,0]
        self.MDFW = [0,0,0,0]
        self.MFTW1 = [0,0,0,0]
        self.MFTW2 = [0,0,0,0]
        
        FGenBase.__init__(self)
        
    def set_ChStartFrequency(self,chanName,chanFrequency):
        
         """! Définit une fréquence fixe.
        @param chanName   Nom de la voie.
        @param chanFrequency   Fréquence en Hz.
        @param chanFrequency_max   150000000 Hz.
        @param chanFrequency_min   0 Hz.
        @return  
        """
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
        
"""! Retourne la fréquence définie par l'utilisateur.
        @param chanName   Nom de la voie.
        @return  Fréquence en Hz.
        """

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
         """! Pas implémenté.""" 
        self.ChanAmplitude[self.chanName.index(chanName)]=float(chanAmplitude)
                
    def get_ChAmplitude(self,chanName):
         """! Pas implémenté.""" 
        
        return self.ChanAmplitude[self.chanName.index(chanName)]

class Wfm(StdFunc):
    
    def __init__(self):
         """! Initialise la classe Waveform."""
        """! Gestion des parametres généraux d'une rampe de fréquence ou single tone."""
        """! Elle nécessite une fréquence de départ, une fréquence de fin et une durée en cas de rampe."""
        """! L'utilisateur peut surdéfinir les valeurs envoyées aux DDS """      
        StdFunc.__init__(self)
        self.SweepMode=["Single","Sweep"]
        self.chanMode = ["Single","Single","Single"]
        self.Modif=0        
    
      
    def set_ChStopFrequency(self,chanName,chanFrequency):
        
 """! Définit une fréquence de fin.
        @param chanName   nom de la voie.
        @param chanFrequency   fréquence en Hz.
        @param chanFrequency_max   150000000 Hz.
        @param chanFrequency_min   0 Hz.
        @return  
        """
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
        
 """! Retourne la fréquence de fin définie par l'utilisateur.
        @param chanName   nom de la voie.
        @return  fréquence en Hz.
        """
        try:
            index=self.chanName.index(chanName)
        except ValueError:
            self.Err_Add(102)
        else :
            
            return self.ChanStopFreq[self.chanName.index(chanName)]
        
        
    def set_ChDuration(self,chanName,chanDuration):
         """! Définit la durée de la rampe en secondes.
        @param chanName   Nom de la voie.
        @param chanDuration   durée en secondes.
        @return  
        """

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
"""! Retourne la durée de la rampe en secondes définie par l'utilisateur.
        @param chanName   Nom de la voie.
        @return  durée en secondes.
        """
        return self.ChanDuration[self.chanName.index(chanName)]
        #try:
            #index=self.chanName.index(chanName)
        #except ValueError:
            #self.Err_Add(102)
        #else :
            
            #return self.ChanDuration[self.chanName.index(chanName)] 
        
    def set_ChFTW1(self,chanName,_FTW1_):


        try:
            index=self.chanName.index(chanName)
        except ValueError:
            self.Err_Add(102)
        else :

            if (int(_FTW1_) < 2**48) and (int(_FTW1_) > 0) :

                
                self.MFTW1[self.chanName.index(chanName)]=int(_FTW1_)

            else :

                self.Err_Add(102)

    def set_ChFTW2(self,chanName,_FTW2_):


        try:
            index=self.chanName.index(chanName)
        except ValueError:
            self.Err_Add(102)
        else :

            if (int(_FTW2_) < 2**48) and (int(_FTW2_) > 0) :

                
                self.MFTW2[self.chanName.index(chanName)]=int(_FTW2_)

            else :

                self.Err_Add(102)



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

    def get_ChFTW1(self,chanName):

        try:
            index=self.chanName.index(chanName)
        except ValueError:
            self.Err_Add(102)
        else :
            
            return self.MFTW1[self.chanName.index(chanName)]


    def get_ChFTW2(self,chanName):

        try:
            index=self.chanName.index(chanName)
        except ValueError:
            self.Err_Add(102)
        else :
            
            return self.MFTW2[self.chanName.index(chanName)]



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
         """! Définit le mode de fonctionnement d'une sortie de la DDS.
        @param chanName   Nom de la voie.
        @param Mode   'Single' ou 'Sweep'.
        @return  
        """
        try:
            index=self.SweepMode.index(Mode) #and index2=self.chanName.index(chanName) 
        except ValueError:
            self.Err_Add(102)
        else :
           
            self.chanMode[self.chanName.index(chanName)]=Mode
       
    
    def get_ChMode(self,Name):
         """! Retourne le mode de fonctionnement d'une sortie de la DDS.
        @param Name   Nom de la voie.
        @return  'Single' ou 'Sweep'.
        """
        return  self.chanMode[self.chanName.index(Name)]

class Seq(Error) : 
    
    def __init__(self):
     """! Initialise la classe Séquence."""
        """! Elle se compose d'une liste d'objets waveform."""
        """! L'utilisateur peut manipuler cette liste comme une liste classique."""
        Error.__init__(self)
        #Wfm.__init__(self)
        Current=0
        self.List = []
        self.Active=0

    
    
    def Seq_Add(self,obj):
     """! Ajoute à la liste un objet de la classe waveform.
        @param obj   objet waveform.
        @return  
        """
        self.List.append(obj)
        
    def Seq_Get(self,index):
   """! Renvoie une référence à l'objet Waveform n de la séquence.
        @param index   index de l'objet dans la liste.
        @return  référence à un objet Waveform.
        """
        if (index < len(self.List)) and  (index >=0) :

            return self.List[index]

        else :

            self.Err_Add(102)

    def Seq_Clear(self):
        """! Efface la totalité de la séquence.
        @return  
        """
        self.List.clear()
    
    def Seq_Insert(self,index,obj):
        """! Ajoute à la position n de la séquence un objet Waveform.
        @param index  position dans la séquence.
        @param obj   objet waveform.
        @return  
        """
        if (index < len(self.List)) and  (index >=0) :

            self.List.insert(index,obj)

        else :

            self.Err_Add(102)

        
    def Seq_Del(self,index):
          """! Supprime à la position n de la séquence un objet Waveform.
        @param index  position dans la séquence.
        @return  
        """
        if (index < len(self.List)) and  (index >=0) :

            self.List.pop(index)

        else :

            self.Err_Add(102)

        
    def Seq_GetSize(self):
        """! Renvoie le nombre d'objets Waveform de la séquence.
        @return  nombre d'objets.
        """
        return len(self.List)

    
           
    def Seq_Save(self,_FName_):  
         """! Dump la totalité de la séquence dans un fichier Pickle.
        @param FName  nom du fichier.
        @return  
        """
        try:
            with open(_FName_,'wb') as f: 
                pickle.dump(self.List, f)
        
        except ValueError:
            self.Err_Add(102)
       
    
    def Seq_Read(self,_FName_):  
         """! Regénere la totalité de la séquence à partir d'un fichier pickle.
        @param FName  nom du fichier.
        @return  
        """
        try:
            with open(_FName_,'rb') as f:
                self.List.clear()
                self.List = pickle.load(f)
                
        except ValueError:
            self.Err_Add(102)


class Gen (Seq): 
    
    def __init__(self,Core):
        
         """! Initialise la classe Generateur."""
        """! Un dispositif peut engager plusieurs séquences et/ou Waveforms."""
        """! Chaque DDS n'ayant qu'une sortie, est controlée par un objet Générateur différent."""  
        """! @param core  O/1 pour DDS1/2."""      
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
        self.Mode=0
        self.UFTW1=0# valeur user de la freq1
        self.UFTW2=0# valeur user de la freq2
        self.UDFW=0# valeur user du step en freq
        self.URRC=0# valeur user du step en temps
        
        if Core :
            
            self.cfg_offset= 0x50000000 
            self.axi_bram_reader=0x43C40000
            self.axi_bram_writer=0x43C50000
            self.IPCore=1

        else :
            self.cfg_offset= 0x60000000 
            self.axi_bram_reader=0x43C10000
            self.axi_bram_writer=0x43C00000
            self.IPCore=0

    ## Documentation for a function.
    #
    #  More details.
            
    def IP_Reset(self):
    """! Reset de la logique programmable en charge du séquencement."""
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
    
    
  

    def Reset(self):
"""! prends le controle du bus et effectue un reset de la DDS."""
        """! TXB_ON : active les drivers de bus de la carte."""
        """! DDS_RAZ_SOFT :  aiguille le switch et envoie raz soft et non IP sur raz DDS bit."""
        """! DDS_RAZ : effectue un pulse sur le bit 7  du registre cfg0."""
        """! La DDS étant revenue en mode update interne, elle est reprogrammée par spi en mode externe."""
        tmp = [0,0,0,0,0]
        self.set_TXB(0)
        
        fd0=os.open('/dev/mem',os.O_RDWR)
        cfg0=mmap.mmap(fileno=fd0,length=mmap.PAGESIZE,offset=self.cfg_offset)
        
        self.v0=struct.unpack("<L",cfg0[0:4])[0]
        
        self.v0= self.v0 & ~(1<< self.DDS_RAZ)
        self.v0= self.v0 | (1 << self.DDS_RAZ_SOFT) #prends la main sur l'ip
        
        cfg0[0:4]=struct.pack("L",self.v0)
       
        sleep(0.01)
        self.v0= self.v0 | (1 << self.DDS_RAZ)
        self.v0= self.v0 | (1 <<  self.DDS_RAZ_SOFT)#prends la main sur l'ip
        
        cfg0[0:4]=struct.pack("L",self.v0)
        
        sleep(0.01)
        self.v0= self.v0 & ~(1<< self.DDS_RAZ)
        
        self.v0= self.v0 & ~ (1 <<  self.DDS_RAZ_SOFT)#rends la main sur l'ip
        cfg0[0:4]=struct.pack("L",self.v0)
        
        sleep(0.01)
        
        os.close(fd0)

        for i in range (0,4):
            tmp[i]=self.RAM_Read(i)
            
        self.CR = self.CR & ~ (3 << 9)
        self.CR = self.CR & ~(1 << 8)  # external update
        self.CR = self.CR | (1 << 21) #pll diseable
        self.RAM_Write(0,0x8040007 | (self.Sign1 <<17)) ####registre CSR
        self.RAM_Write(1,int(self.CR))
        self.RAM_Write(2,0)
        self.RAM_Write(3,0)
        self.RAM_Write(4, 0x100000 & ~(1 <<17) & ~(1 <<16) )
        self.Run2()
        
        for i in range (0,4):
            self.RAM_Write(i,tmp[i])

        self.set_TXB(1)
        self.SPI_Mode ='Spi'
        
        


    
    
    def Run(self):
     """! Lance la logique programmable en charge du séquencement."""
    """! L'IPCore effectue d'abord un update sur la DDS puis commence à lire la mémoire contenant la séquence."""
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
     """! Lance la logique programmable en charge du séquencement."""
    """! L'IPCore n'effectue pas d'update au préalable sur la DDS puis commence à lire la mémoire contenant la séquence."""
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
    
    
    
    def Update(self):

 """! prends le controle du bus et effectue un update soft de la DDS."""
    """! TXB_ON : active les drivers de bus de la carte."""
    """! UPDT_SOFT : aiguille le switch et envoie updt soft et non IP sur updt de la DDS."""
    """! UPDT : effectue un pulse sur le bit 4  du registre cfg0 """
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

   


    
    
    def set_PowerUp(self,power):
            """! non implémenté."""
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
          """! non implémenté."""  
        return self.POWER_MODE
        

    

    def set_UpdateCtrl(self,mode):
             """! pilote l'IPCore multiplexeur qui permet de choisir entre :
        - le signal update venant du serveur AD9852.py  
        - le signal update venant de l'IPCore séquenceur."""
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
        


        
    

    def set_SpiClock(self,clock):
         """! fixe le rapport de division de l'horloge du protocole spi."""
        """! @param cfg0[15:19]  valeur sur 32 bits.
        @return """
        if (int(clock) <=2**31) and (int(clock) >0):
        
            fd0=os.open('/dev/mem',os.O_RDWR)
            cfg0=mmap.mmap(fileno=fd0,length=mmap.PAGESIZE,offset=self.cfg_offset)
            self.spi_clk=clock
            cfg0[12:16]=struct.pack("L",self.spi_clk)
            sleep(0.01)
        
            os.close(fd0)

        else :
 
            self.Err_Add(102)        

    
    
    def get_SpiClock(self):
        
         """! Retourne le rapport de division de l'horloge du protocole spi."""
        """! @return valeur sur 32 bits."""
        fd0=os.open('/dev/mem',os.O_RDWR)
        cfg0=mmap.mmap(fileno=fd0,length=mmap.PAGESIZE,offset=self.cfg_offset)
        return struct.unpack("<L",cfg0[12:16])[0]
        sleep(0.01)
        os.close(fd0)
        
   
        
    def set_UpdtClock(self,clock):
 """! fixe le rapport de division du compteur en charge de la durée d'une Waveform."""
        """! Celui-ci est cadencé par une horloge de 150 MHz."""
        """! Plus la valeur est importante et plus le compteur sera ralenti."""
        """! Nécessaire en cas de rampe dont la durée peut dépasser quelques secondes."""
        """! @param clock  valeur sur 32 bits"""
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
        """! Retourne le rapport de division du compteur en charge de la durée d'une Waveform."""
        """! @return valeur sur 32 bits"""
        fd0=os.open('/dev/mem',os.O_RDWR)
        cfg0=mmap.mmap(fileno=fd0,length=mmap.PAGESIZE,offset=self.cfg_offset)
        return struct.unpack("<L",cfg0[8:12])[0]
        sleep(0.01)
        os.close(fd0)
    
        
    
    
    def set_UpdtDelay(self,clock):
"""! Non implémenté."""
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
        """! Non implémenté."""
        fd0=os.open('/dev/mem',os.O_RDWR)
        cfg0=mmap.mmap(fileno=fd0,length=mmap.PAGESIZE,offset=self.cfg_offset)
        return struct.unpack("<L",cfg0[4:8])[0]
        sleep(0.01)
        os.close(fd0)

   

    def set_TXB(self,_state_):
        """! Active ou pas le driver de ligne txb0108.Celui-ci est entre la pin GPIO du FPGA et la pin update de la DDS."""
        """! @param state 0/1 isolé/passant"""
        
        
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

    ## Documentation for a function.
    #
    #  More details.
    
    def Get_Memory_Access(self): 
    
        return self.MemAccess_Mode
    
    
   
    ###############################################################################
    # update interne ou externe
    ###############################################################################

    ## Documentation for a function.
    #
    #  More details.

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
				
    

    def get_UPDT_Mode(self): 
            
        return  self.UPD_Mode				
				
				
    
          
    def set_QSPI_Mode(self,opt):
    
         """! Non implémenté.""" 
       
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

    ## Documentation for a function.
    #
    #  Non implémentée.

    def get_QSPI_Mode(self): 
        """! Non implémenté."""    
        return  self.SPI_Mode



    ###############################################################################
    # determine si trig sur front montant (1) ou descendant (0)
    ###############################################################################

    ## Documentation for a function.
    #
    #  More details.

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

    ## Documentation for a function.
    #
    #  More details.

    def Get_Trig_Mode(self) :

        return self.TrigMode

    ## Documentation for a function.
    #
    #  More details.
   
    
    def RAM_Write(self,addr,val):
    
        self.Set_Memory_Access('Wr')
        fd0=os.open('/dev/mem',os.O_RDWR | os.O_SYNC)
        ram0=mmap.mmap(fileno=fd0,length=mmap.PAGESIZE,offset=self.axi_bram_writer)
        
        ram0[(int(addr)*4)+16:(int(addr)*4)+4+16]=struct.pack("L", int(val))
        #sleep(0.01)
        os.close(fd0) 
        
    ## Documentation for a function.
    #
    #  More details.  
    
    def RAM_Read(self,addr):
        
        self.Set_Memory_Access('Rd')
        fd0=os.open('/dev/mem',os.O_RDWR | os.O_SYNC)
        ram0=mmap.mmap(fileno=fd0,length=mmap.PAGESIZE,offset=self.axi_bram_reader)
        struct.unpack("<L", ram0[int(addr+3)*4:(int(addr+3)*4)+4])[0]
        return struct.unpack("<L", ram0[(int(addr)*4)+16:(int(addr)*4)+20])[0]
        
        os.close(fd0)

    ## Documentation for a function.
    #
    #  More details. 

    def Optimal_Ramp(self,low,high,Time,RefClock): 


        SYNC_CLK=RefClock 
        
        
        RSRRArray=np.array([])
        RDWArray=np.array([])
        COUNTArray=np.array([])
        figureOfMeritArray=np.array([])
        figureOfMeritMin=0
        RSRRMin=1
        RDWMin=0
        S0=int(np.ceil(low/RefClock*2**48))
        E0=int(np.ceil(high/RefClock*2**48))
        slope=abs((E0-S0)/(Time))
        for RSRR in range (1,1048575,4112):
        
            timeStep=(1+RSRR)/SYNC_CLK
            NTimeSteps=np.ceil(Time/timeStep)
              
            RDW=int((np.ceil(abs(E0-S0)/NTimeSteps)))
    
            
            NDACSteps=np.floor(abs(E0-S0)/RDW)
            NDACStepsCeil=np.ceil(abs(E0-S0)/RDW)
            
            figureOfMerit=0
            figureOfMerit+=1/6 *NDACSteps *timeStep *(RDW**2* (1 + NDACSteps)* (1 + 2 *NDACSteps) - RDW *slope *(1 + NDACSteps) *(-1 + 4* NDACSteps)* timeStep +  2 *slope**2 *NDACSteps**2 *timeStep**2)
            figureOfMerit+=1/3* slope**2 *(Time - NDACSteps*timeStep)**3
               
                
            if (RDW*NDACStepsCeil+S0)<2**48: 

               # if (RSRR==1) :
                #    figureOfMeritMin=figureOfMerit
                 #   RSRRMin=RSRR
                  #  RDWMin=RDW
                   # NTimeStepsMin=NTimeSteps

                if (figureOfMerit < figureOfMeritMin or RSRR==1):
                    figureOfMeritMin=figureOfMerit
                    RSRRMin=RSRR
                    RDWMin=RDW
                    NTimeStepsMin=NTimeSteps
                    
        self.SRRC=RSRRMin
        self.SDFW=RDWMin
        self.COUNT=NTimeStepsMin
        
        #try:
         #   minIndex=np.where(figureOfMeritArray==np.min(figureOfMeritArray))[0][0]
            
         #   end = time.time()
         #   print(end - start)
         #   self.SRRC=RSRRArray[minIndex]
         #   self.SDFW=RDWArray[minIndex]
                        
         #   self.COUNT=COUNTArray[minIndex]
            
           
        #except:
            
         #   return [0,0,0,0]

      
      
    ## Documentation for a function.
    #
    #  More details.
     
        
    def Calc_Ramp(self,_low_,_high_,_Time_,_RefClock_,_Mode_,_UFTW1_,_UFTW2_,_UDFW_,_URRC_):     
        
                 
        self.FTW1= int(_UFTW1_)
        self.FTW2= int(_UFTW2_)
        
## si pas optimisation : on prend les valeurs fournies par user
  
        if _URRC_==0 : #### eviter le diviser par 0
            _URRC_=1

        if(_Mode_=='Sweep') :

            self.SDFW=int(_UDFW_)
            self.SRRC=int(_URRC_)
            self.NbPts=int(np.ceil(_Time_*_RefClock_/(self.SRRC+1)))
            self.COUNT=self.NbPts		

           			
            if (_low_>_high_ ):

                self.Sign=0
                                
            else : 

                self.Sign=1

                
            if self.get_Optimize_Mode()=='On' :

                self.FTW1= int(round((2**(48))*_low_/_RefClock_))
                self.FTW2= int(round((2**(48))*_high_/_RefClock_))
                self.Optimal_Ramp(_low_,_high_,_Time_,_RefClock_)
                self.COUNT=self.COUNT*self.SRRC/(self.get_UpdtDelay()+1)
                        
        else : ##### mode single tone #######
            
            self.Sign=1

            if self.get_Optimize_Mode()=='On' :
                
                self.FTW1= int(round((2**(48))*_low_/_RefClock_))
	    
            self.COUNT =int(round( _Time_ *_RefClock_/4)) # /2 : le compteur fpga a 150 MHZ et clock DDS a 300 MHZ
            
    
       
    def Load(self,_seq_,_wfm_,_all_):
        adreSS=0
        self.Mode=0
        if (int(_wfm_) == 0 or int(_all_)== 1)  :# si on ne modifie que la 1ere rampe ou prog de la totalite

            
            #preprogramme la 1ere rampe
            tmp=seq[int(_seq_)].Seq_Get(0)
        
            self.Calc_Ramp(tmp.get_ChStartFrequency(tmp.get_ChName(1)),tmp.get_ChStopFrequency(tmp.get_ChName(1)),tmp.get_ChDuration(tmp.get_ChName(1)),tmp.get_RefClockValue(),tmp.get_ChMode(tmp.get_ChName(1)),tmp.get_ChFTW1(tmp.get_ChName(1)),tmp.get_ChFTW2(tmp.get_ChName(1)),tmp.get_ChDFW(tmp.get_ChName(1)),tmp.get_ChRRC(tmp.get_ChName(1)))
            self.Sign1=self.Sign
        
            if(self.Sign1==1):
                # pente montante
   
                self.RAM_Write(adreSS, 0xC040002 )
                self.RAM_Write(adreSS+1, (self.FTW1) >>16)
                self.RAM_Write(adreSS+2, (self.FTW1-((self.FTW1 >>16)<<16)))
                self.RAM_Write(adreSS+3, 1)

                self.RAM_Write(adreSS+4, 0xC040003 )
                self.RAM_Write(adreSS+5, (self.FTW2) >>16)
                self.RAM_Write(adreSS+6, (self.FTW2-((self.FTW2 >>16)<<16)))
                self.RAM_Write(adreSS+7, 2)

            if (self.Sign1==0 and self.Mode==0) :
                #pente descendante
    
                self.RAM_Write(adreSS, 0xC040002 )
                self.RAM_Write(adreSS+1, (self.FTW2) >>16)
                self.RAM_Write(adreSS+2, (self.FTW2-((self.FTW2 >>16)<<16)))
                self.RAM_Write(adreSS+3, 1)

                self.RAM_Write(adreSS+4, 0xC040003 )
                self.RAM_Write(adreSS+5, (self.FTW1) >>16)
                self.RAM_Write(adreSS+6, (self.FTW1-((self.FTW1 >>16)<<16)))
                self.RAM_Write(adreSS+7, 2)

            if (self.Sign1==0 and self.Mode==1) :

                self.RAM_Write(adreSS, 0xC040002 )
                self.RAM_Write(adreSS+1, (self.FTW1) >>16)
                self.RAM_Write(adreSS+2, (self.FTW1-((self.FTW1 >>16)<<16)))
                self.RAM_Write(adreSS+3, 1)

                self.RAM_Write(adreSS+4, 0xC040003 )
                self.RAM_Write(adreSS+5, (self.FTW2) >>16)
                self.RAM_Write(adreSS+6, (self.FTW2-((self.FTW2 >>16)<<16)))
                self.RAM_Write(adreSS+7, 2)


            self.RAM_Write(adreSS+8, 0xC040004 )


            if (self.Sign1==0 and self.Mode==1) :
            
                t=self.SDFW ^ 0xFFFFFFFFFFFF # on inverse tous les bits +1
                t=t+1
                tM=(t & 0xFFFFFFFF0000)>>16
                tL=(t & 0xFFFF)
    
                self.RAM_Write(adreSS+9, tM)
                self.RAM_Write(adreSS+10, tL)
            else :
                tM=(titi.SDFW  & 0xFFFFFFFF0000)>>16
                tL=(titi.SDFW  & 0xFFFF)
                self.RAM_Write(adreSS+9, tM)
                self.RAM_Write(adreSS+10, tL)

            self.RAM_Write(adreSS+11, 3)


            self.RAM_Write(adreSS+12,0x6040006 )
            self.RAM_Write(adreSS+13,int(self.SRRC)<<8)
            self.RAM_Write(adreSS+14,0)
            self.RAM_Write(adreSS+15,4)


            if(tmp.get_ChMode(tmp.get_ChName(1))=="Single"):
                self.CR = self.CR & ~ (3 << 9)
            else : 
                self.CR = self.CR & ~ (3 << 9)
                self.CR = self.CR | (self.Mode+2)<< 9 #modulation
                self.CR = self.CR & ~ (1 << 8)
        
            self.RAM_Write(adreSS+16,0x8040007 ) ####registre CSR
            self.RAM_Write(adreSS+17,int(self.CR))
            self.RAM_Write(adreSS+18,0)
            self.RAM_Write(adreSS+19,5)

            ##############programmation de la phase ####################"""

            self.PAR1=int(np.ceil(tmp.get_ChStartPhase(tmp.get_ChName(1))*2**14/360))

            self.RAM_Write(adreSS+20,0x4040000 ) ####registre PAR1
            self.RAM_Write(adreSS+21,int(self.PAR1) <<16 )
            self.RAM_Write(adreSS+22,0 )
            self.RAM_Write(adreSS+23,0 )

            self.RAM_Write(adreSS+24, 0x100000 |(self.Sign1 <<17) |(self.Mode <<16))
            self.Run2()



           

        ####prog de n rampe #################################
        adreSS=0
        for i in range (1,seq[int(_seq_)].Seq_GetSize()):

            self.Mode=abs(self.Mode-1) # alternance des modes 2 et 3 fsk et chirp

            ## Documentation for a function.
            #
            #  int(_wfm_)== i on modifie une seule sequence en dehors de wfm0
            #  int(_wfm_)+1== i si on modifie wfm0 l adresse 0 a été utilisée pour spi + Run2. wfm1 demarre aussi a l adresse 0 il faut la reprogrammer
            #  int(_all_)== 1 on reprogrammer l ensemble des wfm
            # une modification du wfm0 oblige a reprogrammer cette partie.
            
            if (int(_wfm_)== i or (int(_wfm_)+1 == i) or int(_all_)== 1)  : 
            

                tmp=seq[int(_seq_)].Seq_Get(i)
                self.Calc_Ramp(tmp.get_ChStartFrequency(tmp.get_ChName(1)),tmp.get_ChStopFrequency(tmp.get_ChName(1)),tmp.get_ChDuration(tmp.get_ChName(1)),tmp.get_RefClockValue(),tmp.get_ChMode(tmp.get_ChName(1)),tmp.get_ChFTW1(tmp.get_ChName(1)),tmp.get_ChFTW2(tmp.get_ChName(1)),tmp.get_ChDFW(tmp.get_ChName(1)),tmp.get_ChRRC(tmp.get_ChName(1)))
                self.Sign1=self.Sign
                #self.Mode=abs(self.Mode-1) # alternance des modes 2 et 3 fsk et chirp
            
                if(self.Sign1==1):
                    # pente montante
   
                    self.RAM_Write(adreSS, 0xC040002 )
                    self.RAM_Write(adreSS+1, (self.FTW1) >>16)
                    self.RAM_Write(adreSS+2, (self.FTW1-((self.FTW1 >>16)<<16)))
                    self.RAM_Write(adreSS+3, 6*i)

                    self.RAM_Write(adreSS+4, 0xC040003 )
                    self.RAM_Write(adreSS+5, (self.FTW2) >>16)
                    self.RAM_Write(adreSS+6, (self.FTW2-((self.FTW2 >>16)<<16)))
                    self.RAM_Write(adreSS+7, 7*i)

                if (self.Sign1==0 and self.Mode==0) :
                    #pente descendante
    
                    self.RAM_Write(adreSS, 0xC040002 )
                    self.RAM_Write(adreSS+1, (self.FTW2) >>16)
                    self.RAM_Write(adreSS+2, (self.FTW2-((self.FTW2 >>16)<<16)))
                    self.RAM_Write(adreSS+3, 6*i)

                    self.RAM_Write(adreSS+4, 0xC040003 )
                    self.RAM_Write(adreSS+5, (self.FTW1) >>16)
                    self.RAM_Write(adreSS+6, (self.FTW1-((self.FTW1 >>16)<<16)))
                    self.RAM_Write(adreSS+7, 7*i)

                if (self.Sign1==0 and self.Mode==1) :

                    self.RAM_Write(adreSS, 0xC040002 )
                    self.RAM_Write(adreSS+1, (self.FTW1) >>16)
                    self.RAM_Write(adreSS+2, (self.FTW1-((self.FTW1 >>16)<<16)))
                    self.RAM_Write(adreSS+3, 6*i)

                    self.RAM_Write(adreSS+4, 0xC040003 )
                    self.RAM_Write(adreSS+5, (self.FTW2) >>16)
                    self.RAM_Write(adreSS+6, (self.FTW2-((self.FTW2 >>16)<<16)))
                    self.RAM_Write(adreSS+7, 7*i)


                self.RAM_Write(adreSS+8, 0xC040004 )

                if (self.Sign1==0 and self.Mode==1) :

                    t =self.SDFW ^ 0xFFFFFFFFFFFF # on inverse tous les bits
                    t=t+1
                    tM=(t & 0xFFFFFFFF0000)>>16
                    tL=(t & 0xFFFF)
                    titi.RAM_Write(adreSS+9, tM)
                    titi.RAM_Write(adreSS+10, tL)
                else :
                    tM=(titi.SDFW  & 0xFFFFFFFF0000)>>16
                    tL=(titi.SDFW  & 0xFFFF)
                    self.RAM_Write(adreSS+9, tM)
                    self.RAM_Write(adreSS+10, tL)

                self.RAM_Write(adreSS+11, 8*i)

                self.RAM_Write(adreSS+12,0x6040006 )
                self.RAM_Write(adreSS+13,int(self.SRRC)<<8)
                self.RAM_Write(adreSS+14,0)
                self.RAM_Write(adreSS+15,9*i)

                print(tmp.get_ChMode(tmp.get_ChName(1)))
                if(tmp.get_ChMode(tmp.get_ChName(1))=="Single"):
                    self.CR = self.CR & ~ (3 << 9)
                else : 
                    self.CR = self.CR & ~ (3 << 9)
                    self.CR = self.CR | (self.Mode+2)<< 9 #modulation
                    self.CR = self.CR & ~ (1 << 8)

                           
                self.RAM_Write(adreSS+16,0x8040007 ) ####registre CSR
                self.RAM_Write(adreSS+17,int(self.CR))
                self.RAM_Write(adreSS+18,0)
                self.RAM_Write(adreSS+19,10*i)

                #############programmtion phase ############################""""""""""""
                self.PAR1=int(np.ceil(tmp.get_ChStartPhase(tmp.get_ChName(1))*2**14/360))

                self.RAM_Write(adreSS+20,0x4040000 ) ####registre PAR1
                self.RAM_Write(adreSS+21,int(self.PAR1) <<16 )
                self.RAM_Write(adreSS+22,0 )
                self.RAM_Write(adreSS+23,0 )


                tmp=seq[int(_seq_)].Seq_Get(i-1)
                self.Calc_Ramp(tmp.get_ChStartFrequency(tmp.get_ChName(1)),tmp.get_ChStopFrequency(tmp.get_ChName(1)),tmp.get_ChDuration(tmp.get_ChName(1)),tmp.get_RefClockValue(),tmp.get_ChMode(tmp.get_ChName(1)),tmp.get_ChFTW1(tmp.get_ChName(1)),tmp.get_ChFTW2(tmp.get_ChName(1)),tmp.get_ChDFW(tmp.get_ChName(1)),tmp.get_ChRRC(tmp.get_ChName(1)))

                self.RAM_Write(adreSS+24,0x80000 |(titi.Sign1 <<17) |(self.Mode <<16)) ####registre CSR

                self.RAM_Write(adreSS+25,0)
                self.RAM_Write(adreSS+26,1)
                #self.RAM_Write(adreSS+27,int(self.COUNT*self.SRRC/(self.get_UpdtDelay()+1)))
                self.RAM_Write(adreSS+27,int(self.COUNT))
            adreSS=adreSS+28




         

        ########### programmation d'un single tone a freq start de la rampe 1

        adreSS=(i*28)

        ## Documentation for a function.
        #
        #  La sequence de fin : single tone a F1 de la 1ere rampe et preprogrammation de la 1ere rampe pour demarrer des le TTL recu
        # une modification du wfm0 oblige a reprogrammer cette partie.

        if (int(_wfm_)== 0  or int(_all_)== 1)  :
                
            tmp=seq[int(_seq_)].Seq_Get(0)
            self.Calc_Ramp(tmp.get_ChStartFrequency(tmp.get_ChName(1)),tmp.get_ChStopFrequency(tmp.get_ChName(1)),tmp.get_ChDuration(tmp.get_ChName(1)),tmp.get_RefClockValue(),tmp.get_ChMode(tmp.get_ChName(1)),tmp.get_ChFTW1(tmp.get_ChName(1)),tmp.get_ChFTW2(tmp.get_ChName(1)),tmp.get_ChDFW(tmp.get_ChName(1)),tmp.get_ChRRC(tmp.get_ChName(1)))
            self.Sign1=self.Sign

            self.RAM_Write(adreSS, 0xC040002 )
            self.RAM_Write(adreSS+1, (self.FTW1) >>16)
            self.RAM_Write(adreSS+2, (self.FTW1-((self.FTW1 >>16)<<16)))
            self.RAM_Write(adreSS+3, 101)
        
            self.CR = self.CR & ~ (3 << 9)#single tone
            self.CR = self.CR & ~ (1 << 8)
        
            self.RAM_Write(adreSS+4,0x8040007 ) ####registre CSR
            self.RAM_Write(adreSS+5,int(self.CR))
            self.RAM_Write(adreSS+6,0)
            self.RAM_Write(adreSS+7,777)


            #############programmtion phase ############################
            self.PAR1=int(np.ceil(tmp.get_ChStartPhase(tmp.get_ChName(1))*2**14/360))

            self.RAM_Write(adreSS+8,0x4040000 ) ####registre PAR1
            self.RAM_Write(adreSS+9,int(self.PAR1) <<16 )
            self.RAM_Write(adreSS+10,0 )
            self.RAM_Write(adreSS+11,0 )
       

            tmp=seq[int(_seq_)].Seq_Get(i-1)
            self.Calc_Ramp(tmp.get_ChStartFrequency(tmp.get_ChName(1)),tmp.get_ChStopFrequency(tmp.get_ChName(1)),tmp.get_ChDuration(tmp.get_ChName(1)),tmp.get_RefClockValue(),tmp.get_ChMode(tmp.get_ChName(1)),tmp.get_ChFTW1(tmp.get_ChName(1)),tmp.get_ChFTW2(tmp.get_ChName(1)),tmp.get_ChDFW(tmp.get_ChName(1)),tmp.get_ChRRC(tmp.get_ChName(1)))
           
            self.RAM_Write(adreSS+12,0x80000 |(titi.Sign1 <<17) |(self.Mode <<16)) ####registre CSR
            self.RAM_Write(adreSS+13,0)
            self.RAM_Write(adreSS+14,1)
            self.RAM_Write(adreSS+15,int(self.COUNT*self.SRRC/(self.get_UpdtDelay()+1)))


            ####prog de la premiere rampe sans update #################################
        
            adreSS=adreSS+16
      
            self.Mode=0 # la premiere rampe est toujours en mode 0
            tmp=seq[int(_seq_)].Seq_Get(0)
            self.Calc_Ramp(tmp.get_ChStartFrequency(tmp.get_ChName(1)),tmp.get_ChStopFrequency(tmp.get_ChName(1)),tmp.get_ChDuration(tmp.get_ChName(1)),tmp.get_RefClockValue(),tmp.get_ChMode(tmp.get_ChName(1)),tmp.get_ChFTW1(tmp.get_ChName(1)),tmp.get_ChFTW2(tmp.get_ChName(1)),tmp.get_ChDFW(tmp.get_ChName(1)),tmp.get_ChRRC(tmp.get_ChName(1)))
            self.Sign1=self.Sign

                
            if(self.Sign1==1):
                # pente montante
   
                self.RAM_Write(adreSS, 0xC040002 )
                self.RAM_Write(adreSS+1, (self.FTW1) >>16)
                self.RAM_Write(adreSS+2, (self.FTW1-((self.FTW1 >>16)<<16)))
                self.RAM_Write(adreSS+3, 1111)

                self.RAM_Write(adreSS+4, 0xC040003 )
                self.RAM_Write(adreSS+5, (self.FTW2) >>16)
                self.RAM_Write(adreSS+6, (self.FTW2-((self.FTW2 >>16)<<16)))
                self.RAM_Write(adreSS+7, 200)

            if (self.Sign1==0 and self.Mode==0) :
                #pente descendante
    
                self.RAM_Write(adreSS, 0xC040002 )
                self.RAM_Write(adreSS+1, (self.FTW2) >>16)
                self.RAM_Write(adreSS+2, (self.FTW2-((self.FTW2 >>16)<<16)))
                self.RAM_Write(adreSS+3, 100)

                self.RAM_Write(adreSS+4, 0xC040003 )
                self.RAM_Write(adreSS+5, (self.FTW1) >>16)
                self.RAM_Write(adreSS+6, (self.FTW1-((self.FTW1 >>16)<<16)))
                self.RAM_Write(adreSS+7, 200)

            if (self.Sign1==0 and self.Mode==1) :

                self.RAM_Write(adreSS, 0xC040002 )
                self.RAM_Write(adreSS+1, (self.FTW1) >>16)
                self.RAM_Write(adreSS+2, (self.FTW1-((self.FTW1 >>16)<<16)))
                self.RAM_Write(adreSS+3, 100)

                self.RAM_Write(adreSS+4, 0xC040003 )
                self.RAM_Write(adreSS+5, (self.FTW2) >>16)
                self.RAM_Write(adreSS+6, (self.FTW2-((self.FTW2 >>16)<<16)))
                self.RAM_Write(adreSS+7,200)


            self.RAM_Write(adreSS+8, 0xC040004 )

            if (self.Sign1==0 and self.Mode==1) :
            
                t=self.SDFW ^ 0xFFFFFFFFFFFF # on inverse tous les bits +1
                t=t+1
                tM=(t & 0xFFFFFFFF0000)>>16
                tL=(t & 0xFFFF)
    
                self.RAM_Write(adreSS+9, tM)
                self.RAM_Write(adreSS+10, tL)
            else :
                tM=(titi.SDFW  & 0xFFFFFFFF0000)>>16
                tL=(titi.SDFW  & 0xFFFF)
                self.RAM_Write(adreSS+9, tM)
                self.RAM_Write(adreSS+10, tL)

            self.RAM_Write(adreSS+11, 300)


            self.RAM_Write(adreSS+12,0x6040006 )
            self.RAM_Write(adreSS+13,int(self.SRRC)<<8)
            self.RAM_Write(adreSS+14,0)
            self.RAM_Write(adreSS+15,400)

            if (tmp.get_ChMode(tmp.get_ChName(1))=="Single"):
                self.CR = self.CR & ~ (3 << 9)
            else : 
                self.CR = self.CR & ~ (3 << 9)
                self.CR = self.CR | (self.Mode+2)<< 9 #modulation
                self.CR = self.CR & ~ (1 << 8)

            self.RAM_Write(adreSS+16,0x8040007 ) ####registre CSR
            self.RAM_Write(adreSS+17,int(self.CR))
            self.RAM_Write(adreSS+18,0)
            self.RAM_Write(adreSS+19,500)

            #############programmtion phase ############################
            self.PAR1=int(np.ceil(tmp.get_ChStartPhase(tmp.get_ChName(1))*2**14/360))

            self.RAM_Write(adreSS+20,0x4040000 ) ####registre PAR1
            self.RAM_Write(adreSS+21,int(self.PAR1) <<16 )
            self.RAM_Write(adreSS+22,0 )
            self.RAM_Write(adreSS+23,0 )
        
            self.RAM_Write(adreSS+24, 0x100000 |(self.Sign1 <<17) |(self.Mode <<16))
        





obj[0]=Wfm()
obj[0].set_ChName(1,'V1')
obj[0].set_ChEnable('V1',1)
obj[0].set_ChName(2,'V2')
obj[0].set_ChEnable('V2',0)
obj[0].set_RefClock(300000000)
obj[0].set_ChStartFrequency('V1', 23000000)
obj[0].set_ChStopFrequency('V1',  20000000)
obj[0].set_ChStartFrequency('V2', 6000000)
obj[0].set_ChStopFrequency('V2',  14000000)
obj[0].set_ChDuration('V1',1)
obj[0].set_ChDuration('V2',0.00004)
obj[0].set_ChMode('V1','Sweep')
obj[0].set_ChMode('V2','Sweep')

obj[1]=Wfm()
obj[1].set_ChName(1,'V1')
obj[1].set_ChEnable('V1',1)
obj[1].set_ChName(2,'V2')
obj[1].set_ChEnable('V2',0)
obj[1].set_RefClock(300000000)
obj[1].set_ChStartFrequency('V1',43000000)
obj[1].set_ChStopFrequency('V1', 40000000)
obj[1].set_ChStartFrequency('V2',30000000)
obj[1].set_ChStopFrequency('V2',40000000)
obj[1].set_ChDuration('V1',2)
obj[1].set_ChDuration('V2',0.00002)
obj[1].set_ChMode('V1','Single')
obj[1].set_ChMode('V2','Sweep')

obj[2]=Wfm()
obj[2].set_ChName(1,'V1')
obj[2].set_ChEnable('V1',1)
obj[2].set_ChName(2,'V2')
obj[2].set_ChEnable('V2',0)
obj[2].set_RefClock(300000000)
obj[2].set_ChStartFrequency('V1',60000000)
obj[2].set_ChStopFrequency('V1', 70000000)
obj[2].set_ChStartFrequency('V2',40000000)
obj[2].set_ChStopFrequency('V2',50000000)
obj[2].set_ChDuration('V1',1)
obj[2].set_ChDuration('V2',0.50002)
obj[2].set_ChMode('V1','Single')
obj[2].set_ChMode('V2','Sweep')

obj[3]=Wfm()
obj[3].set_ChName(1,'V1')
obj[3].set_ChEnable('V1',1)
obj[3].set_ChName(2,'V2')
obj[3].set_ChEnable('V2',0)
obj[3].set_RefClock(300000000)
obj[3].set_ChStartFrequency('V1',80000000)
obj[3].set_ChStopFrequency('V1', 90000000)
obj[3].set_ChStartFrequency('V2',40000000)
obj[3].set_ChStopFrequency('V2',50000000)
obj[3].set_ChDuration('V1',1)
obj[3].set_ChDuration('V2',0.50002)
obj[3].set_ChMode('V1','Single')
obj[3].set_ChMode('V2','Sweep')

obj[4]=Wfm()
obj[4].set_ChName(1,'V1')
obj[4].set_ChEnable('V1',1)
obj[4].set_ChName(2,'V2')
obj[4].set_ChEnable('V2',0)
obj[4].set_RefClock(300000000)
obj[4].set_ChStartFrequency('V1', 100000000)
obj[4].set_ChStopFrequency('V1',  90000000)
obj[4].set_ChStartFrequency('V2',40000000)
obj[4].set_ChStopFrequency('V2',50000000)
obj[4].set_ChDuration('V1',0.5)
obj[4].set_ChDuration('V2',0.50002)
obj[4].set_ChMode('V1','Sweep')
obj[4].set_ChMode('V2','Sweep')

seq[0]=Seq()
seq[0].Seq_Add(obj[0])
seq[0].Seq_Add(obj[1])
seq[0].Seq_Add(obj[2])
#seq[0].Seq_Add(obj[3])
#seq[0].Seq_Add(obj[4])

titi=Gen(0)
titi.IP_Reset()
titi.set_SpiClock(10)
titi.set_UpdtClock(20)
titi.set_UpdtDelay(1)
titi.set_TXB(0)
titi.Reset()
titi.set_Optimize_Mode('On')

toto=Gen(1)
toto.IP_Reset()
toto.set_SpiClock(50)
toto.set_UpdtClock(20)
toto.set_UpdtDelay(1)
toto.set_TXB(0)
toto.Reset()
toto.set_Optimize_Mode('On')

titi.set_SYNCCRTL(0)
titi.set_SYNCReset(1)
titi.set_SYNCReset(0)
titi.set_SYNC(70)# freq=20 MHZ/(n+1)
titi.set_SYNCCRTL(1)
titi.set_TXB(1)

toto.set_SYNCCRTL(0)
toto.set_SYNCReset(1)
toto.set_SYNCReset(0)
toto.set_SYNC(70)# freq=20 MHZ/(n+1)
toto.set_SYNCCRTL(1)
toto.set_TXB(1)

titi.Load(0,0,1)
toto.Load(0,0,1)
#titi.Run()
#toto.Run()


## Programmation du FPGA par un fichier de configuration "system_wrapper.bit".
os.system('cat /home/redpitaya/system_wrapper.bit > /dev/xdevcfg')

UDP_Err=Error()

host = '192.168.1.10'
data_payload = 2048
backlog = 5 


# Create a TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = (host, 550)
#print ("Starting up DDS server on %s port %s" % server_address)
sock.bind(server_address)


while True:
    
    sleep(0.01)
 #   data=invoke_process_popen_poll_live("/home/redpitaya/./loopWithSleep.sh")
    data, addr = sock.recvfrom(1024)
   
    
    if data.decode()!='' :
        x=data.decode()
        x=x.split(SEP)
        x[len(x)-1]=x[len(x)-1].rstrip('\n')    
        
        try : 
            index = int(x[0])

        except ValueError:

            if x[0] == 'UDP':

                if x[1] == 'Err_GetSize':
                    tmp = UDP_Err.Err_GetSize()
                    tmp = str(tmp)  # float n'a pas de methode encode
                    os.system('echo ' + tmp + ' > /dev/ttyPS1')

                if x[1] == 'Err_GetMessageSize' and len(x) > 2:
                    tmp = UDP_Err.Err_Message(int(x[2]))
                    os.system('echo ' + tmp + ' > /dev/ttyPS1')

            else:

                UDP_Err.Err_Add(102)
                tmp = '102'
                tmp = str(tmp)  # float n'a pas de methode encode
                os.system('echo ' + tmp + ' > /dev/ttyPS1')

        else :



            ###########################################################################
            # FGenBase
            ###########################################################################
    
            if x[1]=='Wfm' and len(x)==2 :
                obj[index]=Wfm()
    

            if x[1]=='Wfm' and len(x)>2 :

                  
                if x[1]=='Wfm' and x[2]=='set_RefClock' and obj[index] and len(x)==4 :
                    obj[index].set_RefClock(x[3])
        
                if x[1]=='Wfm' and x[2]=='get_RefClockValue' and obj[index] and len(x)==3:
    
                    tmp=obj[index].get_RefClockValue()
                    tmp=str(tmp)# float n'a pas de methode encode
                   #os.system('echo ' + tmp + ' > /dev/ttyPS1')
                    sock.sendto(tmp.encode(), addr)
                                        
                if x[1]=='Wfm' and x[2]=='set_ChName' and obj[index] and len(x)==5 :
                    obj[index].set_ChName(x[3],x[4])
                            
                if x[1]=='Wfm' and x[2]=='get_ChName' and obj[index] and len(x)==4 :
        
                    tmp=obj[index].get_ChName(x[3])
                    #os.system('echo ' + tmp + ' > /dev/ttyPS1')
                    sock.sendto(tmp.encode(), addr)
                
                if x[1]=='Wfm' and x[2]=='set_ChEnable' and obj[index] and len(x)==5 :
        
                    obj[index].set_ChEnable(x[3],x[4])
        
                if x[1]=='Wfm' and x[2]=='get_ChEnable' and obj[index] and len(x)==4 :
        
                    tmp=obj[index].get_ChEnable(x[3])
                    tmp=str(tmp)
                    #os.system('echo ' + tmp + ' > /dev/ttyPS1')
                    sock.sendto(tmp.encode(), addr)

                    
                ###########################################################################
                # StdFunc
                ###########################################################################
        
                if x[1]=='Wfm' and x[2]=='set_ChStartFrequency' and obj[index] and len(x)==5 :
            
                    obj[index].set_ChStartFrequency(x[3],x[4])
    
                if x[1]=='Wfm' and x[2]=='get_ChStartFrequency' and obj[index] and len(x)==4 :
        
                    tmp=obj[index].get_ChStartFrequency(x[3])
                    tmp=str(tmp) # float n'a pas de methode encode
                    #os.system('echo ' + tmp + ' > /dev/ttyPS1')
                    sock.sendto(tmp.encode(), addr)
                    
                if x[1]=='Wfm' and x[2]=='set_ChStartPhase' and obj[index] and len(x)==5 :
        
                    obj[index].set_ChStartPhase(x[3],x[4])
       
                if x[1]=='Wfm' and x[2]=='get_ChStartPhase' and obj[index] and len(x)==4 :
        
                    tmp=obj[index].get_ChStartPhase(x[3])
                    tmp=str(tmp) # float n'a pas de methode encode
                    #os.system('echo ' + tmp + ' > /dev/ttyPS1')
                    sock.sendto(tmp.encode(), addr)
            
                ###########################################################################
                # WfmFunc
                ###########################################################################
        
                if x[1]=='Wfm' and x[2]=='set_ChStopFrequency' and obj[index] and len(x)==5 :
        
                    obj[index].set_ChStopFrequency(x[3],x[4])
    
                if x[1]=='Wfm' and x[2]=='get_ChStopFrequency' and obj[index] and len(x)==4 :
    
                    tmp=obj[index].get_ChStopFrequency(x[3])
                    tmp=str(tmp) # float n'a pas de methode encode
                    #os.system('echo ' + tmp + ' > /dev/ttyPS1')
                    sock.sendto(tmp.encode(), addr)

                     
                if x[1]=='Wfm' and x[2]=='set_ChDuration' and obj[index] and len(x)==5 :
        
                    obj[index].set_ChDuration(x[3],x[4])
    
                if x[1]=='Wfm' and x[2]=='get_ChDuration' and obj[index] and len(x)==4 :
        
                    tmp=obj[index].get_ChDuration(x[3])
                    tmp=str(tmp) # float n'a pas de methode encode
                    #os.system('echo ' + tmp + ' > /dev/ttyPS1')
                    sock.sendto(tmp.encode(), addr)
                    
                if x[1]=='Wfm' and x[2]=='set_ChMode' and obj[index] and len(x)==5 :
        
                    obj[index].set_ChMode(x[3],x[4])
    
                if x[1]=='Wfm' and x[2]=='get_ChMode' and obj[index] and len(x)==4 :
    
                    tmp=obj[index].get_ChMode(x[3])
                    #tmp=str(tmp) # float n'a pas de methode encode
                    #os.system('echo ' + tmp + ' > /dev/ttyPS1')
                    sock.sendto(tmp.encode(), addr)
                    
                if x[1]=='Wfm' and x[2]=='set_ChRSRR' and obj[index] and len(x)==5 :
        
                    obj[index].set_ChRSRR(x[3],x[4])
        
                if x[1]=='Wfm' and x[2]=='get_ChRSRR' and obj[index] and len(x)==4 :
    
                    tmp=obj[index].get_ChRSRR(x[3])
                    tmp=str(tmp) # float n'a pas de methode encode
                    #os.system('echo ' + tmp + ' > /dev/ttyPS1')
                    sock.sendto(tmp.encode(), addr)
                    
                if x[1]=='Wfm' and x[2]=='set_ChFSRR' and obj[index] and len(x)==5 :
        
                    obj[index].set_ChFSRR(x[3],x[4])
        
                if x[1]=='Wfm' and x[2]=='get_ChFSRR'  and obj[index]and len(x)==4 :
    
                    tmp=obj[index].get_ChFSRR(x[3])
                    tmp=str(tmp) # float n'a pas de methode encode
                    #os.system('echo ' + tmp + ' > /dev/ttyPS1')
                    sock.sendto(tmp.encode(), addr)
                    
                if x[1]=='Wfm' and x[2]=='set_ChRDW' and obj[index] and len(x)==5 :
        
                    obj[index].set_ChRDW(x[3],x[4])
        
                if x[1]=='Wfm' and x[2]=='get_ChRDW' and obj[index] and len(x)==4 :
    
                    tmp=obj[index].get_ChRDW(x[3])
                    tmp=str(tmp) # float n'a pas de methode encode
                    #os.system('echo ' + tmp + ' > /dev/ttyPS1')
                    sock.sendto(tmp.encode(), addr)
                    
                if x[1]=='Wfm' and x[2]=='set_ChFDW' and obj[index] and len(x)==5 :
        
                    obj[index].set_ChFDW(x[3],x[4])
        
                if x[1]=='Wfm' and x[2]=='get_ChFDW' and obj[index]  and len(x)==4 :
        
                    tmp=obj[index].get_ChFDW(x[3])
                    tmp=str(tmp) # float n'a pas de methode encode
                    #os.system('echo ' + tmp + ' > /dev/ttyPS1')
                    sock.sendto(tmp.encode(), addr)
       
                if x[1]=='Wfm' and x[2]=='Err_GetSize' and obj[index] and len(x)==3 :
    
                    tmp=obj[index].Err_GetSize()
                    tmp=str(tmp) # float n'a pas de methode encode
                    #os.system('echo ' + tmp + ' > /dev/ttyPS1')
                    sock.sendto(tmp.encode(), addr)
                    
                if x[1]=='Wfm' and x[2]=='Err_Message' and obj[index] and len(x)==4 :
    
                    tmp=obj[index].Err_Message(int(x[3]))
                    tmp=str(tmp) # float n'a pas de methode encode
                    #os.system('echo ' + tmp + ' > /dev/ttyPS1')
                    sock.sendto(tmp.encode(), addr)
                    
                if x[1]=='Wfm' and x[2]=='Err_Clear' and obj[index] and len(x)==3 :
    
                    obj[index].Err_Clear()
     
                if x[1]=='Wfm' and x[2]=='Err_Get' and obj[index] and len(x)==4 :
    
                    tmp=obj[index].Err_Get(int(x[3]))
                    tmp=str(tmp) # float n'a pas de methode encode
                    #os.system('echo ' + tmp + ' > /dev/ttyPS1')
                    sock.sendto(tmp.encode(), addr)

                    
            ###########################################################################
            # Seq
            ###########################################################################
    
            if x[1]=='Seq' and len(x)==2 :
                seq[index]=Seq()
    
            if x[1]=='Seq' and len(x)>2 :
    
                if x[1]=='Seq' and x[2]=='Seq_Add' and seq[index] and obj[int(x[3])] and len(x)==4 :
                    seq[index].Seq_Add(obj[int(x[3])])
            
                if x[1]=='Seq' and x[2]=='Seq_Clear' and seq[index] and len(x)==3 :
                    seq[index].Seq_Clear()
        
                if x[1]=='Seq' and x[2]=='Seq_Insert' and seq[index] and len(x)==5 :
                    seq[index].Seq_Insert(x[3],x[4])
        
                if x[1]=='Seq' and x[2]=='Seq_Del' and seq[index] and len(x)==4 :
                    seq[index].Seq_Del(x[3])
        
                if x[1]=='Seq' and x[2]=='Seq_GetSize' and seq[index] and len(x)==3 :
                    tmp=seq[index].Seq_GetSize()
                    tmp=str(tmp) # float n'a pas de methode encode
                    #os.system('echo ' + tmp + ' > /dev/ttyPS1')
                    sock.sendto(tmp.encode(), addr)
                    
                if x[1]=='Seq' and x[2]=='Seq_Save' and seq[index] and len(x)==4 :
                    seq[index].Seq_Save(x[3])
        
                if x[1]=='Seq' and x[2]=='Seq_Read' and seq[index] and len(x)==4 :
                    seq[index].Seq_Read(x[3])
        
                if x[1]=='Seq' and x[2]=='Err_GetSize' and seq[index] and len(x)==3 :
    
                    tmp=seq[index].Err_GetSize()
                    tmp=str(tmp) # float n'a pas de methode encode
                    #os.system('echo ' + tmp + ' > /dev/ttyPS1')
                    sock.sendto(tmp.encode(), addr)
                    
                if x[1]=='Seq' and x[2]=='Err_Message' and seq[index] and len(x)==4 :
    
                    tmp=seq[index].Err_Message(int(x[3]))
                    tmp=str(tmp) # float n'a pas de methode encode
                    #os.system('echo ' + tmp + ' > /dev/ttyPS1')
                    sock.sendto(tmp.encode(), addr)
                    
                if x[1]=='Seq' and x[2]=='Err_Clear' and seq[index] and len(x)==3 :
    
                    seq[index].Err_Clear()
     
                if x[1]=='Seq' and x[2]=='Err_Get' and seq[index] and len(x)==4 :
        
                    tmp=seq[index].Err_Get(int(x[3]))
                    tmp=str(tmp) # float n'a pas de methode encode
                    #os.system('echo ' + tmp + ' > /dev/ttyPS1')
                    sock.sendto(tmp.encode(), addr)
                    
            ###########################################################################
            # Sweepgen
            ###########################################################################
    
            if x[1]=='Gen' and len(x)==2 :
                gen[index]=Gen()

     
            if x[1]=='Gen' and len(x)>2 :
    
                if x[1]=='Gen' and x[2]=='IP_Reset' and gen[index] and len(x)==3 :
                    gen[index].IP_Reset()
        
                if x[1]=='Gen' and x[2]=='Reset' and gen[index] and len(x)==3 :
                    gen[index].Reset()
        
                if x[1]=='Gen' and x[2]=='Run' and gen[index] and len(x)==3 :
                    gen[index].Run()
        
                if x[1]=='Gen' and x[2]=='Run2' and gen[index] and len(x)==3 :
                    gen[index].Run2()
        
                if x[1]=='Gen' and x[2]=='Update' and gen[index] and len(x)==3 :
                    gen[index].Update()
        
                if x[1]=='Gen' and x[2]=='set_PowerUp' and len(x)==4 :
                    gen[index].set_PowerUp(x[3])
        
               # if x[1]=='Gen' and x[2]=='get_Power' and gen[index] and len(x)==3 :
        
                #    tmp=gen[index].get_Power()
                    #tmp=str(tmp) # float n'a pas de methode encode
                 #   os.system('echo ' + tmp + ' > /dev/ttyPS1')
                    #sock.sendto(tmp.encode(), addr)

                #if x[1]=='Gen' and x[2]=='set_SpiClock' and gen[index] and len(x)==4 :
                #    gen[index].set_SpiClock(int(x[3]))
        
                #if x[1]=='Gen' and x[2]=='get_SpiClock' and gen[index] and len(x)==3 :
        
                #    tmp=gen[index].get_SpiClock()
                #    tmp=str(tmp) # float n'a pas de methode encode
                #    os.system('echo ' + tmp + ' > /dev/ttyPS1')
        
                #if x[1]=='Gen' and x[2]=='set_UpdtClock' and gen[index] and len(x)==4 :
                #    gen[index].set_UpdtClock(int(x[3]))
        
                #if x[1]=='Gen' and x[2]=='get_UpdtClock' and gen[index] and len(x)==3 :
        
                #    tmp=gen[index].get_UpdtClock()
                #    tmp=str(tmp) # float n'a pas de methode encode
                #    os.system('echo ' + tmp + ' > /dev/ttyPS1')
        
                #if x[1]=='Gen' and x[2]=='set_UpdtDelay' and gen[index] and len(x)==4 :
                #    gen[index].set_UpdtDelay(int(x[3]))
        
                #if x[1]=='Gen' and x[2]=='get_UpdtDelay' and gen[index] and len(x)==3 :
        
                #    tmp=gen[index].get_UpdtDelay()
                #    tmp=str(tmp)
                #    os.system('echo ' + tmp + ' > /dev/ttyPS1')
        
                if x[1]=='Gen' and x[2]=='set_Optimize_Mode' and gen[index] and len(x)==4 :
                    gen[index].set_Optimize_Mode(x[3])
        
                if x[1]=='Gen' and x[2]=='get_Optimize_Mode' and gen[index] and len(x)==3 :
        
                    tmp=gen[index].get_Optimize_Mode()
                    #tmp=str(tmp) # float n'a pas de methode encode
                    #os.system('echo ' + tmp + ' > /dev/ttyPS1')
                    sock.sendto(tmp.encode(), addr)
                    
                                  
                if x[1]=='Gen' and x[2]=='RAM_Write' and gen[index] and len(x)==5 :
                    gen[index].RAM_Write(int(x[3]),int(x[4]))
    
                if x[1]=='Gen' and x[2]=='RAM_Read' and gen[index] and len(x)==4 :
                    tmp=gen[index].RAM_Read(int(x[3]))
                    tmp=str(tmp) # float n'a pas de methode encode
                    #os.system('echo ' + tmp + ' > /dev/ttyPS1')
                    sock.sendto(tmp.encode(), addr)
                    
                if x[1]=='Gen' and x[2]=='Err_GetSize' and gen[index] and len(x)==3 :
    
                    tmp=gen[index].Err_GetSize()
                    tmp=str(tmp) # float n'a pas de methode encode
                    #os.system('echo ' + tmp + ' > /dev/ttyPS1')
                    sock.sendto(tmp.encode(), addr)
                    
                if x[1]=='Gen' and x[2]=='Err_Message' and gen[index] and len(x)==4 :
    
                    tmp=gen[index].Err_Message(int(x[3]))
                    tmp=str(tmp) # float n'a pas de methode encode
                    #os.system('echo ' + tmp + ' > /dev/ttyPS1')
                    sock.sendto(tmp.encode(), addr)
                    
                if x[1]=='Gen' and x[2]=='Err_Clear' and gen[index] and len(x)==3 :
    
                    gen[index].Err_Clear()
     
                if x[1]=='Gen' and x[2]=='Err_Get' and gen[index] and len(x)==4 :
    
                    tmp=gen[index].Err_Get(int(x[3]))
                    tmp=str(tmp) # float n'a pas de methode encode
                    #os.system('echo ' + tmp + ' > /dev/ttyPS1')
                    sock.sendto(tmp.encode(), addr)
                    
                if x[1]=='Gen' and x[2]=='Load' and gen[index] and len(x)==4 :
    
                    gen[index].set_SpiClock(1)
                    gen[index].set_UpdtClock(20)
                    gen[index].set_UpdtDelay(1)
                    gen[index].Load(x[3],0,1)

                if x[1]=='Gen' and x[2]=='Mod' and gen[index] and len(x)==5 :

                    gen[index].set_SpiClock(100)
                    gen[index].set_UpdtClock(20)
                    gen[index].set_UpdtDelay(1)
                    if int(x[4])==0 :
                        gen[index].Load(x[3],0,1)
                    else : 
                        gen[index].Load(x[3],x[4],0)




sock.close()        
        



















