# TFG
# Salvador Guerrero García
# salvadorgg@alu.comillas.edu
# Montecarlo Simulation: Anual Vaccine routing 
# 01.26.2022


from __future__ import absolute_import, division, print_function
import os
import random
import sys
from builtins import map, object, range, sorted, zip
from turtle import shape
import openpyxl 

import numpy as np
import pandas as pd
from amplpy import AMPL, DataFrame

import matplotlib.pyplot as plt

from tqdm import tqdm
 
from ahp4 import ahp
from ahp4_temp import ahp_comp
from routing_lib import routing

# Disable printing
def blockprint():
    sys.stdout = open(os.devnull, 'w')

# Restore printing
def enableprint():
    sys.stdout = sys.__stdout__


def round_int(x):
    if x in [float("-inf"),float("inf")]: return (99999999)
    return int(np.round(x))



os.chdir(os.path.dirname(__file__) or os.curdir)
ampl = AMPL()
ampl.reset()
ampl.set_option('solver', 'cplex')
# Read the model file
ampl.read('routing_reduced.mod')

#Data:
tmax = 12
M_AMD = 1000000
M_AMS = 25

Man = ['JL','BB', 'SII', 'AJ', 'BF', 'BE']  																  #Manufactures
Co = ['SOM', 'PNG', 'SSD', 'TCD', 'CRI', 'NGA', 'ETH', 'YEM', 'COG', 'SLE', 'COD', 'GIN', 'HTI', 'MDG', 'SYR']#Countries
Tv = ['BCG', 'DTwP', 'Measles']
No = Co + Man

man_num = range(len(Man))
co_num = range(len(Co))
tv_num = range(len(Tv))
no_num = range(len(No))
T = list(range(tmax)) 

nd = {}
fv = {}
ac = {}
dc = {}
for i,ii in enumerate(No):
	for j,jj in enumerate(No):
		for k,kk in enumerate(T):
			for v,vv in enumerate(Tv):
				nd[i,k,v] = 0
				fv[i,v,k] = 0
				ac[i,j,k] = 0
				dc[i,j] = 0

ampl.get_parameter('M_AMS').set(M_AMS)
ampl.get_parameter('M_AMD').set(M_AMD)
ampl.get_set('Man').set_values(Man)
ampl.get_set('Co').set_values(Co)
ampl.get_set('Tv').set_values(Tv)


#Dstribution cost:
D_df = pd.read_csv(r'C:\Users\Usuario\OneDrive - Universidad Pontificia Comillas\RIT2021_2022\TFG\model\AMPL\ampl\ampl_ready_data/dc.csv',sep=',') 

max = D_df['dc'].max()
min = D_df['dc'].min()
for i,row in D_df.iterrows():
	dc[ No.index(row['Co']), No.index(row['Man']) ] = abs( (row['dc'] - min)*(10000 - 1)/(max - min) + 1 )
	dc[ No.index(row['Man']), No.index(row['Co']) ] = abs( (row['dc'] - min)*(10000 - 1)/(max - min) + 1 )
dc_df = DataFrame(('No','No1'), 'dc')
dc_df.setValues({
	(node, node1): int( dc[i,j] )
	for i,node in enumerate(No)
	for j,node1 in enumerate(No)
})
ampl.set_data(dc_df)

deley = {} 
for c in Co:
	for v in Tv:
		deley[c,v] = 0

