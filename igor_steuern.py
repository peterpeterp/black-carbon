################################# import packages/libraries

import Tkinter as tk
import os, sys, subprocess, ConfigParser,time, string
import numpy as np
import warnings
warnings.simplefilter("error")

def igor_steuern(datum):
	pfad="../../igor/procedures"
	igor_alt=open(pfad+'/einlesen_sicherung.ipf','r').read().split('\n')
	igor_neu=open(pfad+'/einlesen.ipf','w')

	pfad="../../igor/messung"

	ordner_list=[]
	index_list=[]
	for item in os.listdir(pfad):
		if item.split('-')[0]==datum:ordner_list.append(item)
	igor_alt[27]=string.join(['strconstant datum="',datum,'"'],'')

	for j in range(len(ordner_list)):
		pfad_ordner=pfad+"/"+ordner_list[j]
		data_list = sorted(os.listdir(pfad_ordner))
		indices=[]
		for i in range(len(data_list)):
			if data_list[i].split('.')[-1]=='hk':hk_file=data_list[i]
			if data_list[i].split('.')[-1]=='sp2b':indices.append(data_list[i].split('.')[0].split('x')[-1])
		igor_alt[30+4*j]=string.join(['strconstant ordner%d="'%(j+1),ordner_list[j],':"'],'')
		igor_alt[31+4*j]=string.join(['strconstant indices%d="'%(j+1),string.join(indices,';'),'"'],'')
		igor_alt[32+4*j]='constant anzahl%d=%d'%(j+1,len(indices))
	igor_alt[43]='constant ordner_anzahl=%d'%(len(ordner_list))
	igor_alt[28]=string.join(['strconstant hk_ordner="root:',"'",hk_file.split('.')[0],"_HK'",'"'],'')
	igor_alt[47]="string hk_file=quelle_linux+ordner1+"+'"'+hk_file+'"'
	for line in igor_alt:
		igor_neu.write(line+'\n')
	igor_neu.close()
