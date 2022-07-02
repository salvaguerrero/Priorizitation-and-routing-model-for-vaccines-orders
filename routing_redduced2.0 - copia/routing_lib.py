# TFG
# Salvador Guerrero García
# salvadorgg@alu.comillas.edu
# Montecarlo Simulation: BaseLine
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
from ahp4_temp import ahp_comp

from tqdm import tqdm


# Disable print()
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore print()
def enablePrint():
    sys.stdout = sys.__stdout__

def routing(rnd_co,t_prog):
	
	os.chdir(os.path.dirname(__file__) or os.curdir)
	ampl = AMPL()

	ampl.reset()
	ampl.set_option('solver', 'gurobi')
	ampl.read('routing_reduced_complete.mod')

	#Data:
	tmax = 12
	M1 = 25
	alpha = 0

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

	M_AMD = 1000000
	M_AMS = 25
	ampl.get_parameter('M_AMD').set(M_AMD)
	ampl.get_parameter('M_AMS').set(M_AMS)


	ampl.get_set('Man').set_values(Man)
	ampl.get_set('Co').set_values(Co)
	ampl.get_set('Tv').set_values(Tv)
	ampl.get_set('T').set_values(T)



	# #income:		
	# D_df = pd.read_csv(r'C:\Users\Usuario\OneDrive - Universidad Pontificia Comillas\RIT2021_2022\TFG\model\AMPL\ampl\ampl_ready_data/income/income-equal.csv',sep=',') 
	# max = D_df['fv'].max()
	# min = D_df['fv'].min()

	# for c in Co:
	# 	for t in T:
	# 		for v in Tv:
	# 			fv[ No.index(c), Tv.index(v), t] = (D_df[ (D_df['Co'] == c) & (D_df['Vac'] == v) & (D_df['t'] == t)  ]['fv'].values  - min)*(10000 - 1)/(max - min) + 1

	# df = DataFrame(("No", "T", "Tv"), 'fv')
	# a =  {
	# 	(node, time, vac): int(fv[n,v,t])
	# 	for n,node in enumerate(No)
	# 	for t,time in enumerate(T)
	# 	for v,vac in enumerate(Tv)
	# }
	# df.setValues( a )
	# ampl.set_data(df)


	#Dstribution cost:
	D_df = pd.read_csv(r'C:\Users\Usuario\OneDrive - Universidad Pontificia Comillas\RIT2021_2022\TFG\model\AMPL\ampl\ampl_ready_data/dc.csv',sep=',') 

	max = D_df['dc'].max()
	min = D_df['dc'].min()
	for i,row in D_df.iterrows():
		dc[ No.index(row['Co']), No.index(row['Man']) ] = abs( (row['dc'] - min)*(10000 - 1)/(max - min) + 1 )
		dc[ No.index(row['Man']), No.index(row['Co']) ] = abs( (row['dc'] - min)*(10000 - 1)/(max - min) + 1 )

	df = DataFrame(('No','No1'), 'dc')
	df.setValues({
		(node, node1): int( dc[i,j] )

		for i,node in enumerate(No)
		for j,node1 in enumerate(No)
	})
	ampl.set_data(df)



	#setting to 0 variables:
	for i,ii in enumerate(No):
		for j,jj in enumerate(No):
			for k,kk in enumerate(T):
				for v,vv in enumerate(Tv):
					nd[i,k,v] = 0
					ac[i,j,k] = 0


	#Demand
	D_df = pd.read_csv(r'C:\Users\Usuario\OneDrive - Universidad Pontificia Comillas\RIT2021_2022\TFG\model\AMPL\ampl\ampl_ready_data\demand.csv',sep=',') 
	for t in T:
		for c in rnd_co[t]:
			for v in Tv:
				nd[ No.index(c), t, Tv.index(v) ] = int(D_df[ ( D_df['Co'] == c) & (D_df['Vac'] == v) ]['d'].to_numpy())

	#Offer:
	D_df = pd.read_csv(r'C:\Users\Usuario\OneDrive - Universidad Pontificia Comillas\RIT2021_2022\TFG\model\AMPL\ampl\ampl_ready_data\flights.csv',sep=',') 
	for t in T:
		for m in Man:
			for v in Tv:
				nd[ No.index(m), t, Tv.index(v) ] = int(-D_df[ ( D_df['Man'] == m) & ( D_df['Co'].isin(rnd_co[t]) ) & (D_df['Vac'] == v) ]['X'].sum())
	
	df = DataFrame(('No', 'T','Tv'), 'nd')
	df.setValues({
		(node, time, vac): int(nd[n,t,v])
		for n,node in enumerate(No)
		for t,time in enumerate(T)
		for v,vac in enumerate(Tv)
	})
	ampl.set_data(df)


	#Flights reduction:
	red = [  0.982275938,  0.891000132,  0.195215369,  0.111143636,  0.158681703,  0.148489803,  0.24291322, 0.294282636,  0.277955223,  0.265607102,  0.236428909,  0.236808659]
	#red = [1,1,1,1,1,1,1,1,1,1,1,1]
	for t in T:
		for m in Man:
			for c in rnd_co[t]:
				for v in Tv:
					ac[ No.index(m), No.index(c) , t] = int(red[t]*D_df[ ( D_df['Man'] == m) & (D_df['Co'] == c) ]['X'].sum())
	
	#Available capacity:
	df = DataFrame(('No','No1','T'), 'ac')
	df.setValues({
		(node, node1, time): int(ac[i,j,k])
		for i,node in enumerate(No)
		for j,node1 in enumerate(No)
		for k,time in enumerate(T)
	})
	ampl.set_data(df)

	sheets = ['base','model']



	tot = 0

	ampl.solve()

	totalcost = ampl.get_objective('cost')
	tot = totalcost.value()
		

	x = ampl.get_variable('AMD')
	x = x.get_values()
	x = x.to_dict()

	y = ampl.get_variable('AMS')
	y = y.get_values()
	y = y.to_dict()	

	At_AMD = 0
	At_AMS = 0
	tdt = 0
	tot = 0

	for cc,c in enumerate(Co):
		for vv,v in enumerate(Tv):
			At_AMD = At_AMD + x[c, tmax-1, v]
			for t in T:
				tdt = tdt + nd[cc,t,vv]

	for m in Man:
		for v in Tv:
			At_AMS = At_AMS + y[m, tmax-1, v]
			for t in T:
				tot = tot + nd[No.index(m), t, Tv.index(v)]

	a = ampl.get_variable('dist_cost')
	a = a.get_values()
	Dc = a.to_list()

	if Dc[0] != 0:
		#Calculating value:
		deley = {} 
		for c in Co:
			for v in Tv:
				deley[c,v] = 0

		fv_df = {}
		for cc,c in enumerate(Co):
			for vv,v in enumerate(Tv):
				for t in T:
					if x[c, t, v] > 0:
						deley[c, v] = t - t_prog[c, v]
					else:
						deley[c, v] = 0
		print("executing ahp")		
		for t in T:
			fv_df[t] = ahp_comp(deley,x,t)
		print("finished executing ahp")		
		
		x = ampl.get_variable('F')
		x = x.get_values()
		F = x.to_dict()
		value = 0
		for cc,c in enumerate(Co):
			for vv,v in enumerate(Tv):
				for t in T:
					value = value + fv_df[t][c,v][0]*F[c, t, v]

		#print(x[0])
		# print(At_AMD,At_AMS,tdt,tot)
		# print(rnd_co)
		# print('AMD:',At_AMD/tdt)
		#print('AMS:',At_AMS/tot)
		# print('Final value:',value)
		# print('Distribution cost',Dc[0])

		res = [value, Dc[0], At_AMD/tdt, At_AMS/tot]
		# print([ value, Dc[0], At_AMD/tdt, At_AMS/tot])
		
		
	return res

