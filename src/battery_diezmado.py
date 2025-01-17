from src.base_module import *


class BatteryD(Module):

    def __init__(self, param):
        
        self.maxp=param["max_cap"] #kwh
        self.tsample=param["t_sample"] #5 #seg
        self.tsample_ratio=param["t_sample_ratio"]
        self.soc_a = [] 
        self.soc_a.append(0)

        self.timestamp_a = [] 
        self.timestamp_a.append(0)
        self.model=param["battery"]["model"]
        self.inputs=param["battery"]["inputs"]

        self.SOC_max=param["SOC_max"]
        self.SOC_min=param["SOC_min"]

        if(self.model!="algorithmic"):
            self.RNNmodelPath=param["battery"][self.model]["modelPath"]
            self.RNNmodel = load_model(self.RNNmodelPath)
            self.RNNmean=param["battery"][self.model]["mean"]
            self.RNNstd=param["battery"][self.model]["std"]
            self.RNNdepth=param["battery"][self.model]["depth"]

            self.socN_a = [] 
            self.socN_a.append(0)
            self.d_a = []
            self.count=0

            self.d_rate=param["d_rate"]
            self.d_index=0
            self.pcarsum=0
            self.pdessum=0
        
        print("init battery")
    
    def run(self,ds):
        if(self.model=="algorithmic"):
            self.runAlgorithmic(ds)   
        else:
            self.runRNN(ds)  

    def runAlgorithmic(self,ds):

        timestamp=ds.readEst("datetime")

        if(ds.readReal("Breaks")=="OPEN"):
            self.reset(ds)
        else:
            self.soc=self.soc_a[-1]         #Float
            
            if(self.inputs=="real"):
                pdes=ds.readReal("P_des")
                pcar=ds.readReal("P_car")
            else:
                pdes=ds.readEst("P_des")
                pcar=ds.readEst("P_car")
            
            pcar_pila=ds.readEst("P_car_pila")
            
            delta_t=timestamp-self.timestamp_a[-1]
            self.tsample=delta_t.seconds*self.tsample_ratio
      
            deltap=pcar-pdes+pcar_pila
            delta_soc= (deltap*self.tsample)/(self.maxp*3600)*100
            self.soc=self.soc+delta_soc
            if(self.soc>100):
                self.soc=100
            if(self.soc<10):
                self.soc=10

        self.soc_a.append(self.soc)
        self.timestamp_a.append(timestamp)   

        ds.writeEst("SOC", math.ceil(self.soc)) #Save rounded value (Up)
        
        print("Run battery: OK")
       

    
    def runRNN(self,ds):
        
        if(self.inputs=="real"):
            pdes=ds.readReal("P_des")
            pcar=ds.readReal("P_car")
                            
        else:
            pdes=ds.readEst("P_des")
            pcar=ds.readEst("P_car")

        soc_real=ds.readReal ("SOC")
        
        if(ds.readReal("Breaks")=="OPEN"):
            self.soc=soc_real
        else:
            self.soc=self.soc_a[-1]
        
        self.pcarsum+=pcar
        self.pdessum+=pdes
      
        
        if(self.d_index==(self.d_rate-1)):  #Decimation 
            

            pcarN=(self.pcarsum-self.RNNmean[0])/self.RNNstd[0]
            pdesN=(self.pdessum-self.RNNmean[1])/self.RNNstd[1]
            soc_realN=(soc_real-self.RNNmean[2])/self.RNNstd[2]
                            
            if(ds.readReal("Breaks")=="OPEN"):
                self.count=0
                self.soc=soc_real

                soc_prevN=(self.soc-self.RNNmean[2])/self.RNNstd[2]
                d_in= [pcarN,pdesN, soc_prevN]  
                
            else:
                
                soc_prevN=(self.soc_a[-1]-self.RNNmean[2])/self.RNNstd[2]
            
                d_in= [pcarN,pdesN, soc_prevN]
                          
                if(self.count<self.RNNdepth-1):
                    self.soc=ds.readReal("SOC")
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
                    
                    self.soc=pred*self.RNNstd[2]+self.RNNmean[2]
                    if(self.soc>self.SOC_max):
                        self.soc=self.SOC_max
                    if(self.soc<self.SOC_min):
                        self.soc=self.SOC_min
                                
            self.d_a.append(d_in)
            self.count+=1
           
            #Reset counter for decimation:
            self.pcarsum=0
            self.pdessum=0
            self.d_index=-1
       
        self.soc_a.append(self.soc)
       
        self.d_index+=1
        
        ds.writeEst("SOC", math.ceil(self.soc)) #Save rounded value (Up)
   





    def runDNN(self,ds): #DELETE

        if(self.inputs=="real"):
            pdes=ds.readReal("P_des")
            pcar=ds.readReal("P_car")
        else:
            pdes=ds.readEst("P_des")
            pcar=ds.readEst("P_car")

        if(ds.readReal("Breaks")=="OPEN"):
            self.reset(ds)
            d= [[(pcar-self.RNNmean[0])/self.RNNstd[0],(pdes-self.RNNmean[1])/self.RNNstd[1], (self.soc-self.RNNmean[2])/self.RNNstd[2]]]
        else:
            #RNNmodel = load_model(self.RNNmodel)
            #print(RNNmodel)

            
            SOC_prev=self.soc_a[-1]

            d= [[(pcar-self.RNNmean[0])/self.RNNstd[0],(pdes-self.RNNmean[1])/self.RNNstd[1], (SOC_prev-self.RNNmean[2])/self.RNNstd[2]]]

            aux = tf.expand_dims(tf.convert_to_tensor(d, dtype=tf.float32), axis=0)
            print(aux)
            pred= tf.squeeze(self.RNNmodel(aux)).numpy()
            
            self.soc=pred*self.RNNstd[2]+self.RNNmean[2]
            
        self.soc_a.append(self.soc)
        self.d_a.append(d)
        print(self.soc)
        ds.writeEst("SOC", math.ceil(self.soc)) #Save rounded value (Up)
        print("Run battery: OK")
                

    def reset(self,ds):
        self.soc=ds.readReal("SOC")
        
    