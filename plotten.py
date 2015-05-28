################################# import packages/libraries

import time, string
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.ticker import MaxNLocator
from matplotlib.figure import Figure 
import matplotlib.figure as mplfig
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

import datetime 
import warnings
warnings.simplefilter("error")

from funktionen import * 

def time_ticks(plo,sub,data):
	if sub.plottyp=='x': 
		ax.set_xticks(ticks)	
		ax.set_xticklabels(ticks_uhr)
		ax.set_xlim(data[zeit_start,1],data[zeit_stop,1])
	if sub.plottyp=='y': 
		ax.set_yticks(ticks)	
		ax.set_yticklabels(ticks_uhr)
		ax.set_ylim(data[zeit_start,1],data[zeit_stop,1])

def new_subplot(nummer,sub,data,spuren,plo,zeit_start,zeit_stop): 
	# nummer = wieveilter subplot
	# sub = Inos ueber sub-plot (ist ein teil von plo -> siehe funktionen.py)
	# data = messwerte in matrix form
	# spuren = Info ueber Messreihen (auch farbe und marker)
	# plo = Infos ueber den gesamt-plot (-> siehe funktionen.py)
	# zeit_start,zeit_stop = von zeit_start bis zeit_stop wird geplottet (integer index von start_zeit und stop_zeit)
	global ax,fig
	markersize=6
	pos=plo.grid[0]*100+plo.grid[1]*10+sub.position[0]+plo.grid[0]*sub.position[1]+1
	ax = fig.add_subplot(pos)
	for i in range(len(sub.traces)):
	# Daten werden gemittelt und in scatter-plot dargestellt
		#if spuren[sub.traces[i]].typ != "SP1A": dat,x=mittelung(data[zeit_start:zeit_stop,sub.traces[i]],plo.mittelung),mittelung(data[zeit_start:zeit_stop,sub.gegen],plo.mittelung)
		dat,x=data[zeit_start:zeit_stop,sub.traces[i]],data[zeit_start:zeit_stop,sub.gegen]
		try:
			if sub.plottyp=='x':ax.scatter(x,dat,color=spuren[sub.traces[i]].farbe,marker=spuren[sub.traces[i]].marker,s=markersize,label=spuren[sub.traces[i]].label)
			if sub.plottyp=='y':ax.scatter(dat,x,color=spuren[sub.traces[i]].farbe,marker=spuren[sub.traces[i]].marker,s=markersize,label=spuren[sub.traces[i]].label)
		except ValueError:		
			ax.plot([0],[0],label='problem with data')
		
# legends, labels, grid....
	ax.legend(loc=3,ncol=sub.legcol, bbox_to_anchor=(0.0, .95, 1., .95), borderaxespad=0.0,frameon=False,scatterpoints=3)
	if sub.ylabel_pos == "r":
		ax.yaxis.tick_right()
		ax.yaxis.set_label_position("right")
	if sub.ylabel!='\t':	ax.set_ylabel(sub.ylabel,size='large')
	if sub.ylow == -99: sub.ylow=ax.get_ylim()[0]
	if sub.yhigh == -99: sub.yhigh=ax.get_ylim()[1]
	ax.set_ylim(sub.ylow,sub.yhigh)
	if sub.yoption == 'invert': 
		ax.invert_yaxis()
	if sub.yoption == 'log': ax.set_yscale('log')

	if sub.xlabel!='\t': ax.set_xlabel(sub.xlabel,size='large')
	if sub.xlow == -99: sub.xlow=ax.get_xlim()[0]
	if sub.xhigh == -99: sub.xhigh=ax.get_xlim()[1]
	ax.set_xlim(sub.xlow,sub.xhigh)
	if sub.xoption == 'invert': 
		ax.invert_xaxis()
	if sub.xoption == 'log': ax.set_xscale('log')
	if len(ticks)>1:
		if sub.gegen==1:time_ticks(plo,sub,data)
		if plo.gemeinsame_achse=="x":
			if plo.grid[0]-sub.position[0]!=1:ax.set_xticklabels(' ')		
			ax.yaxis.set_major_locator(MaxNLocator(5))	
		if plo.gemeinsame_achse=="y":
			if sub.position[0]+sub.position[1]!=0:ax.set_yticklabels(' ')	
			ax.xaxis.set_major_locator(MaxNLocator(5))
		ax.minorticks_on()
	ax.grid(True)	
	
	return ax


def plotten(datum_list,plo,spuren):
	#datum_list = Liste an Daten in string Format der Form '20140708'
	#plo = Plot-Einstellung nach der geplottet wird (ein Plot-Objekt -> siehe funktionen.py)
	#spuren = Informationen ueber Messreihen (-> siehe funktionen.py
	global fig,ticks,ticks_uhr,achsen_info,zeit_start,zeit_stop
	matplotlib.rcParams.update({'font.size': 15})
	for k in range(len(datum_list)):
		start = time.clock()
		achsen_info=[]
		datum=datum_list[k]
		data=np.loadtxt(string.join(['../txt/',datum,'_data.txt'],''),skiprows=1)	
	# Informationen ueber den zu plottenen Zeitraum
		zeit=data[:,1]
		if plo.zeit_start==0 and plo.zeit_stop==1:zeit_start,zeit_stop=data[0,1],data[-1,1]
		else: zeit_start,zeit_stop=plo.zeit_start,plo.zeit_stop
	# Zeit-Ticks erstellen
		ticks=[]
		if plo.sub[0].gegen==1:
			if (zeit_stop-zeit_start)/3600.>5:ticks = np.arange(zeit_start,zeit_stop,3600)
			if (zeit_stop-zeit_start)/3600.<5:ticks = np.arange(zeit_start,zeit_stop,1800)
			if (zeit_stop-zeit_start)/3600.<2:ticks = np.arange(zeit_start,zeit_stop,600)
			if (zeit_stop-zeit_start)/3600.<0.5:ticks = np.arange(zeit_start,zeit_stop,60)
			if plo.sub[0].gegen==1:
				ticks_uhr = []
				for index, item in enumerate(ticks):
					ticks_uhr.append(time.strftime('%H:%M',time.gmtime(item)))
	# Index der Start-Zeit und Ende-Zeit
		zeit_start,zeit_stop=np.argmax(zeit==zeit_start),np.argmax(zeit==zeit_stop)

		fig = matplotlib.figure.Figure(figsize=(18,10),dpi=50)
		canvas=FigureCanvas(fig)
	# die sub-plots werden einzeln eingefuegt
		axen=[]
		for i in range(len(plo.sub)):
			axen.append(new_subplot(i,plo.sub[i],data,spuren,plo,zeit_start,zeit_stop))

		fig.suptitle(datum)

		canvas.print_figure('../plots/'+datum+'_'+str(plo.mittelung)+'_'+plo.name+'.png')
		axi=open('../plots/.'+datum+'_'+str(plo.mittelung)+'_'+plo.name+'.txt','w')
		for sub in achsen_info:
			for element in sub:	axi.write(str(element)+"\t")
			axi.write("\n")
		axi.close()
		print datum,plo.name, 'geplottet in %d s'%(time.clock()-start)
		#print fig
	return fig,axen,canvas

def manuel_plot(datum_list):
	spuren=spuren_lesen('speicher/spuren_info.txt')
	plots=plots_lesen()	
	for ploteinstellung in plots:
		plotten(datum_list,ploteinstellung,spuren)

#manuel_plot(["20140708","20140710"])
		

