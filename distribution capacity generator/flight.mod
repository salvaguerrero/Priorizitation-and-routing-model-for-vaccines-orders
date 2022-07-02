# TFG
# Flights generator
# 05.04.2022

set Man;
set Co;
set Vac;

param dc{i in Co, j in Man};  			#Distribution cost per vaccine senf from man j to country i
param o{j in Man, v in Vac} default 0;	#Is the vaccine v offer from manufacture j: yes->1000000,No->0
param d{i in Co, v in Vac}; 			#Demand of vaccine v from country i
param vc{j in Man, v in Vac};			#Cost of vaccine v for manufacture j

var X{i in Co, j in Man, v in Vac} >= 0; #num of vaccines of type v send from an j to country i

minimize cost:
	sum{ i in Co, j in Man, v in Vac} X[i,j,v]*( dc[i,j] + vc[j,v] );

s.t.	offer{j in Man, v in Vac}: sum{ i in Co }X[i,j,v] <= o[j,v];

		demand{i in Co, v in Vac}: sum{ j in Man}X[i,j,v] = d[i,v];
