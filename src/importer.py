from src.base_module import *


class Importer(Module):

    def __init__(self,param):
        print ("init importer")
        
        df = pd.read_csv(param["csv_path_in"], sep=',', dtype=float, converters={'datetime':str, 'Breaks': str})
        df['datetime'] = pd.to_datetime(df['datetime'], dayfirst=True)
        
        self.df=df
        self.index=0
       
        
    
    def reset(self):
        print("Reset:Read csv")




    def run(self, ds):
        for x in ds.getKeysReal():
            ds.writeReal(x,self.df.iloc[self.index][str(x)])
        
        ds.writeEst('P_pan',self.df.iloc[self.index]['P_pan'])
        ds.writeEst('P_viv',self.df.iloc[self.index]['P_viv'])
        ds.writeEst('datetime',self.df.iloc[self.index]['datetime'])
        ds.writeEst('Breaks',self.df.iloc[self.index]['Breaks'])
        ds.writeEst('Temperature',self.df.iloc[self.index]['Temperature'])

        if(ds.readReal('Breaks')=="OPEN"):
            ds.writeEst('SOC',self.df.iloc[self.index]['SOC'])
            ds.writeEst('pres_buf',self.df.iloc[self.index]['pres_buf'])
            ds.writeEst('pres_comp',self.df.iloc[self.index]['pres_comp'])
            ds.writeEst('P_elec',self.df.iloc[self.index]['P_elec'])
            ds.writeEst('P_comp',self.df.iloc[self.index]['P_comp'])
            ds.writeEst('P_pila',self.df.iloc[self.index]['P_pila'])
            ds.writeEst('P_pur',self.df.iloc[self.index]['P_pur'])
    
        self.index=self.index+1
        return(self.index)
        