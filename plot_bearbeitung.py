import Tkinter as tk
import os, sys, subprocess, ConfigParser,time, string
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import matplotlib.pyplot as pltlib


from plotten import *


def welcher():
	global start, ende
	x0,x1,y0,y1=[],[],[],[]
	for i in range(len(pos_info)):
		x0.append(start[0]>=pos_info[i][0] and start[0]<=pos_info[i][2])
		x1.append(ende[0]>=pos_info[i][0] and ende[0]<=pos_info[i][2])
		y0.append(start[1]<=pos_info[i][1] and start[1]>=pos_info[i][3])
		y1.append(ende[1]<=pos_info[i][1] and ende[1]>=pos_info[i][3])
	return x0,x1,y0,y1

def click_links(event):
	global start
	start=(event.x, event.y)

	
def drop_links(event):
	global ende
	initi()
	ende=(event.x,event.y)
	print start, ende
	x0,x1,y0,y1=welcher()
	wahl=[]
	for i in range(len(x0)):
		if plo.gemeinsame_achse=="y": wahl.append(i)
		elif x0[i]==1 and x1[i]==1 and y0[i]==1 and y1[i]==1: wahl.append(i)
	sub=wahl[0]
	posit=[]
	if start[1]>ende[1]:
		posit.append(((start[1]-pos_info[sub][1])/float(pos_info[sub][3]-pos_info[sub][1]))*(plo.sub[sub].yhigh-plo.sub[sub].ylow)+plo.sub[sub].ylow)
		posit.append(((ende[1]-pos_info[sub][1])/float(pos_info[sub][3]-pos_info[sub][1]))*(plo.sub[sub].yhigh-plo.sub[sub].ylow)+plo.sub[sub].ylow)
		posi=posit
		for j in range(len(wahl)):
			plo.sub[wahl[j]].ylow=posi[0]
			plo.sub[wahl[j]].yhigh=posi[1]
			axen[wahl[j]].set_ylim(posi[0],posi[1])
		canvas1.draw()

def click_rechts(event):
	global start
	start=(event.x, event.y)
	
def drop_rechts(event):
	global ende
	ende=(event.x,event.y)
	x0,x1,y0,y1=welcher()
	wahl=[]
	for i in range(len(x0)):
		if plo.gemeinsame_achse=="x": wahl.append(i)
		elif x0[i]==1 and x1[i]==1 and y0[i]==1 and y1[i]==1: wahl.append(i)
	sub=wahl[0]
	posit=[]
	if start[0]<ende[0]:
		posit.append(((start[0]-pos_info[sub][0])/float(pos_info[sub][2]-pos_info[sub][0]))*(plo.sub[sub].xhigh-plo.sub[sub].xlow)+plo.sub[sub].xlow)
		posit.append(((ende[0]-pos_info[sub][0])/float(pos_info[sub][2]-pos_info[sub][0]))*(plo.sub[sub].xhigh-plo.sub[sub].xlow)+plo.sub[sub].xlow)
		posi=posit
		for j in range(len(wahl)):
			if plo.sub[wahl[j]].gegen!=1:
				plo.sub[wahl[j]].xlow=posi[0]
				plo.sub[wahl[j]].xhigh=posi[1]
			if plo.sub[wahl[j]].gegen==1:
				plo.zeit_start=int(posi[0])
				plo.zeit_stop=int(posi[1])
			axen[wahl[j]].set_xlim(posi[0],posi[1])
			canvas1.draw()


def initi():
	for sub in pos_info:
		canvas0.create_line(0,sub[1],breite,sub[1],dash=(5,1),fill="green")
		canvas0.create_line(0,sub[3],breite,sub[3],dash=(5,1),fill="grey")
		canvas0.create_line(sub[0],0,sub[0],hoehe,dash=(5,1),fill="grey")
		canvas0.create_line(sub[2],0,sub[2],hoehe,dash=(5,1),fill="grey")

