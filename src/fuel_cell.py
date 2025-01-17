from src.base_module import *


class FuelCell(Module):

    def __init__(self, param):

        self.h2flowmean=param['H2_flow_mean_pila'] #NL/min
        self.Pmean=param['Pmean_pila'] #W
        self.thr_pila_on=param["thr_pila_on"] #0, #W
         
        self.model=param["fuelCell"]["model"]
        self.inputs=param["fuelCell"]["inputs"]

        self.modelh2fc=param["fuelCell"]["modelh2fc"]

        if(self.model!="algorithmic"):
            self.RNNmodelPath=param["fuelCell"][self.model]["modelPath"]
            self.RNNmodel = load_model(self.RNNmodelPath)
            print(self.RNNmodelPath)
            self.RNNmean=param["fuelCell"][self.model]["mean"]
            self.RNNstd=param["fuelCell"][self.model]["std"]
            self.RNNdepth=param["fuelCell"][self.model]["depth"]

            self.RNNmodelPathh2fc=param["fuelCell"][self.modelh2fc]["modelPath"]
            self.RNNmodelh2fc = load_model(self.RNNmodelPathh2fc)
            self.RNNmeanh2fc=param["fuelCell"][self.modelh2fc]["mean"]
            self.RNNstdh2fc=param["fuelCell"][self.modelh2fc]["std"]
            self.RNNdepthh2fc=param["fuelCell"][self.modelh2fc]["depth"]

            self.P_pila_a = [] 
            self.P_pila_a.append(0)

            self.t_on_pila_a = []  
            self.t_on_pila_a.append(0)
        
            self.d_a = []
            self.d_h2_a = []
            self.init=0
        
        print("init fuel cell")
    
    def run(self,ds):
        if(self.model=="algorithmic"):
            self.runAlgorithmic(ds)   
        else:
            self.runRNN_ALL(ds)  

    def runAlgorithmic(self,ds):

        if(self.inputs=="real"):
            if(ds.readReal("P_pila")>self.thr_pila_on):
                s_pila=1
            else:
                s_pila=0

        else:
            s_pila=ds.readEst("s_pila")

        if(s_pila>0):
            h2_pila=self.h2flowmean
            P_pila=self.Pmean
        else:
            h2_pila=0
            P_pila=0

        ds.writeEst("h2_flow_pila", h2_pila) 
        ds.writeEst("P_pila", P_pila) 
        
 

    def runRNN_ALL(self,ds):
      
        if(self.inputs=="real"):
            if(ds.readReal("h2_flow_pila")>self.thr_pila_on):
                s_pila=1
            else:
                s_pila=0
                
        else:
            s_pila=ds.readEst("s_pila")


        if(s_pila>0):
            t_on_pila=self.t_on_pila_a[-1]+1
        else:
            t_on_pila=0

        self.t_on_pila_a.append(t_on_pila)

        t_on_pilaN=(t_on_pila-self.RNNmean[3])/self.RNNstd[3]
        s_pilaN=(s_pila-self.RNNmean[0])/self.RNNstd[0]
        
        if(self.init==0):
            self.count=0
            self.P_pila=ds.readReal("P_pila")
            self.h2_flow_pila=ds.readReal("h2_flow_pila")

            d_in= [t_on_pilaN] 
            self.init=1
        else:
            
            d_in= [t_on_pilaN] 
            
           
            if(self.count<self.RNNdepth-1):
                self.P_pila=ds.readReal("P_pila")
                self.h2_flow_pila=ds.readReal("h2_flow_pila")
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
                
                self.P_pila=pred[0]*self.RNNstd[1]+self.RNNmean[1]
                self.h2_flow_pila=pred[1]*self.RNNstd[2]+self.RNNmean[2]

                if(self.P_pila<0):
                    self.P_pila=0
                if(self.h2_flow_pila<0):
                    self.h2_flow_pila=0
                

        self.d_a.append(d_in)
               
        self.count+=1
                    
        ds.writeEst("P_pila", self.P_pila)
        ds.writeEst("h2_flow_pila", self.h2_flow_pila) 
      
    