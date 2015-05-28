################################# import packages/libraries
import os, sys, subprocess, ConfigParser,time, string
import numpy as np
import matplotlib.pyplot as plt
from funktionen import * 

def ableitung(x,y):
        dev=np.empty([y.shape[0],2])
        for i in range(y.shape[0]-1):
                a=float(y[i+1]-y[i])
                b=float(x[i+1]-x[i])
                dev[i,1]=a/b
                dev[i,0]=x[i]
        return dev

def abgleich_pressure(datum_list):
	for k in range(len(datum_list)):
		start = time.clock()
		datum=datum_list[k]
		dat=np.genfromtxt(string.join(["../txt/",datum,"_data.txt"],''),skip_header=1)
		zeit_start=dat[0,0]
		zeit_stop=dat[-1,0]
		fig=plt.figure(figsize=(18,10))
		fig.suptitle(datum)

		mi1=5
		mi2=1
		mispta=1

		ax1=fig.add_subplot(221)
		try:
			abl=ableitung(mittelung(dat[:,0],mi1),mittelung(dat[:,2],mi1))
			miabl=mittelung(abl[:,1],mi2)
			zeit=mittelung(abl[:,0],mi2)
			ax1.plot(zeit,miabl,label="SP2 pressure deviation")
		except (IndexError,ValueError): pass
		try:
			abl=ableitung(mittelung(dat[:,0],mi1),mittelung(dat[:,42]*0.01,mi1))
			miabl=mittelung(abl[:,1],mi2)
			zeit=mittelung(abl[:,0],mi2)
			ax1.plot(zeit,miabl,c="g",linestyle="--",label="AIMMS pressure deviation")
		except (IndexError,ValueError): pass
		ax1.legend(loc="upper left")
		ax1.set_xlim(zeit_start,zeit_stop)
		ax2=fig.add_subplot(222)
		try:
			x,y=[],[]
			for i in range(dat.shape[0]):
						  if np.isnan(dat[i,16])==False:
						          x.append(dat[i,0])
						          y.append(dat[i,16])
			x=np.array(x)
			y=np.array(y)
			abl=ableitung(x,y)
			zeit=mittelung(abl[:,0],mispta)
			yabl=mittelung(abl[:,1],mispta)
			ax2.plot(zeit,yabl,c="r",linewidth=2,label="SP1A altitude deviation")
		except (IndexError,ValueError): pass
		try:
			abl=ableitung(mittelung(dat[:,0],mi1),mittelung(dat[:,36],mi1))
			miabl=mittelung(abl[:,1],mi2)
			zeit=mittelung(abl[:,0],mi2)
			ax2.plot(zeit,miabl,c="c",linestyle='--',label="Wetter GPS altitude deviation")
		except (IndexError,ValueError): pass
		try:
			abl=ableitung(mittelung(dat[:,0],mi1),mittelung(dat[:,47],mi1))
			miabl=mittelung(abl[:,1],mi2)
			zeit=mittelung(abl[:,0],mi2)
			ax2.plot(zeit,miabl,c="g",linestyle='-.',label="AIMMS altitude deviation")
		except (IndexError,ValueError): pass
		ax2.invert_yaxis()
		ax2.legend(loc="upper right")
		ax2.set_xlim(zeit_start,zeit_stop)

		ax1=fig.add_subplot(223)
		try:
			ax1.plot(dat[:,0],dat[:,2],label="SP2 pressure")
			ax1.scatter(dat[:,0],dat[:,42]*0.01,c="g",label="AIMMS pressure")
			ax1.invert_yaxis()
			ax1.set_ylabel("pressure")
			ax1.set_xlabel("seconds of day")
			ax1.legend(loc="upper left")
		except (IndexError,ValueError): pass
		ax1.set_xlim(zeit_start,zeit_stop)

		ax2=fig.add_subplot(224)
		try:
			ax2.scatter(dat[:,0],dat[:,16],c="r",label="SP1A altitude")
			ax2.plot(dat[:,0],dat[:,36],c="c",linestyle='--',label="Wetter altitude")
			ax2.plot(dat[:,0],dat[:,47],c="g",label="AIMMS altitude")
			ax2.set_ylabel("altitude")
			ax2.set_xlabel("seconds of day")
			ax2.legend(loc="upper right")
			ax2.set_xlim(zeit_start,zeit_stop)
		except (IndexError,ValueError): pass
		plt.savefig(string.join(["../plots/",datum,"_pressure_abgleich_sp2_sp1a.eps"],''))
		print string.join([datum,"_pressure_abgleich_sp2_sp1a.eps geplottet in %d s"%(time.clock()-start)],'')
	return 0

#abgleich_pressure(["20140708"])
