from src.base_module import *


class Inverter(Module):

    def __init__(self, param):
        self.max_pw_bat_car= param['max_pw_bat_car']
        self.max_pw_bat_des= param['max_pw_bat_des']
        self.model=param["inverter"]["model"]
        self.inputs=param["inverter"]["inputs"]
        
        if(self.model!="algorithmic"):
            self.RNNmodelPath=param["inverter"][self.model]["modelPath"]
            self.RNNmodel = tf.saved_model.load(self.RNNmodelPath)
            self.RNNmean=param["inverter"][self.model]["mean"]
            self.RNNstd=param["inverter"][self.model]["std"]
            self.RNNdepth=param["inverter"][self.model]["depth"]
        
        self.d_a = []
        self.count=0
        print("init inverter")

    def run(self,ds):
        if(self.model=="algorithmic"):
            self.runAlgorithmic(ds)
        
        else:
            self.runRNN(ds)   

    def runAlgorithmic(self,ds):
        
        if(self.inputs=="real"):
            ppan=ds.readReal('P_pan')
            pviv=ds.readReal('P_viv')
            soc=ds.readReal('SOC')
            pelec=ds.readReal('P_elec')
            pcomp=ds.readReal('P_comp')
            ppur=ds.readReal('P_pur')
            ppila=ds.readReal('P_pila')
        else:
            ppan=ds.readEst('P_pan')
            pviv=ds.readEst('P_viv')
            soc=ds.readEst('SOC')
            pelec=ds.readEst('P_elec')
            pcomp=ds.readEst('P_comp')
            ppur=ds.readEst('P_pur')
            ppila=ds.readEst('P_pila')
        
        self.pcar=0
        self.pdes=0
        self.pexp=0
        self.pimp=0
        self.pcar_pila=0
        self.pinv_pila=0

        pcon=pviv+pelec+pcomp+ppur 

        if(ppan>pcon): #Day mode: energy excess
        
            pexc=ppan-pcon
            self.pcar_pila=ppila
            self.pinv_pila=0
            if(soc<100): 
                self.pcar=min(self.max_pw_bat_car,pexc)
                pexc=pexc-self.pcar
        
            if(pexc>0):
                self.pexp=pexc

        else:  #Night mode: ppan<pcon
            pdef=pcon-(ppan+ppila) 
            if(pdef<0):            
                self.pinv_pila=ppan-pcon
                self.pcar_pila=ppila-self.pinv_pila
            if(pdef>0):
                self.pinv_pila=ppila
                self.pcar_pila=0
                if (soc>0):
                    self.pdes=min(self.max_pw_bat_des,pdef)
                    pdef=pdef-self.pdes
        
                if(pdef>0):
                    self.pimp=pdef
        
        ds.writeEst('P_car',self.pcar)
        ds.writeEst('P_des',self.pdes)
        ds.writeEst('P_exp',self.pexp)
        ds.writeEst('P_imp',self.pimp)
        ds.writeEst('P_car_pila', self.pcar_pila )  

        print("Run inverter: OK")

    def reset(self,ds):
        self.pcar=ds.readReal("P_car") 
        self.pdes=ds.readReal("P_des") 
        self.pimp=ds.readReal("P_imp") 
        self.pexp=ds.readReal("P_exp") 
       
    def runRNN(self,ds):
        
        if(self.inputs=="real"):
            ppan=ds.readReal('P_pan')
            pviv=ds.readReal('P_viv')
            soc=ds.readReal('SOC')
            pelec=ds.readReal('P_elec')
            pcomp=ds.readReal('P_comp')
            ppur=ds.readReal('P_pur')
            ppila=ds.readReal('P_pila')
        else:
            ppan=ds.readEst('P_pan')
            pviv=ds.readEst('P_viv')
            soc=ds.readEst('SOC')
            pelec=ds.readEst('P_elec')
            pcomp=ds.readEst('P_comp')
            ppur=ds.readEst('P_pur')
            ppila=ds.readEst('P_pila')
    
        pcon=pviv+pelec+pcomp+ppur 

        d_in= [(ppan-self.RNNmean[0])/self.RNNstd[0],(pcon-self.RNNmean[1])/self.RNNstd[1], (ppila-self.RNNmean[2])/self.RNNstd[2], (soc-self.RNNmean[3])/self.RNNstd[3]]
        
        if(self.count<self.RNNdepth-1):
            self.reset(ds)
        else:
            d=[]
            i=1
            while(i<(self.RNNdepth)):
                d.append(self.d_a[self.count-(self.RNNdepth-i)])
                i+=1
            d.append(d_in)
            aux = tf.expand_dims(tf.convert_to_tensor(d, dtype=tf.float32), axis=0)
           
            pred=self.RNNmodel.serve(aux).numpy()
            
            if(self.model=="RNN"):
                pred=pred[-1]
                pred=pred[0]
            else:
                pred=pred[0][0]
            
            self.pcar=pred[0]*self.RNNstd[4]+self.RNNmean[4]
            if(self.pcar<0):self.pcar=0
            self.pdes=pred[1]*self.RNNstd[5]+self.RNNmean[5]
            if(self.pdes<0):self.pdes=0
            self.pimp=pred[2]*self.RNNstd[6]+self.RNNmean[6]
            if(self.pimp<0):self.pimp=0
            self.pexp=pred[3]*self.RNNstd[7]+self.RNNmean[7]
            if(self.pexp<0):self.pexp=0
            
           
                            
        self.d_a.append(d_in)
        
        self.count+=1
       
        ds.writeEst("P_car", self.pcar)
        ds.writeEst("P_des", self.pdes) 
        ds.writeEst("P_imp", self.pimp) 
        ds.writeEst("P_exp", self.pexp)  
  