# HY2RES Digital Twin



## Input files

The input file is a .csv file with the format described in the following. Each row represents a sample from the real system, and the colums the measuments colleted. Some of them are mandatory, like "datetime", "Breaks", "P_pan", "P_viv" and "Temperature". The rest of colums are only required when executing the models with real inputs ("inputs":"real" in the configuration file), in other case ("inputs":"est" in the configuration file) these colums can be completed with zero values.

In any case, it is also recomended to include the state of charge of the battery (SOC) and hydrogen storage (pres_buf and pres_comp) when starting a measurements period (Breaks="OPEN").

An example of input file is located in data folder.

The fields of the input file are next described:

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
