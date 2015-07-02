import numpy as np
import os, sys, subprocess, ConfigParser,time, string

class kampagne_einstellung(object):
	class_typ="Kampagneneinstellung"
	def __init__(self,config):
		self.name = config[0]
		self.flugzeiten = config[1].split("\t")[-1]
		self.icartt_sp2 = config[2].split("\t")[-1]
		self.icartt_sp1a = config[3].split("\t")[-1]

def kampagne_lesen(filename):
	config_dat=open(filename,"r").read().split("\n")
	kampagne=kampagne_einstellung(config_dat)
	return kampagne



class plot(object):
	class_typ="Plot Einstellungen"
	def __init__(self,pfad,x,subis):
		self.path = pfad
		self.mittelung = int(float(x[0]))
		self.zeit_start = int(float(x[1]))
		self.zeit_stop =	int(float(x[2]))
		self.grid = [int(float(x[3].split(',')[0])),int(float(x[3].split(',')[1]))]
		self.gemeinsame_achse = x[4]
		self.name = x[5]
		self.sub = subis
		
class subplot(object):
	class_typ="Subplot Einstellung"
	def __init__(self,i):
		self.position = [int(ee.split('\n')[i].split(';')[0].split(',')[0]),int(ee.split('\n')[i].split(';')[0].split(',')[1])]
		self.traces =[]

		for j in range(len(ee.split('\n')[i].split(';')[2].split(','))):
			self.traces.append(int(ee.split('\n')[i].split(';')[2].split(',')[j]))
		self.plottyp=ee.split('\n')[i].split(';')[3]
		self.gegen=int(float(ee.split('\n')[i].split(';')[4]))
		
		self.xlabel = ee.split('\n')[i].split(';')[5].lower()
		self.xlabel_pos = ee.split('\n')[i].split(';')[6].lower()
		self.xoption = ee.split('\n')[i].split(';')[7]
		self.xlow = int(float(ee.split('\n')[i].split(';')[8]))
		self.xhigh = int(float(ee.split('\n')[i].split(';')[9]))
		self.ylabel = ee.split('\n')[i].split(';')[10].lower()
		self.ylabel_pos = ee.split('\n')[i].split(';')[11].lower()
		self.yoption = ee.split('\n')[i].split(';')[12]
		self.ylow = int(float(ee.split('\n')[i].split(';')[13]))
		self.yhigh = int(float(ee.split('\n')[i].split(';')[14]))
		self.legcol = int(float(ee.split('\n')[i].split(';')[15]))

#fuer jede Plot-Vorlage gibt es eine Datei im Speicher
#Informationen werden aus Plot_vorlage gelesen und in ein "Plot-Objekt" geschrieben
#Die "Plot-Objekte" werden in einer Liste gesammelt
# Die Attribute eines "Plot-Objekts" beinhalten die Informationen zum plotten der Vorlage
		
def plots_lesen():
	global ee
	plots=[]
	path=os.path.expanduser('./speicher/')
	for h in range(len(os.listdir(path))-1):
		if os.listdir(path)[h].split('_')[0]=='plot' and os.listdir(path)[h].split('.')[1]!='txt~': 
			ee=open(string.join(['./speicher/',os.listdir(path)[h]],''),"r").read()
			ppll=[]
			for i in range(1,len(ee.split('\n'))-1,1):
				ppll.append(subplot(i))
			plots.append(plot('./speicher/',ee.split('\n')[0].split(';'),ppll))
	return plots
	
