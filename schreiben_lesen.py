################################# import packages/libraries

import Tkinter as tk
import os, sys, subprocess, ConfigParser,time, string
import numpy as np
import scipy as scipy
import datetime 
import itertools
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.io import netcdf

from funktionen import * 

conv = lambda valstr: float(valstr.decode("utf-8").replace(',','.'))
c8 = {0:conv, 1:conv, 2:conv, 3:conv, 4:conv, 5:conv, 6:conv, 7:conv }
c2 = {0:conv, 1:conv }
	
def einlesen(datum_list,pfad,sp2_timeshift,sp1a_timeshift,optionen_var,kampagne):
	#datum_list = list of dates in string format as '20140708'
	#pfad = string of path where measurement data is located
	#sp2_timeshift = integer of seconds that sp2 measurements have to be shifted in order to synchronize
	#sp1a_timeshift = integer of seconds that sp1a measurements have to be shifted in order to synchronize
	#optionen_var = list of things to do for the date (coming from check boxes in menu) 1 = do it ; 0 = skip this

	for datum in datum_list:
		start=time.clock()
		if optionen_var[0]==1:
			hk_list,bc_list,sp1a_list,wetter_list,aimms_list = [],[],[],[],[]							# Listen fuer Dateinamen
			hkdata,bcdata,sp1adata,wetterdata, aimmsdata = [],[],[],[],[] 								# Listen fuer Messreihen
	# Informationen ueber die Dateistruktur der Rohdaten die zur Bearbeitigung benoetigt werden
			fill_types=[[None],[None],[None],[-99.0],[-99, -9999999, -999, -9999, -99999]]					# eintraege die durch nan ersetzt werden
			sample_flow=[1,1,None,1,1]																		# bei 1 gibt es jede Sekunde einen Messwert, bei None ist das unregelmaesig
			labels=["HK","BC","sp1a","Wetter","AIMMS"]										# fuer Ueberschriften in Logdatei
			name_list=[hk_list,bc_list,sp1a_list,wetter_list,aimms_list]  # Dateinamen fuer Logdatei
			datas=[hkdata,bcdata,sp1adata,wetterdata,aimmsdata]						# Messdaten, wobei bcdata die Liste der BC-Data Datein eines Datums ist
			time_trace=[]																									# Nummer der Zeitspalte in der Originaldatei							
			traces=[]																											# relevante Spaltennummern in Originaldatei
			position=[]																										# Spaltennummer, ab der in die erstellte Matrix geschrieben wird					
	# Spaltennummern in der End-Datei:	 0-time in seconds of day, 1-leer
	# ------------------------- HK-Data
	#	0-pressure
			traces.append([1,0])
			position.append(1)
	# ------------------------- BC-Data 
	# 0-TimeBdr	1-TotTrig_NumbConc	2-BBHG_NumbConc	3-BBHG_MassConc	4-BBLG_NumbConc	5-BBLG_MassConc	6-BHBL_NumbConc	7-BHBL_MassConc	8-NBHG_NumbConc	9-NBHG_MassConc	10,NBLG_NumbConc	11-NBLG_MassConc	12-BBHGorSCHG_NumbConc	13-SCHGnotBBHG_NumbConc
			traces.append([0,1,2,3,4,5,6,7,8,9,10,11,12,13])
			position.append(2)
	# ------------------------- SP1A-Data
	# 7-time,	11-altitude,	9-geo breite,	10-geo laenge,	27-alpha,	28-beta, 39-AOD367.0,	48-AOD391.9,	57-AOD413.7,	66-AOD499.5,	75-AOD610.5,	84-AOD675.0,	93-AOD779.3,	102-AOD861.3,	111-AOD946.4,	120-AOD1026.2	
			traces.append([7,11,9,10,27,28,39,48,57,66,75,84,93,102,111,120])
			position.append(15)
	# ------------------------- Wetter
	# /!\ 2->Time,	3-TempRiosemount, 41-TempHumicap, 18-GroundSpeed, 35-TrueAirSpeed, 7-Altitude, 45-GPSAltitude, 40-RelHumidity, -6-Geobreite, -5-GeoLaenge		
			traces.append([2,3,41,18,35,7,45,40,-6,-5])			#zeit ist eigentlich spalte 1 und wird umgerechnet eingefuegt (spalte 2 ist unwichtig)
			position.append(30)
	#-------------------------- AIMMS
	# 0-Time,	2-Temp, 3-RH, 4-BP, 5-WindFlowN, 6-WindFlowE, 7-Latitude, 8-Longitude, 9-Altitude
			traces.append([0,2,3,4,5,6,7,8,9])
			position.append(39)

	# --------------------------------------------- 		a)	--------------------------------------------	
			path=os.path.expanduser(pfad)
			# sucht in gewaehlten Ordner nach Dateien, die das gewuenschte Datum enthalten
			# falls das Datum passt wird anhand des Dateinamens das Messgeraet bestimmt
			for file in sorted(os.listdir(path)):
				if os.path.isfile(os.path.join(path,file)):
					if os.path.splitext(file)[-1].lower() == '.txt':
						if os.path.splitext(file)[0].split('-')[0].lower() == 'awi':
							if os.path.splitext(file)[0].split('-')[1].lower() == datum:
								# AWI-datum-01.txt
								wetter_list.append(os.path.join(path,file))
								data_zw=np.genfromtxt(os.path.join(path,file),dtype='float',skip_header=0,delimiter='\t',usecols=traces[3])
								wetterzeit=np.genfromtxt(os.path.join(path,file),dtype='str',skip_header=0,delimiter='\t')
								for j in range(wetterzeit.shape[0]):
									zeit_zw=wetterzeit[j,0].split(' ')[1].split(':')
									data_zw[j,0] =float(zeit_zw[0])*60*60 + float(zeit_zw[1])*60 + float(zeit_zw[2])  
								wetterdata.append(data_zw)

						if os.path.splitext(file)[0].split('-')[0].lower() == datum:
							if os.path.splitext(file)[0].split('-')[-1] == 'HKData':
								# datum-01-HKData.txt
								hk_list.append(os.path.join(path,file))
								data_zw=np.genfromtxt(os.path.join(path,file),dtype='float',skip_header=1,delimiter='	', converters = c2,usecols=traces[0])
								for j in range(data_zw.shape[0]):
									hktime = time.gmtime(data_zw[j,0]-sp2_timeshift)
									data_zw[j,0] = hktime[3]*3600+hktime[4]*60+hktime[5]
								hkdata.append(data_zw)

							if  os.path.splitext(file)[0].split('-')[-1] == 'BCData':
								# datum-01-BCData.txt

								try:
									data_zw=np.genfromtxt(os.path.join(path,file),dtype='float',skip_header=1,delimiter='	', converters = c8,usecols=traces[1])
									bc_list.append(os.path.join(path,file))
									for j in range(data_zw.shape[0]):
										bctime = time.gmtime(data_zw[j,0]-sp2_timeshift)
										data_zw[j,0] = bctime[3]*3600+bctime[4]*60+bctime[5]
									bcdata.append(data_zw)		
								except: print os.path.join(path,file)+" has wrong format"
							if  os.path.splitext(file)[0].split('-')[-1] != 'BCData' and os.path.splitext(file)[0].split('-')[-1] != 'HKData':
								# datum-01.txt
								sp1a_list.append(os.path.join(path,file))
								data_zw=np.genfromtxt(os.path.join(path,file),dtype='float',skip_header=0,delimiter=';',usecols=traces[2])
								data_zw[:,0]=	np.round(data_zw[:,0]*24*60*60)
								for j in range(data_zw.shape[0]):
									sp1atime = time.gmtime(data_zw[j,0] - sp1a_timeshift)
									data_zw[j,0] = sp1atime[3]*3600+sp1atime[4]*60+sp1atime[5]
								sp1adata.append(data_zw)

					if os.path.splitext(file)[-1].lower() == '.ict':
						if os.path.splitext(file)[0].split('_')[2].lower() == datum:
							# AIMMS_07231537Polar6_datum_R0_V2.ict
							aimms_list.append(os.path.join(path,file))
							skip=int(open(os.path.join(path,file),"r").read().split('\n')[0].split(',')[0])+1
							aimmsdata.append(np.genfromtxt(os.path.join(path,file),dtype='float',skip_header=skip,delimiter=',',usecols=traces[4]))
			#	im logfile werden ab hier Informationen ueber Messzeiten und eingelesene Dateien hinterlegt
			logfile = open(string.join(['../log/',datum,'_log.txt'],''),'w')
			logfile.write(string.join(['Data measured the',datum,'\n'],' '))

	# --------------------------------------------- 		b)	--------------------------------------------	
	# Neue Zeitachse
			minis,maxis=[],[]
			for i in range(len(labels)):
				if len(datas[i])>0:
					minis.append(datas[i][0][0,0])															# sammelt fruehste Zeiten
					maxis.append(datas[i][-1][-1,0])														# sammelt spaeteste Zeiten
				else: logfile.write(string.join(['/!\ no ',labels[i],' Data!\n\n'],''))		# schreibt in logdatei, falls keine Messwerte vorhanden
	# erstellt einheitliche Zeitachse
			time_array = np.arange(np.nanmin(minis),np.nanmax(maxis)+5,1)

		
	# --------------------------------------------- 		c)	--------------------------------------------	
	# erstellt leere Matrix in die Messwerte geschrieben werden
			data = nans(time_array.shape[0], position[-1]+len(traces[-1]))
	# fuegt Zeitspalten in die Matrix ein		 
			data[:,0] = time_array
			data[:,1] = time_array
			if time_array.shape[0] <100: 
				print '/!\ eine Messdatei ist entweder nicht vorhanden oder ist grob unlesbar!'
				return None			
			logfile.write( string.join(['%d seconds measuring time going from'%(time_array[-1]-time_array[0]),time.strftime('%H:%M:%S',time.gmtime(time_array[0] )),'to',time.strftime('%H:%M:%S',time.gmtime(time_array[-1] )),'\n'],' '))
	# fuegt Messwerte in die Matrix ein
			for k in range(len(labels)):
				logfile.write(string.join(["---------------",labels[k],"-----------------\n"],''))
				for j in range(len(datas[k])):																													# fuer alle Datein eines Messgeraets
					if fill_types[k][0]!=None:
						for no in range(len(fill_types[k])):																									# fill_typ durch nan ersetzen
							datas[k][j][datas[k][j]==fill_types[k][no]]=np.nan																
					match = np.nanargmin(np.abs(time_array[:] - datas[k][j][0,0]))							# sucht Anfangszeit in Zeitspalte
					counter = match+len(datas[k][j])
					try:																															
						for i in range(1,len(traces[k])):
							if np.isnan(match)!=True:				
								if sample_flow[k]==1:		data[match:counter,position[k]+i] = datas[k][j][:,i]	#falls sekuendlich wird ein Block eingefuegt
								if sample_flow[k]==None:								
									for u in range(datas[k][j].shape[0]):																							#falls nicht werden Messwerte einzeln eingefuegt
										match_zw = np.nanargmin(np.abs(time_array[:] - datas[k][j][u,0]))
										data[match_zw,position[k]+i] = datas[k][j][u,i]
						logfile.write(name_list[k][j].split('/')[-1]+ ' contributes information from '+time.strftime('%H:%M:%S',time.gmtime(time_array[match] ))+ ' to '+time.strftime('%H:%M:%S',time.gmtime(time_array[match+len(datas[k][j])-1] ))+'\n')
					except ValueError:logfile.write("/!\ "+name_list[k][j].split('/')[-1]+"is damaged \n")
					print name_list[k][j].split('/')[-1]

	# messpunkte vor abflug und nach Landung loeschen
			try:	
				abflug,landung=0,0
				#flug=open("../log/Netcare 2014_Polar 6_start and stop times.csv","r").readlines()
				flug=open(kampagne.flugzeiten,"r").readlines()
				for i in range(11,len(flug),1):
					if datum=="%04d%02d%02d"%(int(flug[i].split('\t')[1].split('.')[2]),int(flug[i].split('\t')[1].split('.')[1]),int(flug[i].split('\t')[1].split('.')[0])):
						abflug,landung=int(flug[i].split('\t')[3]),int(flug[i].split('\t')[5])   
						logfile.write(string.join(["\nAbflug: ",flug[i].split('\t')[2]	,"\n"],''))		
						logfile.write(string.join(["Landung: ",flug[i].split('\t')[4]	,"\n"],''))		
				if abflug==0 or landung==0: logfile.write("\n /!\ keine Informationen ueber Abflugszeit oder Landezeit gefunden!\n")
				else: 	data=data[np.nanargmin(abs(data[:,0]-abflug)):np.nanargmin(abs(data[:,0]-landung))+1]
				logfile.write( string.join(['\nMeasurement Data exists from', time.strftime('%H:%M:%S',time.gmtime(data[0,0] )), 'to', time.strftime('%H:%M:%S',time.gmtime(data[-1,0] ))],' ')	)
			except ValueError: logfile.write("no informations about the flight...")
			logfile.close()

	# Prozentsatz an Incandescence Teilchen
			special = nans(data.shape[0],1)				
			for i in range(special.shape[0]):
				if data[i,14] > 0.00001: special[i] = data[i,4]/data[i,14]*100
			data=np.hstack((data,special))
			text_schreiben(data,datum)

	# --------------------------------------------- 		d)	--------------------------------------------	
	# schreibt die erstellte matrix in verschiedene Dateiformate
		if optionen_var[0]!=1:	data=np.loadtxt(string.join(['../txt/',datum,'_data.txt'],''),skiprows=1)
		if optionen_var[1]==1:	netcdf_schreiben(data[:,:],string.join(['../netcdf/',datum,'.nc'],''))
		if optionen_var[2]==1:	icartt_sp2_schreiben(data[:,:],datum,kampagne)
		if optionen_var[3]==1:	icartt_sp1a_schreiben(data[:,:],datum,kampagne)
		if optionen_var[4]==1:	model_schreiben(datum,data[:,:],string.join(['../model_30s/','k',datum,'_30sec_final.txt'],''))
		print datum, 'gelesen in %d s'%(time.clock()-start)
	return data


