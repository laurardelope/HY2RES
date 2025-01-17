from src.base_module import *


class Electrolyzer(Module):

    def __init__(self, param):
        self.model=param["electrolyzer"]["model"]
        self.modelH2=param["electrolyzer"]["modelH2"]
        self.inputs=param["electrolyzer"]["inputs"]

        self.thr_elec_on=param["thr_elec_on"] #100, #W
        self.t_sample=param["t_sample"] #5 seg
        
        self.h2flowmean=param['H2_flow_mean_elec'] #NL/min
        self.Pmean=param['Pmean_elec'] #W

     
        
        if(self.model!="algorithmic"):
            self.RNNmodelPath=param["electrolyzer"][self.model]["modelPath"]
            self.RNNmodel = load_model(self.RNNmodelPath)
            self.RNNmean=param["electrolyzer"][self.model]["mean"]
            self.RNNstd=param["electrolyzer"][self.model]["std"]
            self.RNNdepth=param["electrolyzer"][self.model]["depth"]

            self.RNNmodelPathH2=param["electrolyzer"][self.modelH2]["modelPath"]
            self.RNNmodelH2 = load_model(self.RNNmodelPathH2)
            self.RNNmeanH2=param["electrolyzer"][self.modelH2]["mean"]
            self.RNNstdH2=param["electrolyzer"][self.modelH2]["std"]
            self.RNNdepthH2=param["electrolyzer"][self.modelH2]["depth"]
        
        self.Pelec_a = []
        self.H2tot_a = []
        self.d_a = []
        self.d_h2_a = []
        self.t_on_a = []
        self.t_off_a = []
        self.count=0
        self.t_on_a.append(0)
        self.t_off_a.append(0)

        print("init electrolyzer")

    def run(self,ds):
        if(self.model=="algorithmic"):
            self.runAlgorithmic(ds)
        
        else:
            self.runRNN_separate_P_H2_flow(ds)     
            
    def runAlgorithmic(self,ds):

        if(self.inputs=="real"):
            if(ds.readReal("P_elec")>self.thr_elec_on):
                s_elec=1
            else:
                s_elec=0

        else:
            s_elec=ds.readEst("s_elec")

        if(s_elec>0):
            h2_flow=self.h2flowmean
            P_elec=self.Pmean
        else:
            h2_flow=0
            P_elec=0

        ds.writeEst("h2_flow", h2_flow) 
        ds.writeEst("P_elec", P_elec) 

       
    def reset(self,ds):
        self.s_elec=ds.readReal("s_elec")
        self.P_elec=ds.readReal("P_elec") 
       

    
    def runRNN_separate_P_H2_flow(self,ds):
                
        if(ds.readReal("Breaks")=="OPEN"):
            self.count=0
            self.P_elec=ds.readReal("P_elec")
                       
            if(self.inputs=="real"):
                if(self.P_elec>self.thr_elec_on):
                    Selec=1
                else:
                    Selec=0
            else:
                Selec=ds.readEst('s_elec')

            SelecN=(Selec-self.RNNmean[0])/self.RNNstd[0]

            if(Selec==1):
                t_on=self.t_on_a[-1]+1
                t_off=0
            else:
                t_on=0
                t_off=self.t_off_a[-1]+1
            
            self.t_on_a.append(t_on)
            self.t_off_a.append(t_off)

            t_onN=(t_on-self.RNNmean[2])/self.RNNstd[2]
            t_offN=(t_off-self.RNNmean[3])/self.RNNstd[3]
            
            d_in= [SelecN,t_onN, t_offN]   
        
        else:
           
            if(self.inputs=="real"):
                if(ds.readReal("P_elec")>self.thr_elec_on):
                    Selec=1
                else:
                    Selec=0
            else:
                Selec=ds.readEst('s_elec')
                            
            SelecN=(Selec-self.RNNmean[0])/self.RNNstd[0]
            
            if(Selec==1):
                t_on=self.t_on_a[-1]+1
                t_off=0
            else:
                t_on=0
                t_off=self.t_off_a[-1]+1
            
            self.t_on_a.append(t_on)
            self.t_off_a.append(t_off)

            t_onN=(t_on-self.RNNmean[2])/self.RNNstd[2]
            t_offN=(t_off-self.RNNmean[3])/self.RNNstd[3]

            d_in= [SelecN,t_onN, t_offN]   
            
            if(self.count<self.RNNdepth-1):
                self.P_elec=ds.readReal("P_elec")
                
            else:
                d=[]
                i=1
                while(i<(self.RNNdepth)):
                    d.append(self.d_a[self.count-(self.RNNdepth-i)])
                    i+=1
                d.append(d_in)
                
                aux = tf.expand_dims(tf.convert_to_tensor(d, dtype=tf.float32), axis=0)
                pred= tf.squeeze(self.RNNmodel(aux)).numpy()
                                
                if(self.model=="RNN"):
                    pred=pred[-1]
                
                self.P_elec=pred*self.RNNstd[1]+self.RNNmean[1]
                if(self.P_elec<0):self.P_elec=0
                
                            
        self.d_a.append(d_in)
       
        
        self.Pelec_a.append(self.P_elec)
        
        ds.writeEst("P_elec", self.P_elec) 
        
        ##################################################
        ########### H2 FLOW production estimation ########
        ##################################################

        if(ds.readReal("Breaks")=="OPEN"):
            self.count=0
            self.P_elec=ds.readReal("P_elec")
            h2_inc=0
            h2_flow=ds.readReal("h2_flow")
            h2_tot=ds.readReal("h2_total")
            h2_tot_prev=h2_tot
            
            PelecN=(self.P_elec-self.RNNmeanH2[0])/self.RNNstdH2[0]
            
        else:
                       
            if(self.inputs=="real"):
                h2_tot=ds.readReal("h2_total")
                h2_flow=ds.readReal("h2_flow")
                
            else:
                h2_tot=ds.readEst("h2_total")
                h2_flow=ds.readEst("h2_flow")
            
            PelecN=(self.P_elec-self.RNNmeanH2[0])/self.RNNstdH2[0]

            h2_tot_prev=self.H2tot_a[-1]
            if(self.count<self.RNNdepthH2-1):
                self.P_elec=ds.readReal("P_elec")
                h2_tot=ds.readReal("h2_total")
                h2_flow=ds.readReal("h2_flow")
                
            else:
                d=[]
                i=1
                while(i<(self.RNNdepthH2)):
                    d.append(self.d_h2_a[self.count-(self.RNNdepthH2-i)])
                    i+=1
                d.append(d_in)
                
                aux = tf.expand_dims(tf.convert_to_tensor(d, dtype=tf.float32), axis=0)
                pred= tf.squeeze(self.RNNmodelH2(aux)).numpy()
                                
                if(self.model=="RNN"):
                    pred=pred[-1]
                
                h2_flow=pred*self.RNNstdH2[1]+self.RNNmeanH2[1]
                if(h2_flow<0):
                    h2_flow=0
                            
        self.d_h2_a.append(d_in)
       
        
        self.count+=1
        
        h2_inc=h2_flow/3600*self.t_sample
        self.H2tot_a.append(h2_tot_prev+h2_inc)
        ds.writeEst("h2_elec", h2_inc) 
        ds.writeEst("h2_flow", h2_flow) 
        ds.writeEst("h2_total", h2_tot_prev+h2_inc) 
        



