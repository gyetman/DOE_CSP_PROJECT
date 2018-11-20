#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  7 10:22:10 2018

@author: adamatia
"""

def pSatW(temp):
#Stoffparameter_H2O
#del = temp + nreg4 ( 9 ) ./ (temp - nreg4 ( 10 ))
#Aco = del.^  2  + nreg4 ( 1 ) .* del + nreg4 ( 2 );
#Bco = nreg4 ( 3 ) .* del .^  2  + nreg4 ( 4 ) .* del + nreg4 ( 5 )
#cco = nreg4 ( 6 ) .* del .^  2  + nreg4 ( 7 ) .* del + nreg4 ( 8 )
#pSatW = ( 2.* cco ./ (-Bco + (Bco .^  2  -  4.* Aco .* cco).^  0.5 ))^ 4.*10
    return temp/1000