# --------------------------------------------- 		.txt			--------------------------------------------
def text_schreiben(data,datum):
	if os.path.exists(string.join(['../txt/',datum,'_data_roh.txt'],'')):os.remove(string.join(['../txt/',datum,'_data_roh.txt'],''))
	if os.path.exists(string.join(['../txt/',datum,'_data.txt'],'')):os.rename(string.join(['../txt/',datum,'_data.txt'],''),string.join(['../txt/',datum,'_data_roh.txt'],''))
	txt=open(string.join(['../txt/',datum,'_data.txt'],''),'w')
	np.savetxt(txt,data,fmt='%.5f',delimiter="\t")
	txt.close()

# --------------------------------------------- 		ICARTT SP2	--------------------------------------------
def icartt_sp2_header(datum,kampagne):
	#h=open('speicher/BC_Polar6_201407xx_R0-header.txt','r').read().split('\n')
	h=open(kampagne.icartt_sp2,'r').read().split('\n')
	h[6]=string.join([string.join(list(datum)[0:4],''),',',string.join(list(datum)[4:6],''),',',string.join(list(datum)[6:8],''),', ',time.strftime("%Y, %m, %d")],'')
	for i in range(len(h)): icartt.write(string.join([h[i],'\n'],''))
	return h[11]	