def plots_schreiben(plots):
	for h in range(len(plots)):
		ww=open(string.join([plots[h].path,'plot_',plots[h].name,'.txt'],''),"w")
		ww.write(str(plots[h].mittelung))	;ww.write(';')
		ww.write(str(plots[h].zeit_start))	;ww.write(';')
		ww.write(str(plots[h].zeit_stop))	;ww.write(';')
		ww.write(str(plots[h].grid[0]))	;ww.write(',')
		ww.write(str(plots[h].grid[1]))	;ww.write(';')
		ww.write(plots[h].gemeinsame_achse)	;ww.write(';')
		ww.write(plots[h].name)	;ww.write(';')
		ww.write('\n')
		for j in range(len(plots[h].sub)):
			ww.write(str(plots[h].sub[j].position[0]))	;ww.write(',')
			ww.write(str(plots[h].sub[j].position[1]))	;ww.write(';')
			ww.write('traces')	;ww.write(';')
			for i in range(len(plots[h].sub[j].traces)):
				ww.write(str(plots[h].sub[j].traces[i]))	
				if i == len(plots[h].sub[j].traces)-1:ww.write(';')
				else:ww.write(',')
			ww.write(plots[h].sub[j].plottyp)	;ww.write(';')
			ww.write(str(plots[h].sub[j].gegen))	;ww.write(';')
			ww.write(plots[h].sub[j].xlabel)	;ww.write(';')
			ww.write(plots[h].sub[j].xlabel_pos)	;ww.write(';')
			ww.write(plots[h].sub[j].xoption)	;ww.write(';')
			ww.write(str(plots[h].sub[j].xlow))	;ww.write(';')
			ww.write(str(plots[h].sub[j].xhigh))	;ww.write(';')

			ww.write(plots[h].sub[j].ylabel)	;ww.write(';')
			ww.write(plots[h].sub[j].ylabel_pos)	;ww.write(';')			
			ww.write(plots[h].sub[j].yoption)	;ww.write(';')
			ww.write(str(plots[h].sub[j].ylow))	;ww.write(';')
			ww.write(str(plots[h].sub[j].yhigh))	;ww.write(';')

			ww.write(str(plots[h].sub[j].legcol))	;ww.write(';')
			ww.write('\n')
	ww.close()

#aehnlich wie die Plot-Objekte gibt es "Spuren-Objekte", die Informationen ueber die Messreiehen beinhalten
#wird in den Ploteinstellungen die Farbe einer Spur geaendert wird die Spur zukuenftig in allen Plots in der neuen Farbe dargestellt
class trace(object):
	class_typ="Messreihe"
	def __init__(self,i):
		self.index = int(float(oo.split('\n')[i].split(";")[0]))
		self.units = oo.split('\n')[i].split(";")[3]
		self.label_orig = oo.split('\n')[i].split(";")[1]
		self.label = oo.split('\n')[i].split(";")[2]
		self.farbe = oo.split('\n')[i].split(";")[5]
		self.marker = oo.split('\n')[i].split(";")[4]	
		self.typ = oo.split('\n')[i].split(";")[6]

def spuren_lesen(pfad):
	global oo
	spuren=[]
	oo=open(pfad,'r').read()
	for i in range(len(oo.split('\n'))-1):
		spuren.append(trace(i))
	return spuren

def spuren_schreiben(spuren):
	uu=open('speicher/spuren_info.txt','w')
	for i in range(len(spuren)):
		uu.write(string.join([str(i),';'],''))
		uu.write(string.join([str(spuren[i].label_orig),';'],''))
		uu.write(string.join([str(spuren[i].label_orig),';'],''))
		uu.write(string.join([str(spuren[i].units),';'],''))
		uu.write(string.join([str(spuren[i].marker),';'],''))
		uu.write(string.join([str(spuren[i].farbe),';'],''))
		uu.write(string.join([str(spuren[i].typ),';'],''))
		uu.write('\n')
	uu.close()

def timeshifts_lesen(pfad):
	tim=open(pfad,'r').read()
	return int(tim.split('\n')[0].split('\t')[0]),int(tim.split('\n')[1].split('\t')[0])

def nans(i,j):
	a = np.empty((i,j))
	a[:] = np.NaN
	return a

def mittelung(data,gemittelt):
	reihe = nans(int(len(data)/gemittelt),1)
	for j in range(len(reihe)):
		if (j+1)*gemittelt < data.shape[0]: 
			a=data[j*gemittelt:(j+1)*gemittelt]
			if np.isnan(a[a.argsort()][0])==True:    #wenn nur nans vorhanden
				reihe[j]=np.nan
			else:
				anzahl_non_nans= np.argmin(abs(np.nanargmax(a)-a.argsort()[:]))+1
				non_nans=a[a.argsort()[0:anzahl_non_nans]]
				reihe[j]=np.average(non_nans)
	reihe=np.delete(reihe,-1,0)
	return reihe


