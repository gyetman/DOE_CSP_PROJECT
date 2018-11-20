#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  9 16:49:12 2018

@author: adamatia
"""
#%% test GUI for inputs.... 
from tkinter import *

root = Tk()
root.title("New Application")
root.geometry("640x640+0+0")
heading=Label(root, text="MED Parameter Inputs",font=("arial",40,"bold"),fg="steelblue").pack()

label=Label(root, text="Seawater inlet temperature,ºC",font=("arial",12,"bold"),fg="black").place(x=10,y=55)

Tcwin=DoubleVar()
Tcwin_box=Entry(root,textvariable=Tcwin,width=5,bg="lightgreen").place(x=250,y=58)




root.mainloop()
#%% test plotting of MED Model Case Study
import matplotlib.pyplot as plt
from Model_MED_PSA_AAA_v1 import *
a=np.arange(1,Nef+1)
plt.plot(a,Mfv,linestyle='-',marker='o')
axes=plt.gca()
axes.set_ylim([150,270])

plt.plot(a,Mb*3600,linestyle='-',marker='o')
axes2=plt.gca()
axes2.set_ylim([4000,8000])