def icartt_sp2_data(data_original):
	global fill_typ
	fill_typ=np.nan	
	data=np.empty((data_original.shape[0],2))
	data[:]=np.nan
	index_list=[0,5]
	for i in range(len(index_list)):
		data[:,i]=data_original[:,index_list[i]]
	np.savetxt(icartt,data,fmt=['%d','%.5f'],delimiter=",",newline="\n")
	return data

def icartt_sp2_schreiben(data_original,datum,kampagne):
	global icartt
	name=string.join(['../icartt/','SP2_',datum,'.ict'],'')
	icartt=open(name,'w')
	fill_neu = icartt_sp2_header(datum,kampagne)
	icartt_sp2_data(data_original)
	icartt.close()
	punkt=open(name,'r').read()
	komma=open(name,'w')
	komma.write(punkt.replace("nan",fill_neu))
	komma.close()	

# --------------------------------------------- 		ICARTT SP1A	--------------------------------------------
def icartt_sp1a_header(datum,kampagne):
	#h=open('speicher/AOD_Polar6_201407xx_R0-header-HS.txt','r').read().split('\n')
	h=open(kampagne.icartt_sp1a,'r').read().split('\n')
	h[6]=string.join([string.join(list(datum)[0:4],''),',',string.join(list(datum)[4:6],''),',',string.join(list(datum)[6:8],''),', ',time.strftime("%Y, %m, %d")],'')
	for i in range(len(h)-1): icartt.write(string.join([h[i],'\n'],''))
	icartt.write(string.join([h[i+1]],''))
	return h[11].split(",")[0]	

