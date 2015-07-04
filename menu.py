################################# import packages/libraries
import Tkinter as tk
import os, sys, subprocess, ConfigParser,time, string
import numpy as np
import warnings
warnings.simplefilter("error")

from schreiben_lesen import * 
from plotten import * 
from abgleich_pressure import *
from igor_steuern import *
#from flugplot import *
from plot_bearbeitung import *


			
def trace_neu(k,h,j):
	plots[k].sub[h].traces.pop(j)
	plot_einstellungen(k)

def update_trace(k,h,j,i):
	if j==None: plots[k].sub[h].gegen=i
	else:
		if j==len(plots[k].sub[h].traces): plots[k].sub[h].traces.append(i)
		if i== -99:  plots[k].sub[h].traces.pop(j)
		else: plots[k].sub[h].traces[j]=i
	plot_einstellungen(k)

def update_marker(k,h,j,i):
	spuren[plots[k].sub[h].traces[j]].marker=marker_list[i]
	plot_einstellungen(k)

def update_farbe(k,index,farbe):
	farb.destroy()
	spuren[index].farbe=farbe
	plot_einstellungen(k)

def farbpalette(kd,index):
	global farb
	farb = tk.Tk()
	farb.geometry('+800+80')
	farb.grid()
	farb.title("alle farben sind schoen")	
	import colorsys
	N = 40
	HSV_tuples = [(x*1.0/N, 1.0, 1.0) for x in range(N)]
	RGB_tuples = map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples)
	for i in range(len(RGB_tuples)):
		farbe='#%02d%02d%02d'%(RGB_tuples[i][0]*99,RGB_tuples[i][1]*99,RGB_tuples[i][2]*99)
		tk.Frame(farb,bg=farbe,width=30,height=70).grid(row=1,column=i,sticky=tk.W+tk.E+tk.N+tk.S)
		tk.Button(farb,text='',command=lambda wahl=farbe: update_farbe(kd,index,wahl)).grid(row=1,column=i)
	farb.update()

def spuren_cascade(ding,j,k,h):
	ding.menu = tk.Menu(ding)
	ding.menu.sp2 = tk.Menu(ding.menu)
	ding.menu.sp1a = tk.Menu(ding.menu)
	ding.menu.wetter = tk.Menu(ding.menu)
	ding.menu.aimms = tk.Menu(ding.menu)
	ding.menu.add_command(label='nichts',command=lambda kd=k,hd=h,jd=j:update_trace(kd,hd,jd,-99))
	for i in range(len(spuren)):
		if spuren[i].typ=="SP2":
			ding.menu.sp2.add_command(label=spuren[i].label,command=lambda kd=k, hd=h,jd=j,id=i :update_trace(kd,hd,jd,id))
		if spuren[i].typ=="SP1A":
			ding.menu.sp1a.add_command(label=spuren[i].label,command=lambda kd=k, hd=h,jd=j,id=i :update_trace(kd,hd,jd,id))
		if spuren[i].typ=="Wetter":
			ding.menu.wetter.add_command(label=spuren[i].label,command=lambda kd=k, hd=h,jd=j,id=i :update_trace(kd,hd,jd,id))
		if spuren[i].typ=="AIMMS":
			ding.menu.aimms.add_command(label=spuren[i].label,command=lambda kd=k, hd=h,jd=j,id=i :update_trace(kd,hd,jd,id))
	ding.menu.add_cascade(label='sp2',menu=ding.menu.sp2)
	ding.menu.add_cascade(label='sp1a',menu=ding.menu.sp1a)
	ding.menu.add_cascade(label='wetter',menu=ding.menu.wetter)
	ding.menu.add_cascade(label='AIMMS',menu=ding.menu.aimms)
	ding['menu'] = ding.menu
	return ding

def eingabe(name,inhalt,ort,breite):
	if name!=None:tk.Label(root,text=name).grid(row=ort[0],column=ort[1],columnspan=ort[2])
	objekt=tk.Entry(root,width=breite)
	objekt.insert(0, inhalt)
	objekt.grid(row=ort[0],column=ort[1]+1,columnspan=ort[2])
	return objekt

