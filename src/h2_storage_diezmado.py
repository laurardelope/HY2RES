from src.base_module import *


class H2StorageD(Module):

    def __init__(self, param):
        
        self.maxp=param["max_cap"] #kwh
        self.tsample=param["t_sample"] #5 #seg
        self.tsample_ratio=param["t_sample_ratio"]
        self.buffer_cap= param["buffer_cap"] #bar
        self.tank_cap=param["tank_cap"]    #bar
        self.vol_tanque=param["vol_tanque"] # litros
        self.vol_buffer=param["vol_buffer"] # 2x50 litros
        self.R=param["Rconst"] #L*bar/(K*mol)
        self.temp=param["temp"] #grados kelvin
        self.init=0

        self.Pmean_comp= param["Pmean_comp"] # Compressor mean power (ON) (W)
        self.thr_comp_on=param["thr_comp_on"] #0, #W
        self.thr_elec_on=param["thr_elec_on"] #100, #W

        self.h2_tot_a = []  #NL
        self.h2_tot_a.append(0)
        self.h2b_nl_a = []  #NL
        self.h2b_nl_a.append(0)
        self.h2t_nl_a = []  #NL
        self.h2t_nl_a.append(0)

        self.t_on_elec_a = []  
        self.t_on_elec_a.append(0)

        self.t_on_comp_a = []  
        self.t_on_comp_a.append(0)

        self.t_off_comp_a = []  
        self.t_off_comp_a.append(0)

        self.timestamp_a = [] 
        self.timestamp_a.append(0)
       
        self.model=param["h2Storage"]["model"]
        self.modelPcomp=param["h2Storage"]["modelPcomp"]
        self.modelptank=param["h2Storage"]["modelptank"]
        self.inputs=param["h2Storage"]["inputs"]

        if(self.model!="algorithmic"):
            self.RNNmodelPath=param["h2Storage"][self.model]["modelPath"]
            self.RNNmodel = load_model(self.RNNmodelPath)
            self.RNNmean=param["h2Storage"][self.model]["mean"]
            self.RNNstd=param["h2Storage"][self.model]["std"]
            self.RNNdepth=param["h2Storage"][self.model]["depth"]

            self.RNNmodelPathPcomp=param["h2Storage"][self.modelPcomp]["modelPath"]
            self.RNNmodelPcomp = load_model(self.RNNmodelPathPcomp)
            self.RNNmeanPcomp=param["h2Storage"][self.modelPcomp]["mean"]
            self.RNNstdPcomp=param["h2Storage"][self.modelPcomp]["std"]
            self.RNNdepthPcomp=param["h2Storage"][self.modelPcomp]["depth"]

            self.RNNmodelPathptank=param["h2Storage"][self.modelptank]["modelPath"]
            self.RNNmodelptank = load_model(self.RNNmodelPathptank)
            self.RNNmeanptank=param["h2Storage"][self.modelptank]["mean"]
            self.RNNstdptank=param["h2Storage"][self.modelptank]["std"]
            self.RNNdepthptank=param["h2Storage"][self.modelptank]["depth"]

            self.pres_buf_a = []  #bar
            self.pres_buf_a.append(0)
            self.pres_comp_a = []  #bar
            self.pres_comp_a.append(0)
            self.P_comp_a = []  #bar
            self.P_comp_a.append(0)

            self.d_a = []
            self.d_Pcomp_a = []
            self.d_ptank_a = []
            self.count=0

            self.d_rateH2=param["d_rate_h2"] 
            self.d_index=0

        print("init h2Storage")
    
    def run(self,ds):
        if(self.model=="algorithmic"):
            self.runAlgorithmic(ds)   
        else:
            self.runRNN2_buffer(ds)  

    def runAlgorithmic(self,ds):

        self.temp=ds.readReal("Temperature")+273.15
        
        if(ds.readReal("Breaks")=="OPEN"):
            self.reset(ds)
        else:
            self.h2b_nl=self.h2b_nl_a[-1]
            self.h2t_nl=self.h2t_nl_a[-1]
            if(self.inputs=="real"):
                self.pb=ds.readReal("pres_buf")#-1
                self.pt=ds.readReal("pres_comp")#-1
                if(ds.readReal("P_comp")>self.thr_comp_on):
                    self.s_comp=1
                else:
                    self.s_comp=0
                
                self.h2_inc=ds.readReal("h2_total")- self.h2_tot_a[-1]
                self.h2_tot_a.append(ds.readReal("h2_total"))
            
            else:
                self.pb=ds.readEst("pres_buf")#-1   
                self.pt=ds.readEst("pres_comp")#-1
                
                self.s_comp=ds.readEst("s_comp")
                self.h2_inc=ds.readEst("h2_elec") 
            
            if(self.s_comp==0): #Compressor OFF ->buffer
                self.h2b_nl=self.h2b_nl+self.h2_inc
                
                self.Pcomp=0 

            else:    # Compressor ON -> tank

                self.h2t_nl=self.h2t_nl+self.h2_inc
                
                self.Pcomp=self.Pmean_comp
                
                deltah2=0.02525*2/0.09*self.vol_buffer/(self.R*self.temp) 
               
                print(deltah2)
                
                self.h2b_nl=self.h2b_nl-deltah2
                self.h2t_nl=self.h2t_nl+deltah2
            
            nb=self.h2b_nl*0.09/2 #moles / 1NL=0.09g / 2g=1 mol
            self.pb=nb *self.R* self.temp/(self.vol_buffer)
            nt=self.h2t_nl*0.09/2 #moles / 1NL=0.09g / 2g=1 mol
            self.pt=nt *self.R* self.temp/(self.vol_tanque) 
            
            self.h2b_nl_a.append(self.h2b_nl)
            self.h2t_nl_a.append(self.h2t_nl)

            ds.writeEst("pres_buf", self.pb)
            ds.writeEst("pres_comp", self.pt)
            ds.writeEst("h2b_nl", self.h2b_nl)
            ds.writeEst("h2t_nl", self.h2t_nl)
            ds.writeEst("P_comp", self.Pcomp)

                

    def reset(self,ds):
        self.h2_tot=ds.readReal("h2_total")
        self.P_comp=ds.readReal("P_comp")
        self.pb=ds.readReal("pres_buf")
        self.pt=ds.readReal("pres_comp")
        #self.pb_a.append(self.pb)
        #self.pt_a.append(self.pt)
        
        #self.timestamp_a.append(timestamp)

        self.h2b_nl= self.pb*self.vol_buffer/(self.R*self.temp)/(0.09/2)
        self.h2b_nl_a.append(self.h2b_nl)

        self.h2t_nl= self.pt*self.vol_tanque/(self.R*self.temp)/(0.09/2)
        self.h2t_nl_a.append(self.h2t_nl)

        self.h2_tot_a.append(self.h2_tot)

        ds.writeEst("pres_buf", self.pb)
        ds.writeEst("pres_comp", self.pt)
        ds.writeEst("h2b_nl", self.h2b_nl)
        ds.writeEst("h2t_nl", self.h2t_nl)
        ds.writeEst("P_comp", self.P_comp)

    
    def runRNN2_buffer(self,ds):
        
        self.temp=ds.readReal("Temperature")

        if(self.inputs=="real"):
            if(ds.readReal("P_comp")>self.thr_comp_on):
                self.s_comp=1
            else:
                self.s_comp=0

            if(ds.readReal("P_elec")>self.thr_elec_on):
                self.s_elec=1
            else:
                self.s_elec=0
  
            self.h2_flow=ds.readReal("h2_flow")
            self.h2_tot_a.append(ds.readReal("h2_total"))
                
        else:
            self.s_comp=ds.readEst("s_comp")
            self.s_elec=ds.readEst("s_elec")
            self.h2_flow=ds.readEst("h2_flow") 

        
        if(self.init==0):
            self.pres_buf=ds.readReal("pres_buf")
            self.pres_comp=ds.readReal("pres_comp")
            self.P_comp=ds.readReal("P_comp")
        else:
            self.pres_buf=self.pres_buf_a[-1]
            self.pres_comp=self.pres_comp_a[-1]
            self.P_comp=self.P_comp_a[-1]

        if(self.d_index==(self.d_rateH2-1)):  #Decimation

            if(self.h2_flow>0):
                t_on_elec=self.t_on_elec_a[-1]+1
            else:
                t_on_elec=0
            if(self.s_comp>0):
                t_on_comp=self.t_on_comp_a[-1]+1
                t_off_comp=0
            else:
                t_off_comp=self.t_off_comp_a[-1]+1
                t_on_comp=0
                
            self.t_on_elec_a.append(t_on_elec)
            self.t_on_comp_a.append(t_on_comp)
            self.t_off_comp_a.append(t_off_comp)
        
            s_elecN=(self.s_elec-self.RNNmean[7])/self.RNNstd[7]
            s_compN=(self.s_comp-self.RNNmean[8])/self.RNNstd[8]
            h2_flowN=(self.h2_flow-self.RNNmean[2])/self.RNNstd[2]
            tempN=(self.temp-self.RNNmean[6])/self.RNNstd[6]

            h2_flowptN=(self.h2_flow-self.RNNmeanptank[1])/self.RNNstdptank[1]
            tempptN=(self.temp-self.RNNmeanptank[0])/self.RNNstdptank[0]

            t_on_elecN=(t_on_elec-self.RNNmean[3])/self.RNNstd[3] 
            t_on_compN=(t_on_comp-self.RNNmean[4])/self.RNNstd[4]
            t_off_compN=(t_off_comp-self.RNNmean[5])/self.RNNstd[5]

            t_on_compptN=(t_on_comp-self.RNNmeanptank[2])/self.RNNstdptank[2]
            t_off_compptN=(t_off_comp-self.RNNmeanptank[3])/self.RNNstdptank[3]
            

            if(self.init==0):
                self.count=0
                self.pres_buf=ds.readReal("pres_buf")
                self.pres_comp=ds.readReal("pres_comp")
                self.P_comp=ds.readReal("P_comp")
                
                pres_buf_prevN=(self.pres_buf-self.RNNmean[0])/self.RNNstd[0] 
                pres_comp_prevptN=(self.pres_comp-self.RNNmeanptank[4])/self.RNNstdptank[4]

                P_compN=(self.P_comp-self.RNNmeanptank[5])/self.RNNstdptank[5]

                d_in= [h2_flowN,tempN,t_on_elecN,t_on_compN,pres_buf_prevN] 
                d_inP= [s_compN, h2_flowN,t_on_compN, t_off_compN]
                d_inptank= [P_compN, h2_flowptN, tempptN,t_on_compptN, t_off_compptN,pres_comp_prevptN]
                
                self.init=1 
            else:
                pres_buf_prevN=(self.pres_buf_a[-1]-self.RNNmean[0])/self.RNNstd[0]
                pres_comp_prevptN=(self.pres_comp_a[-1]-self.RNNmeanptank[4])/self.RNNstdptank[4]
                P_compN=(self.P_comp_a[-1]-self.RNNmeanptank[5])/self.RNNstdptank[5]
                
                d_in= [h2_flowN,tempN,t_on_elecN,t_on_compN,pres_buf_prevN]  
                d_inP= [s_compN, h2_flowN,t_on_compN, t_off_compN]
                d_inptank= [P_compN, h2_flowptN, tempptN,t_on_compptN, t_off_compptN,pres_comp_prevptN]
                
                        
                if(self.count<self.RNNdepth-1):
                    self.pres_buf=ds.readReal("pres_buf")
                    self.pres_comp=ds.readReal("pres_comp")
                    self.P_comp=ds.readReal("P_comp")
                else:
                    d=[]
                    d_Pcomp=[]
                    d_ptank=[]
                    i=1
                    while(i<(self.RNNdepth)):
                        d.append(self.d_a[self.count-(self.RNNdepth-i)])
                        i+=1
                    i=1
                    while(i<(self.RNNdepthPcomp)):
                        d_Pcomp.append(self.d_Pcomp_a[self.count-(self.RNNdepthPcomp-i)])
                        i+=1
                    i=1
                    while(i<(self.RNNdepthptank)):
                        d_ptank.append(self.d_ptank_a[self.count-(self.RNNdepthptank-i)])
                        i+=1

                    d.append(d_in)
                    d_Pcomp.append(d_inP)
                    d_ptank.append(d_inptank)
                    aux = tf.expand_dims(tf.convert_to_tensor(d, dtype=tf.float32), axis=0)
                    pred= tf.squeeze(self.RNNmodel(aux)).numpy()

                    auxP = tf.expand_dims(tf.convert_to_tensor(d_Pcomp, dtype=tf.float32), axis=0)
                    predP= tf.squeeze(self.RNNmodelPcomp(auxP)).numpy()
                    auxpt = tf.expand_dims(tf.convert_to_tensor(d_ptank, dtype=tf.float32), axis=0)
                    predpt= tf.squeeze(self.RNNmodelptank(auxpt)).numpy()
                                    
                    if(self.model=="RNN"):
                        pred=pred[-1]
                    if(self.modelPcomp=="RNNPcomp"):
                        predP=predP[-1]
                    if(self.modelptank=="RNNptank"):
                        predpt=predpt[-1]
                    
                   
                    self.pres_buf=pred*self.RNNstd[0]+self.RNNmean[0]
                    if(self.pres_buf<0):self.pres_buf=0

                    self.P_comp=predP*self.RNNstdPcomp[4]+self.RNNmeanPcomp[4]
                    if(self.P_comp<0):self.P_comp=0
                    
                    self.pres_comp=predpt*self.RNNstdptank[4]+self.RNNmeanptank[4]
                    if(self.pres_comp<0):self.pres_comp=0

               
            
            self.d_a.append(d_in)
            self.d_Pcomp_a.append(d_inP)
            self.d_ptank_a.append(d_inptank)

            #Reset counters for decimation:
            self.d_index=-1
            self.count+=1

        self.pres_buf_a.append(self.pres_buf)
        self.pres_comp_a.append(self.pres_comp)
        self.P_comp_a.append(self.P_comp)

        self.d_index+=1
        
        nb=self.pres_buf*self.vol_buffer/(self.R* (self.temp+273.15))
        self.h2b_nl=nb*2/0.09#moles / 1NL=0.09g / 2g=1 mol
        nt=self.pres_comp*self.vol_buffer/(self.R* self.temp+273.15)
        self.h2t_nl=nt*2/0.09#moles / 1NL=0.09g / 2g=1 mol
                
        ds.writeEst("pres_buf", self.pres_buf)
        ds.writeEst("pres_comp", self.pres_comp)
        ds.writeEst("h2b_nl", self.h2b_nl)
        ds.writeEst("h2t_nl", self.h2t_nl)
        ds.writeEst("P_comp", self.P_comp)

    
    