def icartt_sp1a_data(data_original):
	global fill_typ
	fill_typ=np.nan	
	index_list=[0,23,24,26,28]
	data=np.empty((data_original.shape[0],len(index_list)))
	data[:]=np.nan
	for i in range(len(index_list)):
		data[:,i]=data_original[:,index_list[i]]
	data[data < 0]=np.nan
	np.savetxt(icartt,data,fmt=['%d','%.5f','%.5f','%.5f','%.5f'],delimiter=",",newline="\n")
	return data

def icartt_sp1a_schreiben(data_original,datum,kampagne):
	global icartt
	#SP1A_Polar6_20140704_R0.ict
	name=string.join(['../icartt/','SP1A_Polar6_',datum,'_R0.ict'],'')
	icartt=open(name,'w')
	fill_neu = icartt_sp1a_header(datum,kampagne)
	icartt_sp1a_data(data_original)
	icartt.close()
	ohne_fill=open(name,'r').read()
	mit_fill=open(name,'w')
	mit_fill.write(ohne_fill.replace("nan",fill_neu))
	mit_fill.close()


# ---------------------------------------------30s fuer Modellierer--------------------------------------------	
def model_schreiben(datum,data_original,name):
	global fill_typ
	gemittelt,fill_typ=30,np.nan
	fill_zw=np.empty(data_original.shape[0])
	fill_zw[:]=np.nan
	fill=mittelung(fill_zw[:],gemittelt)	
	data=mittelung(datetime.datetime.strptime(datum,'%Y%m%d').timetuple().tm_yday+data_original[:,0]/(24*60*60),gemittelt)
	data=np.hstack((data,mittelung(data_original[:,0],gemittelt)))
	data=np.hstack((data,fill[:]))
	data=np.hstack((data,fill[:]))
	for i in range(len(data)):	
		for j in range(2):
			a=data_original[i*gemittelt:(i+1)*gemittelt,45+j]
			if np.isnan(a[a.argsort()][0])==True:
				data[i,2+j]=fill_typ
			else:
				anzahl_non_nans= np.argmin(abs(np.nanargmax(a)-a.argsort()[:]))+1
				pos_non_nans=a.argsort()[0:anzahl_non_nans]
				data[i,2+j]=a[pos_non_nans[np.argmin(abs(14-pos_non_nans[:]))]]
	index_list=[47,40,41,42,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,5,23,24,26,28,-99,-99,-99,-99]
	for i in range(len(index_list)):
		if index_list[i]==-99:	data=np.hstack((data,fill[:]))
		else: 	data=np.hstack((data,mittelung(	data_original[:,index_list[i]]	,gemittelt)))
	np.savetxt(name,data,fmt='%.5f',delimiter="\t")
	punkt=open(name,'r').read()
	komma=open(name,'w')
	komma.write(punkt.replace(".",",").replace("nan","-999,9"))
	komma.close()

