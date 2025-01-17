class DataStore():
    def __init__(self):
        print("Init data store")

        self.varReal={
            "datetime": -1,
            "Temperature": -1,
            "Breaks": -1,
            "P_pan": -1,
            "P_viv": -1,
            "P_car" : -1,
            "P_des": -1,
            "P_exp" : -1,
            "P_imp": -1,
            "P_elec": -1,
            "P_comp": -1,
            "P_pur": -1,
            "P_pila": -1,
            "SOC": -1,
            "pres_buf": -1,
            "pres_comp": -1,
            "pres_pila": -1,
            "h2_total": -1,    #NL
            "h2_flow": -1,     #NL/h
            # "s_elec":-1,
            # "s_comp":-1,
            # "s_pila":-1
            "h2_flow_pila": -1  #NL/min
            
        }
        
        self.var={
            "datetime": -1,
            "Temperature": -1,
            "Breaks": -1,
            "P_pan": -1,
            "P_viv": -1,
            "P_car" : -1,
            "P_des": -1,
            "P_exp" : -1,
            "P_imp": -1,
            "P_elec": -1,
            "P_comp": -1,
            "P_pur": -1,
            "P_pila": -1,
            "SOC": -1,
            "pres_buf": -1,
            "pres_comp": -1,
            "pres_pila": -1,
            "P_car_pila": -1,
            "s_elec":-1,
            "s_comp":-1,
            "s_pila":-1,
            "h2_total": -1, #NL hidrogeno total generado por el electrolizador
            "h2_flow": -1,     #NL/h hidrógeno generado por el electrolizador
            "h2_elec": -1, #hidrógeno generado por el electrolizador
            "h2b_nl": -1,  #hidrógeno total almacenado en el buffer
            "h2t_nl": -1,   #hidrógeno total almacenado en el tanque
            "h2_flow_pila": -1   #hidrógeno consumido por la pila
        }
    
    def resetReal(self):
        print("Reset data")
        for x in self.varReal:
            self.varReal[x]=-1

    def resetEst(self):
        print("Reset data")
        for x in self.var:
            self.var[x]=-1
    
    def getKeysReal(self):
        return(self.varReal.keys())

    def getKeysEst(self):
        return(self.var.keys())

    def readEst(self,var):
        return(self.var[var])
    
    def writeEst(self, var, value):
        if var in self.var:
            self.var[var]=value
        else:
            print("Variable does not exist")
    
    def readReal(self,var):
        return(self.varReal[var])
    
    def writeReal(self, var, value):
        if var in self.varReal:
            self.varReal[var]=value
        else:
            print("Variable does not exist")
            
    def printEst(self):
        print(self.var)

    def printReal(self):
        print(self.varReal)