def achsen_begrenzung():
	global plo
	for i in range(len(plo.sub)):
		plo.sub[i].xlow=axen[i].get_xlim()[0]
		plo.sub[i].xhigh=axen[i].get_xlim()[1]
		plo.sub[i].ylow=axen[i].get_ylim()[0]
		plo.sub[i].yhigh=axen[i].get_ylim()[1]

def ausschnitt_plotten(root,datum,plots,spuren,i):
	global plo
	plots[i].zeit_start=plo.zeit_start	
	plots[i].zeit_stop=plo.zeit_stop	
	plot_bearbeitung(root,datum,plots,plots[i],spuren)
	sys.exit()

def plot_speichern(root,datum,plots,plot,spuren):
	canvas.print_figure('../plots/'+datum+'_'+str(plo.mittelung)+'_'+plo.name+'.png')
	zumhauptmenu()

def zumhauptmenu():
	root2.destroy()	
	os.system("python menu.py")	
	sys.exit()

def plot_bearbeitung(root,datum,plots,plot,spuren):
	print datum,plot.name
	global hoehe,breite,canvas0,canvas,canvas1,sub_index,pos_info,x_info,y_info,plo,start,ende,root2,oben,axen,canvas
	start,ende=(0,0),(0,0)
	plo=plot
	try:root.destroy()
	except:pass
	root2 = tk.Tk()  
	root2.geometry('1000x800+800+400')
	root2.grid()

	canvasFig=pltlib.figure(1)
	Fig,axen,canvas= plotten(["20140708"],plot,spuren)
	canvas1 = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(Fig, master=root2)
	canvas0=canvas1.get_tk_widget()

	canvas0.bind("<Button-1>",click_links)
	canvas0.bind("<ButtonRelease-1>",drop_links)
	canvas0.bind("<Button-3>",click_rechts)
	canvas0.bind("<ButtonRelease-3>",drop_rechts)

	canvas0.grid(row=2,column=0,rowspan=7,columnspan=7)
	canvas1.show()

	breite,hoehe =canvas0.winfo_width(),canvas0.winfo_height()  

	pos_info=[]
	for j in range(len(axen)):
		bbox= axen[j].get_position()
		bbox=[bbox.x0,bbox.y0,bbox.width,bbox.height]
		pos_info.append([bbox[0]*breite,hoehe-bbox[1]*hoehe,(bbox[2]+bbox[0])*breite,hoehe-(bbox[1]+bbox[3])*hoehe])

	achsen_begrenzung()


	info=tk.Label(root2,text="Begrenzung der Y-Achse: Linke Maustaste auf einem Subplot gedrueckt von unten nach oben ziehen \nBegrenzung der X-Achse: Rechte Maustaste auf einem Subplot gedrueckt von links nach rechts ziehen \nFalls die Zeit begrenzt wurde, kann fuer den Zeitausschnitt ein anderer Plot erstellt werden!").grid(row=10,column=0,columnspan=4)
	exit=tk.Button(root2,text="Ende",command=lambda:sys.exit("Bis bald")).grid(row=0,column=0)
	zuhauptmenu=tk.Button(root2,text="zum Hauptmenu",command=lambda:zumhauptmenu()).grid(row=0,column=1)
	erneut=tk.Button(root2,text="Plot speichern",command=lambda:plot_speichern(root2,datum,plots,plot,spuren)).grid(row=0,column=2)
	if plot.sub[0].gegen==1 and plot.sub[1].gegen==1:
		ausschnitt=tk.Menubutton(root2,text="fuer gewahltes Zeitfenster anderen Plot erstellen")
		ausschnitt.grid(row=0,column=3)
		ausschnitt.menu=tk.Menu(ausschnitt)
		for i in range(len(plots)):
			ausschnitt.menu.add_command(label=plots[i].name,command=lambda idd=i:ausschnitt_plotten(root2,datum,plots,spuren,idd))
		ausschnitt['menu']=ausschnitt.menu

	root2.mainloop()


