# TFG
# Salvador Guerrero García
# salvadorgg@alu.comillas.edu
# Block Vaccine routing 
# 02.26.2022



#Nodes:
set Man;
set Co;
set No = Co union Man;

#Vaccines types
set Tv;


#Other:
param M_AMD;
param M_AMS;
param alpha;
param beta;


param dc{i in No, j in No};                     #Distribution cost
param fv{i in No, v in Tv};                     #Fullfiling value             
param del{i in Co, v in Tv};                    #Fullfiling value                  
param ac{i in No, j in No}, default 0;          #Available shipping capacity  
param nd{i in No, v in Tv};                     #Net demand    





var X{i in No, j in No,v in Tv} >= 0;               #Vaccines send form node i to j at time t1
var AMD{i in No, v in Tv} >= 0;                     #Acumulated missing demand
var AMS{i in No, v in Tv} >= 0;                     #Acumulated missing stock
var F{i in Co, v in Tv} >= 0;                       #Fullfil demand               
                         
var Value;                                          #Performance metric 1
var dist_cost;                                      #Performance metric 2


minimize cost:
    beta*sum{ i in No, j in No, v in Tv }X[i,j,v]*dc[i,j] + sum{ i in No, v in Tv }(M_AMD*AMD[i,v]+M_AMS*AMS[i,v])  - alpha*sum{ i in Co, v in Tv }F[i,v]*fv[i,v] ; # + sum{ i in No, t1 in T, v in Tv }M2*LV[i,t1,v];

s.t.    capc{ i in No, j in No}: sum{v in Tv} X[i,j,v] <= ac[i,j] ;
        
        net{ j in No, v in Tv }: sum{ i in No} X[i,j,v] - sum{ i in No} X[j,i,v] = nd[j,v] - AMD[j,v] + AMS[j,v];

        consumed{ i in Co, v in Tv}: F[i,v] =  nd[i,v] - AMD[i,v] + AMS[i,v];

        val: Value = sum{ i in Co, v in Tv }F[i,v]*fv[i,v];

        const_cost: dist_cost = sum{ i in No, j in No, v in Tv }X[i,j,v]*dc[i,j];


        