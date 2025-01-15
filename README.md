# HY2RES Digital Twin

## Table of contents
1. General Info
2. Getting Started
3. Configuration File
4. Input and output files
5. Acknowlegments

## 1. General Info

![Screenshot of a comment on a GitHub issue showing an image, added in the Markdown, of an Octocat smiling and raising a tentacle.](resources/real-system-architecture.pdf)

## 2. Getting Started

### Dependencies

### Executing program



## 3. Configuration File 

The digital twin can be configured through the config.json file located in the data folder. The file structure is following described:
    
* "csv_path_in": path to the input file with the real values of the signals measured in the physical twin. Its structure is described in section 3 "Input ans output files". 

* "csv_path_out":path to the output file with the values of the signals estimated by the digital twin. Its structure is described in section 3 "Input ans output files". 

* "n_iter": number of iterations to be run by the digital twin, currently 10000.

### Inverter configuration parameters:
* "max_pw_bat_car": Maximum charging battery power [Watts], currently 3000 W.
* "max_pw_bat_des": Maximum discharging battery power [Watts], currently 3200 W. 

### PLC configuration parameters:
*  "thr_soc_start_h2": Battery State of Charge (SOC) threshold to start electrolyzer [%], currently 86%. 
* "thr_soc_stop_h2": Battery SOC threshold to stop electrolyzer [%], currently 60%.  
* "thr_pcon_stop_h2":500, 
* "thr_start_comp": Buffer pressure threshold to start compressor [bar], currently 33.8 bar
* "thr_stop_comp": Buffer pressure thresholdto stop compressor [bar], currently 29.2 bar 
* "max_pres_tanque": Maximum pressure of the buffer [Bar], currently 300 bar.  
* "max_pres_buffer": Maximum pressure of the buffer [Bar], currently 35 bar. 
* "thr_soc_start_pila":Battery SOC threshold to start fuel cell [%], currently 20%.
* "thr_soc_stop_pila":Battery SOC threshold to stop fuel cell [%], currently 35%.
* "thr_pdes_start_pila":Battery discharge power [Bar] threshold to start fuel cell when there is energy deficit, currently 2500 bar.
* "thr_pdes_stop_pila": Battery discharge power [Bar] threshold to stop fuel cell after * * * 
* "thr_time_stop_pila" minutes, currently 2500,   
* "thr_time_stop_pila": Time [minutes] with battery discharge power under "thr_pdes_stop_pila" to stop fuel cell, currently 5 min. 

* "thr_elec_on": Electrolyzer consumed power threshold [W] to consider it is ON when using real inputs, currently 100 W. 
* "thr_comp_on": Compressor consumed power threshold [W] to consider it is ON when using real inputs, currently 0 W.  
* "thr_pila_on": Fuel Cell generated power threshold [W] to consider it is ON when using real inputs, currently 0 W. , 

### Battery configuration parameters:    
* "max_cap": Maximum battery capacity [KW/h], currently 8800 KW/h.  
* "t_sample": Time between samples [seconds], currently 5 seconds.          
* "t_sample_ratio":0.9,  
* "d_rate":  Decimation rate, currently 60, meaning that 1 of 60 samples is remaining.           
* "SOC_max":Maximum battery  State of Charge (SOC) [%], currently 100% .
* "SOC_min":10,

### Electrolyzer configuration parameters:
* "H2_flow_mean_elec": 340,   
* "Pmean_elec": 1700,        

 ### Hydrogen Storage configuration parameters:   
* "d_rate_h2":60,   
* "buffer_cap": 35, 
* "tank_cap":300,   
* "vol_tanque":600, 
* "vol_buffer":100, 
* "Rconst":83.14466e-3,   
* "temp":293.15,          
* "Pmean_comp": 283.5, 

### Fuel Cell configuration parameters:   
* "H2_flow_mean_pila": 20.87, 
* "Pmean_pila": 1882.2,


### Model configuration parameters:  

Each module of the digital twin can run with two types of inputs and 4 different models:
 
