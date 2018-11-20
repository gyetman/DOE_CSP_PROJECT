# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 00:01:22 2018

@author: vikas
"""

from PSA.Model_MED_PSA import medPsa as psaMed
from SAM.SamCspPhysical import samCspPhysical as SamCsp

sam = SamCsp()
sam.data_free()

psa = psaMed()