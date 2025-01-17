from src.base_module import *
import datetime

class Plc(Module):

    def __init__(self, param):
        
        self.model=param["PLC"]["model"]
        self.inputs=param["PLC"]["inputs"]
        self.th_soc_start_elec=param['thr_soc_start_h2'] #85
        self.th_soc_stop_elec=param['thr_soc_stop_h2'] #60
        self.th_pcon_stop_elec=param['thr_pcon_stop_h2'] #60
        self.th_soc_start_pila=param['thr_soc_start_pila'] #20
        self.th_soc_stop_pila=param['thr_soc_stop_pila']   #35
        self.th_pdes_start_pila=param['thr_pdes_start_pila'] #2500W
        self.th_start_comp=param['thr_start_comp'] #35 bar
        self.th_stop_comp=param['thr_stop_comp']   #30 bar
        self.max_pres_tanque=param['max_pres_tanque']   #300 bar
        self.max_pres_buffer=param['max_pres_buffer']   #35 bar
        self.thr_pdes_stop_pila=param['thr_pdes_stop_pila']   #2500W
        self.thr_time_stop_pila=param['thr_time_stop_pila']   #5 min

        self.thr_elec_on=param["thr_elec_on"] #100, #W
        self.thr_comp_on=param["thr_comp_on"] #0, #W
        self.thr_pila_on=param["thr_pila_on"] #0, #W
        self.cond=0
        self.selec_a = []
        self.spila_a = []
        self.scomp_a = []
        self.t_pdes_low_a= [] #Time with Pdes <2500W
        self.t_pdes_low_a.append(0)
        self.timestamp_a = [] 
        self.timestamp_a.append(0)
        self.selec_a.append(0)
        self.spila_a.append(0)
        self.scomp_a.append(0)
       

        print("init PLC")
    
    def run(self,ds):
        # if(ds.readReal("P_elec")>self.thr_elec_on):
        #     selec=1
        # else:
        #     selec=0
        
        # if(ds.readReal("P_comp")>self.thr_comp_on):
        #     scomp=1
        # else:
        #     scomp=0
        # if(ds.readReal("P_pila")>self.thr_pila_on):
        #     spila=1
        # else:
        #     spila=0

        # ds.writeReal("s_elec", selec)
        # ds.writeReal("s_comp", scomp)
        # ds.writeRealt("s_pila", spila)

        if(self.model=="algorithmic"):
            self.runAlgorithmic(ds)     

    def runAlgorithmic(self,ds):

        if(ds.readReal("Breaks")=="OPEN"):
            self.reset(ds)

        
        self.selec=0
        self.spila=0
        self.scomp=0
        self.spur=0
      
        #Determine previous state of fuel cell and electrolyzer
      
        spila_prev=self.spila_a[-1]
        selec_prev=self.selec_a[-1]
        scomp_prev=self.scomp_a[-1]
        
        self.P_elec=ds.readReal("P_elec")

        #Leer valores actuales de las variables
        if(self.inputs=="real"):
            soc=ds.readReal("SOC")
            pexp=ds.readReal("P_exp")
            pdes=ds.readReal("P_des")
            ppan=ds.readReal("P_pan")
            pcon=ds.readReal("P_viv")
            pres_buff=ds.readReal("pres_buf")
            pres_comp=ds.readReal("pres_comp")
            timestamp=ds.readReal("datetime")
            
            
        else:
            soc=ds.readEst("SOC")
            pexp=ds.readEst("P_exp")
            pdes=ds.readEst("P_des")
            ppan=ds.readEst("P_pan")
            pcon=ds.readEst("P_viv")
            pres_buff=ds.readEst("pres_buf")
            pres_comp=ds.readEst("pres_comp")
            timestamp=ds.readEst("datetime")

    
      
        # Electrolyzer behavior:
       
        if(selec_prev==0):
            if((soc>=self.th_soc_start_elec)&(pexp>0)):
                self.selec=1
            else: 
                self.selec=0
        else: # Electrolyzer previously ON
            if((soc<self.th_soc_stop_elec)|((pdes>=ppan)&(pcon>=self.th_pcon_stop_elec))|((pres_buff>=self.max_pres_buffer)&(pres_comp>=self.max_pres_tanque))):
                self.selec=0
            else:
                self.selec=1
        
        # Compressor behavior: Only ON when electrolyzer is ON
        if(self.selec==1):
            if(scomp_prev==0): # Compressor previously OFF
                if(self.selec==1):
                    if((pres_comp<self.max_pres_tanque) and (pres_buff>=self.th_start_comp)):
                        self.scomp=1
            else: # Compressor previously ON
                if((pres_comp>=self.max_pres_tanque) or (pres_buff<self.th_stop_comp)):
                    self.scomp=0
                    
                else:
                    self.scomp=1
              
        # Fuel cell behavior:
 
        if (pdes>=self.thr_pdes_stop_pila):
            self.t_pdes_low_a.append(0)
        else:
            delta_t=timestamp-self.timestamp_a[-1]
            delta_t=delta_t.seconds + self.t_pdes_low_a[-1]
            self.t_pdes_low_a.append(delta_t)
            self.t_pdes_low_a.append(0)

        if(self.selec==1):
            self.spila=0
        else:
            if(spila_prev==0):
                if(soc<self.th_soc_start_pila):
                    self.spila=1
                    self.cond=1
           
                else:
                    if((pcon>(pdes+ppan))&(pdes>=self.th_pdes_start_pila)):
                        self.spila=1
                        self.cond=2
                        print(timestamp)
                        print(self.cond)
                        print(spila_prev)
                    else:
                        self.spila=0
                
            else: #Fuel cell ON
                if(self.cond==1):
                    if((soc>=self.th_soc_stop_pila)):
                        self.spila=0
                    else:
                        self.spila=1
                                                
                else: #(self.cond==2):
                    if(self.t_pdes_low_a[0]>self.thr_time_stop_pila*60):
                        self.spila=0
                      
                    else:
                        self.spila=1
                        
      
        self.selec_a.append(self.selec)
        self.spila_a.append(self.spila)
        self.scomp_a.append(self.scomp)
        self.timestamp_a.append(timestamp)   

        ds.writeEst("s_elec", self.selec)
        ds.writeEst("s_comp", self.scomp)
        ds.writeEst("s_pila", self.spila)

     
    def reset(self,ds):
        if(ds.readReal("P_elec")>self.thr_elec_on):
            selec=1
        else:
            selec=0
        
        if(ds.readReal("P_comp")>self.thr_comp_on):
            scomp=1
        else:
            scomp=0
        if(ds.readReal("P_pila")>self.thr_pila_on):
            spila=1
        else:
            spila=0
        self.selec_a.append(selec)
        self.spila_a.append(spila)
        self.spila_a.append(scomp)
        self.t_pdes_low_a.append(0)
        self.timestamp_a.append(ds.readEst("datetime"))    
        