* "model": Four models are available, one algorithmic and three based on neural networks.
    - "Algorithmic": Algotithmic model.
    - "DNN": Dense neural network.
    - "CNN": Convolutional neural network.
    - "RNN": Recurrent neural network.

    The following considerations must be taken into account:
    - The PLC module only admits algorithmic model. Because of the nature of its behavior, other models are not considered.
    - At the electrolyzer module, the neural network models associated to the hydrogen flow are named "DNNH2", "CNNH2" and "RNNH2" respectively.
    - At the hydrogen storage module, the neural network models associated to the compressor consumed power are named "DNNPcomp", "CNNPcomp" and "RNNPcomp" respectively. Models associated to the tank pressure are named "DNNptank", "CNNptank" and "RNNptank" respectively.
    - At the fuel cell module, the neural network models associated to the fydrogen consumed flow are named "DNNh2fc", "CNNh2fc" and "RNNh2fc" respectively. 



* "inputs": There are two options:
    - "real": use as input values those real measurements provided in the input file.
    - "est": use as input values those estimated in previous modules or iterations.

Neural networks are defined by the following parameters:

* "modelPath": path to the trained neural network file,
* "mean": Array with the mean value of the input variables used for training the neural network, these variables are the following depending on the component:
    - Inverter: [P_pan, P_con, P_pila, SOC, P_car, P_des, P_imp, P_exp]
    - Battery: [P_car, P_des, SOC]
    - Electrolyzer:
        - Power consumed: [s_elect , P_elec, t_on_elec, t_off_elec]
        - Hydrogen flow: [P_elec, h2flow]
    - Hydrogen storage:
        - Buffer pressure: [pres_buf, h2_flow, t_on_elec, t_on_comp, t_off_comp, temperature, s_elec, s_comp]
     
        - Compressor consumed power: [s_comp, h2_flow,  t_on_comp, t_off_comp, P_comp]
        - Tank pressure: [Temperature, h2_flow, t_on_comp, t_off_comp, pres_comp, P_comp]
    - Fuel Cell:
        - Hydrogen consumed: [s_pila, P_pila, h2_flow_pila]
        - Power generated:[s_pila, P_pila, h2_flow_pila, t_on_pila]

* "std": Array with the standard deviation value of the input variables used for training the neural network, these variables are thefollowing depending on the component: 
    - Inverter: [P_pan, P_con, P_pila, SOC, P_car, P_des, P_imp, P_exp]
    - Battery: [P_car, P_des, SOC]
    - Electrolyzer:
        - Power consumed: [s_elect , P_elec, t_on_elec, t_off_elec]
        - Hydrogen flow: [P_elec, h2flow]
    - Hydrogen storage:
        - Buffer pressure: [pres_buf, h2_flow, t_on_elec, t_on_comp, t_off_comp, temperature, s_elec, s_comp]
     
        - Compressor consumed power: [s_comp, h2_flow,  t_on_comp, t_off_comp, P_comp]
        - Tank pressure: [Temperature, h2_flow, t_on_comp, t_off_comp, pres_comp, P_comp]
    - Fuel Cell:
        - Hydrogen consumed: [s_pila, P_pila, h2_flow_pila]
        - Power generated:[s_pila, P_pila, h2_flow_pila, t_on_pila]
* "depth": Depth of the neural network. In case of the DNN, this parameter must be 1.

## 3. Input and output files

The input file is a .csv file with the colums described in the following. Some of them are mandatory, like "datetime", "Breaks", "P_pan", "P_viv" and "Temperature". The rest of  colums are only required when executing the models with real inputs ("inputs":"real" in the configuration file), in other case ("inputs":"est" in the configuration file) these colums can be completed with zero values.

In any case, it is also recomended to include the state of charge of the battery (SOC) and hydrogen storage (pres_buf and pres_comp) when starting a measurements period (Breaks="OPEN").

