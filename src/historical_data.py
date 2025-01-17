from src.base_module import *


class HistoricalData(Module):
    def __init__(self):
        print("Init historical data")
        
        #Define data frame
        #self.dfh= pd.DataFrame()
        self.index=0
    
    def reset(self,ds):
        COL_NAMES=ds.getKeysEst()
        self.dfh=pd.DataFrame(columns=COL_NAMES, index=[self.index])

        COL_NAMES=ds.getKeysReal()
        self.dfhreal=pd.DataFrame(columns=COL_NAMES, index=[self.index])
        
        print("Reset historical data OK")

    def read(self):
        print("Read data")
    
    def write(self,ds):
        
        estValues=[]
        realValues=[]
        
        for x in ds.getKeysEst():
            estValues.append(ds.readEst(x))

                    
        self.dfh.loc[self.index]=estValues

        for x in ds.getKeysReal():
            realValues.append(ds.readReal(x))
                    
        self.dfhreal.loc[self.index]=realValues
        self.index=self.index+1
        
        
    def printCsv(self, param):
        self.dfh.to_csv(param["csv_path_out"])

    def validate(self, param):

        #Inverter:
        rmse= ((self.dfh['P_car']- self.dfhreal['P_car']) ** 2).mean()**0.5
        
        if(self.dfhreal['P_car'].max() == self.dfhreal['P_car'].min()):
            nrmse=0
        else:
            nrmse = rmse/(self.dfhreal['P_car'].max() - self.dfhreal['P_car'].min())   
        
        print(f'P_car NRMSE= {nrmse}') 
        
        rmse= ((self.dfh['P_des']- self.dfhreal['P_des']) ** 2).mean()**0.5
        
        if(self.dfhreal['P_des'].max() == self.dfhreal['P_des'].min()):
            nrmse=0
        else:
            nrmse = rmse/(self.dfhreal['P_des'].max() - self.dfhreal['P_des'].min())   
        
        print(f'P_des NRMSE= {nrmse}') 

        rmse= ((self.dfh['P_imp']- self.dfhreal['P_imp']) ** 2).mean()**0.5
        
        if(self.dfhreal['P_imp'].max() == self.dfhreal['P_imp'].min()):
            nrmse=0
        else:
            nrmse = rmse/(self.dfhreal['P_imp'].max() - self.dfhreal['P_imp'].min())   
        
        print(f'P_imp NRMSE= {nrmse}')

        rmse= ((self.dfh['P_exp']- self.dfhreal['P_exp']) ** 2).mean()**0.5
        
        if(self.dfhreal['P_exp'].max() == self.dfhreal['P_exp'].min()):
            nrmse=0
        else:
            nrmse = rmse/(self.dfhreal['P_exp'].max() - self.dfhreal['P_exp'].min())   
        
        print(f'P_exp NRMSE= {nrmse}')


        #Battery:
        rmse= ((self.dfh['SOC']- self.dfhreal['SOC']) ** 2).mean()**0.5
        
        if(self.dfhreal['SOC'].max() == self.dfhreal['SOC'].min()):
            nrmse=0
        else:
            nrmse = rmse/(self.dfhreal['SOC'].max() - self.dfhreal['SOC'].min())   
        
        print(f'SOC NRMSE= {nrmse}') 

        


         #Electrolyzer:
        rmse= ((self.dfh['P_elec']- self.dfhreal['P_elec']) ** 2).mean()**0.5
        
        if(self.dfhreal['P_elec'].max() == self.dfhreal['P_elec'].min()):
            nrmse=0
        else:
            nrmse = rmse/(self.dfhreal['P_elec'].max() - self.dfhreal['P_elec'].min())   
        
        print(f'P_elec NRMSE= {nrmse}') 

        rmse= ((self.dfh['h2_flow']- self.dfhreal['h2_flow']) ** 2).mean()**0.5
        
        if(self.dfhreal['h2_flow'].max() == self.dfhreal['h2_flow'].min()):
            nrmse=0
        else:
            nrmse = rmse/(self.dfhreal['h2_flow'].max() - self.dfhreal['h2_flow'].min())   
        
        print(f'h2_flow NRMSE= {nrmse}') 


        for i in range(self.dfhreal['h2_total'].count()):
            if(i>0):
                self.dfhreal.loc[i,'h2_elec']=self.dfhreal.loc[i,'h2_total']-self.dfhreal.loc[i-1,'h2_total']
                if(self.dfhreal.loc[i,'h2_elec']>1):
                    print(self.dfh.iloc[i]['datetime'])
                if(self.dfhreal.loc[i,'h2_elec']<0):
                    print(self.dfhreal.iloc[i]['datetime'])
       
        rmse= ((self.dfh['h2_elec']- self.dfhreal['h2_elec']) ** 2).mean()**0.5
        
        if(self.dfhreal['h2_elec'].max() == self.dfhreal['h2_elec'].min()):
            nrmse=0
        else:
            nrmse = rmse/(self.dfhreal['h2_elec'].max() - self.dfhreal['h2_elec'].min()) 
        
        print(f'H2_elec NRMSE= {nrmse}') 

        #H2Storage:
        
        rmse= ((self.dfh['pres_buf']- self.dfhreal['pres_buf']) ** 2).mean()**0.5
        if(self.dfhreal['pres_buf'].max() == self.dfhreal['pres_buf'].min()):
            nrmse=0
        else:
            nrmse = rmse/(self.dfhreal['pres_buf'].max() - self.dfhreal['pres_buf'].min())   
        print(f'pres_buf NRMSE= {nrmse}') 

        rmse= ((self.dfh['pres_comp']- self.dfhreal['pres_comp']) ** 2).mean()**0.5
        if(self.dfhreal['pres_comp'].max() == self.dfhreal['pres_comp'].min()):
            nrmse=0
        else:
            nrmse = rmse/(self.dfhreal['pres_comp'].max() - self.dfhreal['pres_comp'].min()) 
        print(f'pres_comp NRMSE= {nrmse}')  
        
        rmse= ((self.dfh['P_comp']- self.dfhreal['P_comp']) ** 2).mean()**0.5
        if(self.dfhreal['P_comp'].max() == self.dfhreal['P_comp'].min()):
            nrmse=0
        else:
            nrmse = rmse/(self.dfhreal['P_comp'].max() - self.dfhreal['P_comp'].min())  
        print(f'P_comp NRMSE= {nrmse}') 
        
       
         #Fuel Cell:
        rmse= ((self.dfh['P_pila']- self.dfhreal['P_pila']) ** 2).mean()**0.5
        
        if(self.dfhreal['P_pila'].max() == self.dfhreal['P_pila'].min()):
            nrmse=0
        else:
            nrmse = rmse/(self.dfhreal['P_pila'].max() - self.dfhreal['P_pila'].min())   
        
        print(f'P_pila NRMSE= {nrmse}') 

        rmse= ((self.dfh['h2_flow_pila']- self.dfhreal['h2_flow_pila']) ** 2).mean()**0.5
        
        if(self.dfhreal['h2_flow_pila'].max() == self.dfhreal['h2_flow_pila'].min()):
            nrmse=0
        else:
            nrmse = rmse/(self.dfhreal['h2_flow_pila'].max() - self.dfhreal['h2_flow_pila'].min())   
        
        print(f'h2_flow_pila NRMSE= {nrmse}') 

        #PLC:
        thr_elec_on=param["thr_elec_on"]
        thr_comp_on=param["thr_comp_on"]
        thr_pila_on=param["thr_pila_on"]
        
        self.dfhreal['s_elec']=0
        self.dfhreal['s_comp']=0
        self.dfhreal['s_pila']=0

        self.dfhreal.loc[self.dfhreal['P_elec']>thr_elec_on, 's_elec']=1
        self.dfhreal.loc[self.dfhreal['P_comp']>thr_comp_on, 's_comp']=1
        self.dfhreal.loc[self.dfhreal['P_pila']>thr_pila_on, 's_pila']=1
      
        rmse= ((self.dfh['s_elec']- self.dfhreal['s_elec']) ** 2).mean()**0.5
        
        if(self.dfhreal['s_elec'].max() == self.dfhreal['s_elec'].min()):
            nrmse=0
        else:
            nrmse = rmse/(self.dfhreal['s_elec'].max() - self.dfhreal['s_elec'].min())   
        
        print(f's_elec NRMSE= {nrmse}') 

        rmse= ((self.dfh['s_comp']- self.dfhreal['s_comp']) ** 2).mean()**0.5
        
        if(self.dfhreal['s_comp'].max() == self.dfhreal['s_comp'].min()):
            nrmse=0
        else:
            nrmse = rmse/(self.dfhreal['s_comp'].max() - self.dfhreal['s_comp'].min())   
        
        print(f's_comp NRMSE= {nrmse}') 

        rmse= ((self.dfh['s_pila']- self.dfhreal['s_pila']) ** 2).mean()**0.5
        
        if(self.dfhreal['s_pila'].max() == self.dfhreal['s_pila'].min()):
            nrmse=0
        else:
            nrmse = rmse/(self.dfhreal['s_pila'].max() - self.dfhreal['s_pila'].min())   
        
        print(f's_pila NRMSE= {nrmse}') 

         
       



      