def spuren_einstellungen(k,pl_row,pl_col):
	global wahl,legcol,ylabel,mittel,name,gemeinsam
	ylabel,yoption,xlabel,xoption,legcol,plottyp=[],[],[],[],[],[]
	for h in range(len(plots[k].sub)):	
		wahl,colors,markers=[],[],[]
		if h==0:abstand=pl_row+2
		if h>0:abstand=len(plots[k].sub[h-1].traces)+abstand+2
		tk.Frame(root,bg='#000000',width=400,height=30).grid(row=abstand-1,column=pl_col,columnspan=4)
		tk.Label(root,text='Subplot %d,%d'%(plots[k].sub[h].position[0],plots[k].sub[h].position[1])).grid(row=abstand-1,column=pl_col)
		for j in range(len(plots[k].sub[h].traces)+1):
			if j<len(plots[k].sub[h].traces):wahl.append(tk.Menubutton(root, width=30,text=spuren[plots[k].sub[h].traces[j]].label, underline=0))
			if j==len(plots[k].sub[h].traces):wahl.append(tk.Menubutton(root, width=30,text='nichts', underline=0))
			wahl[j].grid(row=abstand+j,column=pl_col)
			wahl[j]=spuren_cascade(wahl[j],j,k,h)

		for j in range(len(plots[k].sub[h].traces)):
			colors.append(tk.Button(root,background=spuren[plots[k].sub[h].traces[j]].farbe, text=spuren[plots[k].sub[h].traces[j]].farbe, command= lambda kd=k,hd=h,jd=j:farbpalette(kd,plots[kd].sub[hd].traces[jd])))
			colors[j].grid(row=abstand+j,column=pl_col+1)
			tk.Frame(root,width=20,height=23,background=spuren[plots[k].sub[h].traces[j]].farbe).grid(row=abstand+j,column=pl_col+2)
		
			markers.append(tk.Menubutton(root, text=spuren[plots[k].sub[h].traces[j]].marker, underline=0))
			markers[j].grid(row=abstand+j,column=pl_col+3)
			markers[j].menu = tk.Menu(markers[j])		
			for i in range(len(marker_list)):
				markers[j].menu.add_command(label=marker_list[i] ,command=lambda kd=k,hd=h,jd=j,id=i:update_marker(kd,hd,jd,id))
			markers[j]['menu'] = markers[j].menu

		xlabel.append(eingabe("x-Achsenbeschriftung",str(plots[k].sub[h].xlabel),[abstand,pl_col+4,1],25))
		ylabel.append(eingabe("y-Achsenbeschriftung",str(plots[k].sub[h].ylabel),[abstand+1,pl_col+4,1],25))


		gegen=tk.Menubutton(root, width=20,text=spuren[plots[k].sub[h].gegen].label, underline=0)
		gegen.grid(row=abstand-1,column=pl_col+5)
		gegen=spuren_cascade(gegen,None,k,h)	
		tk.Label(root,text="geplottet gegen").grid(row=abstand-1,column=pl_col+4)
		plottyp.append(eingabe("auf",str(plots[k].sub[h].plottyp),[abstand-1,pl_col+6,1],4))	
		legcol.append(eingabe("spalten in legende",str(plots[k].sub[h].legcol),[abstand,pl_col+6,1],4))		

	pl_row,pl_col=1,5
	mittel=eingabe("gemittelte Punkte",str(plots[k].mittelung),[pl_row,pl_col,1],7)
	name=eingabe("name",plots[k].name,[pl_row+1,pl_col,1],7)
	gemeinsam=eingabe("gemeinsame Achse",plots[k].gemeinsame_achse,[pl_row,pl_col+2,1],7)


def plot_einstellungen(k):
	global root
	root.destroy()
	root = tk.Tk()
	root.geometry('1000x800+400+80') 
	root.grid()
	root.title("standart einstellungen")
	tk.Button(root,text="hauptmenu",command=lambda:hauptmenu()).grid(row=1,column=1)
	spuren_einstellungen(k,4,1)
	ploo=tk.Menubutton(root,width=20,text=plots[k].name,underline=0)
	ploo.grid(row=4,column=1)
	ploo.menu = tk.Menu(ploo)
	for p in range(len(plots)):
		ploo.menu.add_command(label=plots[p].name,command=lambda pd=p:plot_einstellungen(pd))
	ploo.menu.add_command(label="neue Plotvorlage",command=lambda pd=p:plot_einstellungen(pd))
	ploo['menu'] = ploo.menu
	tk.Button(root,text="speichern",command=lambda:speichern(k)).grid(row=1,column=2)
	root.update()
	root.mainloop()	