# ---------------------------------------------		netcdf		--------------------------------------------	
def netcdf_schreiben(data,name):
	f = netcdf.netcdf_file(name,'w')
	f.history = name
	f.createDimension('time',data.shape[0])
	Time =f.createVariable('Time','float64',('time',))
	Time[:] = data[:,0]
	Time.units='s'

	spuren=open("../scripte/speicher/spuren_info.txt","r").read().split("\n")
	variables=[]
	for i in range(len(spuren)-1):
		variables.append(f.createVariable(spuren[i].split(";")[1],'f',('time',)))
		variables[i][:]=data[:,i]
		variables[i].units=spuren[i].split(";")[3]
		variables[i].attributes=spuren[i].split(";")[-2]
	f.close()


def manuel(datum_list):	# 
	rohdaten=1					#	1-> rohdaten werden eingelesen und als .txt abgespeichert, 0-> .txt Datei wird geoeffnet
	netcdf=1					#	1-> netcdf wird abgelegt
	icartt_sp2=1			#
	icartt_sp1a=1			#
	model_30s=1				#
	sp2_timeshift,sp1a_timeshift=timeshifts_lesen('speicher/timeshifts.txt')
	einlesen(datum_list,"../messung/",sp2_timeshift,sp1a_timeshift,[rohdaten, peakschneiden, netcdf, icartt_sp2, icartt_sp1a, model_30s])


#manuel(["20140708","20140710"])


 