* datetime (datetime): Timestamp of the measurements, in "yyyy-MM-dd hh:mm:ss" format.
* Breaks (string): Indicates the starting ("OPEN") and end ("CLOSE") of a period of measurements. Intermediate samples should contain empty values.
* P_pan (float): Power generated by the photovoltaic panels [Watts].
* P_viv (float): Power consumed in the dwelling[Watts].
* P_car (float): Changing battery power [Watts].
* P_des (float): Discharching battery power [Watts].
* P_exp (float): Power exported to the grid [Watts].
* P_imp (float): Power imported from the grid [Watts].
* P_elec (float): Power consumed by the electrolizer [Watts]
* P_comp (float): Power consumed by the compressor [Watts].
* P_pur (float): Power consumed by purifier [Watts].
* SOC (float): state of charge of the battery [%].
* pres_buf (float): Buffer pressure [Bar].
* pres_comp (float): Tank pressure [Bar].
* P_pila (float): Power provided by the fuel cell [Watt].
* pres_pila (float): Fuel Cell pressure [Bar].
* h2_flow_pila (float): Hydrogen flow consumed by the fuel cell [NL/h].
* h2_total (float): Total hydrogen generated by the electrolyzer [NL].
* h2_flow (float): Hydrogen flow generatedby the electrolyzer in the pariod between current sample and the one before [NL/h]
* Temperature (float): Environmental temperature [ºC].

When finalizing the execution, the digial twin generates a .csv file with the obtained estimations, with the following colums:
* datetime (datetime): Timestamp of the measurements, in "yyyy-MM-dd hh:mm:ss" format. 
* Temperature: Environmental temperature [ºC].
* Breaks (string): Indicates the starting ("OPEN") and end ("CLOSE") of a period of measurements. Intermediate samples should contain empty values.
* P_pan (float): Power generated by the photovoltaic panels [Watts].
* P_viv (float): Power consumed in the dwelling[Watts].
* P_car (float): Estimated Changing battery power [Watts].
* P_des (float): Estimated Discharching battery power [Watts].
* P_exp (float):Estimated Power exported to the grid [Watts].
* P_imp (float): Estimated Power imported from the grid [Watts].
* P_elec (float): Estimated Power consumed by the electrolizer [Watts]
* P_comp (float): Estimated Power consumed by the compressor [Watts].
* P_pur (float): Estimated Power consumed by purifier [Watts].
* P_pila (float): Estimated Power provided by the fuel cell [Watt].
* SOC (float): Estimated state of charge of the battery [%].
* pres_buf(float): Estimated buffer pressure [Bar].
* pres_comp (float): Estimated Tank pressure [Bar].
* pres_pila (float): Estimated Fuel Cell pressure [Bar].
* P_car_pila: Estimated charging battery power from the fuel cell [Watt].
* s_elec (int): Estimated signal from the PLC to the electrolyzer. 1: ON / 0: OFF.
* s_comp (int): Estimated signal from the PLC to the compressor. 1: ON / 0: OFF.
* s_pila (int): Estimated signal from the PLC to the fuel cell. 1: ON / 0: OFF.
* h2_total (float): Estimated Total hydrogen generated by the electrolyzer [NL].
* h2_flow (float): Estimated hydrogen flow generated by the electrolyzer in the period between current sample and the one before [NL/h].
* h2_elec (float): Estimated volume of hydrogen generated by the electrolyzer in the period between current sample and the one before [NL].
* h2b_nl (float): Estimated volume of hydrogen storaged at the buffer [NL].
* h2t_nl: Estimated volume of hydrogen storaged at the tank [NL].
* h2_flow_pila (float): Estimated Hydrogen flow consumed by the fuel cell [NL/h].



## 5. Acknolegments

This work has been funded by the Spanish Government (Ministry of Science and Innovation) and the European Union (Next GenerationEU/RTRP) through the projects “Digital twin of a hybrid solar photovoltaic-hydro hybrid system for residential supply” (TED2021-129951B-C22) and ”Demonstration pilot of a solar-photovoltaic-hydrogen hybrid system for residential energy supply” (TED2021-129951B-C21), as well as by theGovernment of Cantabria through the project “Enabling Technologies for Digital Twins and their application in the chemical and communications sectors” (GDQuiC) of the TCNIC program (2023/TCN/002).