def speichern(k):
	plots[k].mittelung=int(mittel.get())
	plots[k].name=name.get()
	plots[k].gemeinsame_achse=gemeinsam.get()
	for i in range(len(ylabel)):
		plots[k].sub[i].ylabel=ylabel[i].get()
		plots[k].sub[i].legcol=int(legcol[i].get())
	spuren_schreiben(spuren)
	plots_schreiben(plots)

def ordnerwahl():
	global root,auswahl_list
	root.destroy()
	root = tk.Tk()
	root.geometry('+800+400')
	root.grid()
	root.title("ordnerwahl")
	path=os.path.expanduser('../')
	auswahl_list=[]
	for i in range(len(os.listdir(path))):
		tk.Button(root,text=os.listdir(path)[i],command= lambda id=i:hauptmenu(string.join(["../",os.listdir(path)[id]],''))).grid(row=i,column=1)
	root.update()
	root.mainloop()

def check_all(liste):
	for i in range(len(liste)):
		liste[i].set(1)
		
def uncheck_all(liste):
	for i in range(len(liste)):
		liste[i].set(0)

def kampagnen_update(kampagne_file):
	global kampagne,root2
	kampagne=kampagne_lesen(kampagne_file)
	hauptmenu()

def hauptmenu(pfad="../messung"):
	global root,checks,auswahl,kampagne
	try: root.destroy()
	except NameError,TclError: pass
	root = tk.Tk()
	root.geometry('1000x800+800+400')
	root.grid()
	root.title("Hauptmenu")

