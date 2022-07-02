# TFG
# Salvador Guerrero García
# salvadorgg@alu.comillas.edu
# Anual Vaccine routing 
# 01.26.2022

#Nodes:
set Man;
set Co;
set No = Co union Man;
set T ;

#Vaccines types
set Tv;


#Other:
param M_AMD;
param M_AMS;


param dc{i in No, j in No}, >= 0;                        #Distribution cost
#param fv{i in No, t1 in T, v in Tv};                    #Fullfiling value                  
param ac{i in No, j in No, t1 in T}, default 0;          #Available shipping capacity  
param nd{i in No, t1 in T, v in Tv};                     #Net demand    





var X{i in No, j in No, t1 in T,v in Tv} >= 0;          #Vaccines send form node i to j at time t1
var AMD{i in No, t2 in T, v in Tv} >= 0;                #Acumulated missing demand
var AMS{i in No, t2 in T, v in Tv} >= 0;                #Acumulated stock           
var F{i in Co, t2 in T, v in Tv} >= 0;                  #Fullfil demand               
var D{i in No, t2 in T, v in Tv};                       #Aux var: new planed demand
                         
var dist_cost;     


minimize cost:
    sum{ i in No, j in No, t1 in T, v in Tv }X[i,j,t1,v]*dc[i,j]   + sum{ i in No, t1 in T, v in Tv }(M_AMS*AMS[i,t1,v] + M_AMD*AMD[i,t1,v]); # -  alpha*sum{ i in Co, t2 in T, v in Tv }F[i,t2,v]*fv[i,t2,v] + sum{ i in No, t1 in T, v in Tv }M2*LV[i,t1,v];

s.t.    capc{ i in No, j in No, t1 in T}: sum{v in Tv} X[i,j,t1,v] <= ac[i,j,t1] ;
        
        net{ j in No, t1 in T, v in Tv }: sum{ i in No} X[i,j,t1,v] - sum{ i in No} X[j,i,t1,v] =  D[j,t1,v] - AMD[j,t1,v] + AMS[j,t1,v];

        consumed{ i in Co, t2 in T, v in Tv}: F[i,t2,v] =  D[i,t2,v] - AMD[i,t2,v] ;

        demand{ i in No, t2 in T diff {0}, v in Tv}: D[i,t2,v] = AMD[i,t2-1,v] + nd[i,t2,v] - AMS[i,t2-1,v] ;

        const7{  i in No, v in Tv }: D[i,0,v] = nd[i,0,v];

        const_cost: dist_cost = sum{ i in No, j in No, t1 in T, v in Tv }X[i,j,t1,v]*dc[i,j];

        