wb = openpyxl.load_workbook("results.xlsx") 
sheets = ['min','max','minmax','base']
alpha = [0,1,1,0]   #value
beta = [1,0,1,1]	#cost
for id in tqdm (range (200), 
               desc="Running…", 
               ascii=False, ncols=75):

	#Setting to 0 variables:
	t_prog = {}
	for i,ii in enumerate(No):
		for j,jj in enumerate(No): 
			for k,kk in enumerate(T):
				for v,vv in enumerate(Tv):
					nd[i,k,v] = 0
					ac[i,j,k] = 0

	#Random country allocation:
	co_aux = Co
	rnd_co = {}
	for i in range(tmax):
		rnd_co[i] = []

	for i in range(tmax):
		jj = random.randint(0, 3)

		if len(co_aux) < jj:
			rnd_co[i] = random.sample(co_aux,len(co_aux))	
		else:
			rnd_co[i] = random.sample(co_aux,jj)

		co_aux = list( set(co_aux) ^ set(rnd_co[i]) )

		for c in rnd_co[i]:
			for v in Tv:
				t_prog[c,v] = i

		if i == (tmax-1):
			rnd_co[i] = random.sample(co_aux,len(co_aux))
	
		for c in rnd_co[i]:
			for v in Tv:
				t_prog[c,v] = i

		if len(co_aux) == 0:
			break
	# rnd_co[0] = []
	# rnd_co[1] = ['GIN']
	# rnd_co[2] = ['SYR']
	# rnd_co[3] = []
	# rnd_co[4] = ['SSD']
	# rnd_co[5] =[]
	# rnd_co[6] =['ETH']
	# rnd_co[7] = ['SOM', 'MDG']
	# rnd_co[8] = ['PNG']
	# rnd_co[9] =['COD']
	# rnd_co[10] =['TCD', 'HTI', 'NGA']
	# rnd_co[11] = ['SLE']

	#Demand
	D_df = pd.read_csv(r'C:\Users\Usuario\OneDrive - Universidad Pontificia Comillas\RIT2021_2022\TFG\model\AMPL\ampl\ampl_ready_data\demand.csv',sep=',') 
	for t in T:
		for c in rnd_co[t]:
			for v in Tv:
				nd[ No.index(c), t, Tv.index(v) ] = (D_df[ ( D_df['Co'] == c) & (D_df['Vac'] == v) ]['d'].to_numpy())

	#offer:
	D_df = pd.read_csv(r'C:\Users\Usuario\OneDrive - Universidad Pontificia Comillas\RIT2021_2022\TFG\model\AMPL\ampl\ampl_ready_data\flights.csv',sep=',') 
	for t in T:
		for m in Man:
			for v in Tv: 
				nd[ No.index(m), t, Tv.index(v) ] = (-D_df[ ( D_df['Man'] == m) & ( D_df['Co'].isin(rnd_co[t]) ) & (D_df['Vac'] == v) ]['X'].sum())

	#Flights reduction:
	red = [  0.982275938,  0.891000132,  0.195215369,  0.111143636,  0.158681703,  0.148489803,  0.24291322, 0.294282636,  0.277955223,  0.265607102,  0.236428909,  0.236808659]
	#red = [1,1,1,1,1,1,1,1,1,1,1,1]
	for t in T:
		for m in Man:
			for c in Co:
				for v in Tv:
					ac[ No.index(m), No.index(c) , t] = (red[t]*D_df[ ( D_df['Man'] == m) & (D_df['Co'] == c) ]['X'].sum())

	
	for ii in [3]:#range(4):
		
			
		if ii == 3:

			ampl.reset()
			result = routing(rnd_co,t_prog)
			result = [id] + result
			sheet=wb[sheets[ii]]
			sheet.append(result)	
			print("Results:", result)
			ampl.reset()
			ampl.set_option('solver', 'cplex')
			# Read the model file
			ampl.read('routing_reduced.mod')
			ampl.get_parameter('M_AMS').set(M_AMS)
			ampl.get_parameter('M_AMD').set(M_AMD)
			ampl.get_set('Man').set_values(Man)
			ampl.get_set('Co').set_values(Co)
			ampl.get_set('Tv').set_values(Tv)
			ampl.set_data(dc_df)


		else:	
			ampl.get_parameter('alpha').set(alpha[ii])
			ampl.get_parameter('beta').set(beta[ii])

			value = 0
			cost = 0
			for t in tqdm (T, desc="Simulation:" + str(id), leave=False):


				if t == 0:										#Initial conditions

					#Net Demand
					df = DataFrame(('No','Tv'), 'nd')
					df.setValues({
						(node, vac): int(nd[n,t,v])
						for n,node in enumerate(No)
						for v,vac in enumerate(Tv)
					})
					ampl.set_data(df)

					#Initial value
					deley = {} 
					for c in Co:
						for v in Tv:
							deley[c,v] = 0
					amd_am = {}		
					for c in Co:
						for v in Tv:
							amd_am[c,v] = 0
					fv_df = ahp(deley,amd_am)
					df = DataFrame(("No", "Tv"), 'fv')
					a =  {
						(c, vac): round_int(fv_df[c,vac])
						for cc,c in enumerate(Co)
						for v,vac in enumerate(Tv)
					}
					df.setValues( a )
					ampl.set_data(df)

				else:
					#Value:		
					fv_df = ahp(deley,amd)
					df = DataFrame(("No", "Tv"), 'fv')
					a =  {
						(c, vac): round_int(fv_df[c,vac])
						for cc,c in enumerate(Co)
						for v,vac in enumerate(Tv)
					}
					df.setValues( a )
					ampl.set_data(df)

					df = DataFrame(('No','Tv'), 'nd')
					df.setValues({
						(node, vac): int(nd[n,t,v] + amd[node, vac] - ams[node, vac])       
						for n,node in enumerate(No)
						for v,vac in enumerate(Tv)
					})
					ampl.set_data(df)
					
				#Available distribution capacity:
				df = DataFrame(('No','No1'), 'ac')
				df.setValues({
					(node, node1): int(ac[i,j,t])
					for i,node in enumerate(No)
					for j,node1 in enumerate(No)
				})
				ampl.set_data(df)


				ampl.solve()

				x = ampl.get_variable('AMD')
				x = x.get_values()
				amd = x.to_dict()
				x = ampl.get_variable('AMS')
				x = x.get_values()
				ams = x.to_dict()

				At_AMD = 0
				At_AMS = 0
				tdt = 0
				tot = 0

				for cc,c in enumerate(Co):
					for vv,v in enumerate(Tv):
						At_AMD = At_AMD + int(amd[c, v])
						for tt in T:
							tdt = tdt + nd[cc,tt,vv]
						if amd[c, v] > 0:
							deley[c, v] = t - t_prog[c, v]
						else:
							deley[c, v] = 0

				for m in Man:
					for v in Tv:
						At_AMS = At_AMS + int(ams[m, v])		#ojojojojojojojojo ensure this is ams
						for tt in T:
							tot = tot + nd[No.index(m), tt, Tv.index(v)]


				x = ampl.get_variable('Value')
				x = x.get_values()
				x = x.to_list()
				value = value + x[0]

				#print('Iteration value',x[0])
				x = ampl.get_variable('dist_cost')
				x = x.get_values()
				x = x.to_list()
				cost = cost + x[0]

				X = ampl.get_variable('X')
				X = X.get_values()
				X = X.to_list()
				for i in No:
					for j in No:
						for v in Tv:
							if j in Co:
								shipping_file = [ id, t, i, j, int(X[i,j,v]), v, dc[i,j], fv_df[j,v]]
							else:
								shipping_file = [ id, t, i, j, int(X[i,j,v]), v, dc[i,j], 0	        ]

				for i in Co:
					amd_file = 	[id, t, i, nd[i], amd[i]]

				for i in No:
					ams_file = 	[id, t, i, nd[i], ams[i]]

				result_file = [id ,value, cost, float(At_AMD/tdt), float(At_AMS/tot)]
				##print(x[0])
				#print(At_AMD,At_AMS,tdt,tot)
				#print('AMD:',At_AMD/tdt)
				#print('AMS:',At_AMS/tot)
			#print('Final cost ', cost)
			#print('Final value:',value)
			sheet=wb[sheets[ii]]
			sheet.append([id ,value, cost, float(At_AMD/tdt), float(At_AMS/tot)])
			print("Results:", [id ,value, cost, float(At_AMD/tdt), float(At_AMS/tot)])

	wb.save("results.xlsx")
 