# drop down menu zur kampagnenwahl

	kampagnen=[]
	path=os.path.expanduser('speicher/')
	for file in sorted(os.listdir(path)):
		if os.path.splitext(file)[0].split('_')[0] == "kampagne":
			kampagnen.append(os.path.join(path,file))
	path=os.path.expanduser('../')

	try:	kampagnen_menu=tk.Menubutton(root, width=20,text=kampagne.name, underline=0)
	except:	kampagnen_menu=tk.Menubutton(root, width=20,text="...", underline=0)

	kampagnen_menu.grid(row=1,column=9)
	tk.Label(root,text="Kampagne:").grid(row=1,column=8)
	kampagnen_menu.menu = tk.Menu(kampagnen_menu)
	for i in range(len(kampagnen)):
		kampagnen_menu.menu.add_command(label=kampagnen[i],command=lambda kamp=i:kampagnen_update(kampagnen[kamp]))
	kampagnen_menu['menu'] = kampagnen_menu.menu	


	plo_list=[]
	for i in range(len(plots)):
		plo_list.append([])
	path=os.path.expanduser('../plots/')
	for i in range(len(sorted(os.listdir(path)))):
		for j in range(len(plots)):
			if sorted(os.listdir(path))[i].split('_')[-1].split('.')[0]==plots[j].name:	
				plo_list[j].append(sorted(os.listdir(path))[i].split('_')[0])
	path=os.path.expanduser(pfad)
	auswahl,igor_list=[],[]
	for file in sorted(os.listdir(path)):
		if os.path.isfile(os.path.join(path,file)):
			try: 
				int(os.path.splitext(file)[0].split('-')[0])
				auswahl.append(os.path.splitext(file)[0].split('-')[0])	
			except ValueError:	pass
	path=os.path.expanduser('../../igor/messung/')
	for file in sorted(os.listdir(path)):
		try: 
			x=int(os.path.splitext(file)[0].split('-')[0])
			if (str(x) in auswahl)==False:	auswahl.append(os.path.splitext(file)[0].split('-')[0])	
			if str(x) in auswahl: igor_list.append(os.path.splitext(file)[0].split('-')[0])
		except ValueError:	pass
	checks=[]
	for we in range(len(plots)): 
		if plots[we].name=="wetter": 
			wetter=we
	for i in range(len(list(set(auswahl)))):
		checks.append(tk.IntVar())
		if sorted(list(set(auswahl)))[i] in igor_list:tk.Button(root,text='',command=lambda datum=sorted(list(set(auswahl)))[i]:igor_steuern(datum)).grid(row=i+3,column=3)
		tk.Checkbutton(root,text=sorted(list(set(auswahl)))[i],variable=checks[i]).grid(row=i+3,column=4)
		for j in range(len(plots)):
			if sorted(list(set(auswahl)))[i] in plo_list[j]: 
				tk.Button(root,text=plots[j].name,command=lambda jd=j, datum=sorted(list(set(auswahl)))[i]:plot_bearbeitung(root,datum,plots,plots[jd],spuren)).grid(row=i+3,column=7+j)

	tk.Label(root,text="igor einlesen").grid(row=1,column=3)
	tk.Button(root,text="plot einstellungen",command=lambda:plot_einstellungen(0)).grid(row=1,column=5,columnspan=2)
	tk.Button(root,text="zur Ordnerwahl",command=lambda:ordnerwahl()).grid(row=1,column=1,columnspan=2)
	tk.Button(root,text="Ende",command=lambda:sys.exit("Bis bald")).grid(row=1,column=0)
	tk.Button(root,text="alle",command=lambda:check_all(checks)).grid(row=i+4,column=4)	
	tk.Button(root,text="keine",command=lambda:uncheck_all(checks)).grid(row=i+5,column=4)	
	tk.Label(root,text='SP2 timeshift: %d s'%sp2_timeshift).grid(row=2,column=1)
	tk.Label(root,text='SP1A timeshift: %d s'%sp1a_timeshift).grid(row=3,column=1)

	c_row,c_col=3,1
	optionen_name=['Rohdaten einlesen','netcdf file erstellen','SP2 ICARTT erstellen','SP1A ICARTT erstellen','30s Mittelung erstellen']
	schreiben=[]
	for i in range(len(optionen_name)):
		schreiben.append(tk.IntVar())
		tk.Checkbutton(root,text=optionen_name[i],variable=schreiben[i]).grid(row=c_row+2+i,column=c_col)

	tk.Label(root,text="Plots anpassen").grid(row=2,column=c_col+6,columnspan=len(plots))
	tk.Label(root,text=' ').grid(row=c_row+len(optionen_name)+2,column=c_col)
	tk.Label(root,text='Plots').grid(row=c_row+len(optionen_name)+3,column=c_col)
	ploo,ploop=[],[]
	c_row,c_col=39,1
	for j in range(len(plots)+2):
		ploop.append(tk.IntVar())
		if j<len(plots): ploo.append(tk.Checkbutton(root,text=plots[j].name,variable=ploop[j]).grid(row=c_row+i+j,column=c_col))
		if j==len(plots): ploo.append(tk.Checkbutton(root,text="Druck-Abgleich",variable=ploop[j]).grid(row=c_row+i+j+1,column=c_col))
		if j>len(plots): ploo.append(tk.Checkbutton(root,text="Flugroute",variable=ploop[j]).grid(row=c_row+i+j+1,column=c_col))
	tk.Button(root,text="los",command= lambda: vorbereitung(pfad,schreiben,ploop)).grid(row=c_row+i+j+3,column=c_col)
	root.update()			
	root.mainloop()

def vorbereitung(pfad,schreiben,ploop):
	global kampagne
	datum_list=[]
	for i in range(len(checks)):
		if checks[i].get()==1:datum_list.append(sorted(list(set(auswahl)))[i])
	print datum_list
	for k in range(len(schreiben)):
		if isinstance(schreiben[k],int)==False:schreiben[k]=schreiben[k].get()
	if sum(schreiben)>0:
		einlesen(datum_list,pfad,sp2_timeshift,sp1a_timeshift,schreiben,kampagne)
	for j in range(len(ploop)-2):
		if ploop[j].get()==1: plotten(datum_list,plots[j],spuren)
	if ploop[j+1].get()==1: abgleich_pressure(datum_list)
	if ploop[j+2].get()==1: flugroute(datum_list)
	hauptmenu()



marker_list=['o','s','v','<','>']
spuren=spuren_lesen('speicher/spuren_info.txt')
plots=plots_lesen()
sp2_timeshift,sp1a_timeshift=timeshifts_lesen('speicher/timeshifts.txt')
#kampagne=kampagne_lesen('speicher/kampagne_sommer_2014.txt')

hauptmenu()
