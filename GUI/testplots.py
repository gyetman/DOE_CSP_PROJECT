#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  9 16:49:12 2018

@author: adamatia
"""
#%%
from tkinter import *

window = Tk()
User_input = Entry()
User_input.pack()
window.mainloop()
user_problem  = int(User_input.get())

#%% test 
import matplotlib.pyplot as plt
plt.plot(a,Mfv,linestyle='-',marker='o')
axes=plt.gca()
axes.set_ylim([150,270])

