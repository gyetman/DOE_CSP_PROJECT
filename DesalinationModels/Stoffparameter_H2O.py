#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  7 10:50:54 2018

@author: adamatia
"""
import numpy as np
# ORIGINAL COMMENTS FROM MATLAB VERSION 
# This M-file contains the coefficients for calculating the thermodynamical properties 
#  of water and steam according to the release of the IAPWS industrial formulation 1997
#
#  This routine has been adapted from:
#  water97_v12: A collection of Visual Basic functions
#  for calculating properties of water and steam.
#
#  Source: IAPWS-IF97. For details see
#  http://chemengineer.about.com/library/weekly/aa071700a.htm
#  http://chemengineer.about.com/library/weekly/aa073100a.htm
#  http://chemengineer.about.com/library/weekly/aa081400a.htm
#
#
#  Version 1.2, 02/06/01:   starting value for iteration in densreg3 for
#                           supercritical temperatures changed from 500 to 600
#
#
#  Version 1.1, 01/29/01:   mistake in calculation of partial derivatives
#                           for thermal conductivity corrected
#
#  [c] B. Spang, About Guide to Chemical Engineering, Hamburg, 2000, 2001
#      E-Mail: chemengineer.guide@about.com
#
#  The original coefficients have been developed as an ADD-IN for Microsoft Excel.
#  The routines for saturated Water/Lithiumbromid solution have been added by
#  S. Petersen and J. Albers, IEMB, Salzufer 14, 10587 Berlin, Germany albers@iemb.de
#  according to Feuerecker ....
#
#  For the use with MATLAB it was neccesary to change some indizes which starts with zero
#  in the IAPWS formulation. They are now starting with one.
#
rgas_water = 461.526

# AddIn sub InitFieldsreg1[]
ireg1=np.zeros((34,1))
ireg1[0] = 0
ireg1[1] = 0
ireg1[2] = 0
ireg1[3] = 0
ireg1[4] = 0
ireg1[5] = 0
ireg1[6] = 0
ireg1[7] = 0
ireg1[8] = 1
ireg1[9] = 1
ireg1[10] = 1
ireg1[11] = 1
ireg1[12] = 1
ireg1[13] = 1
ireg1[14] = 2
ireg1[15] = 2
ireg1[16] = 2   # fehlte bei Stefan
ireg1[17] = 2
ireg1[18] = 2
ireg1[19] = 3
ireg1[20] = 3
ireg1[21] = 3
ireg1[22] = 4
ireg1[23] = 4
ireg1[24] = 4
ireg1[25] = 5
ireg1[26] = 8
ireg1[27] = 8
ireg1[28] = 21
ireg1[29] = 23
ireg1[30] = 29
ireg1[31] = 30
ireg1[32] = 31
ireg1[33] = 32

jreg1=np.zeros((34,1))
jreg1[0] = -2
jreg1[1] = -1
jreg1[2] = 0
jreg1[3] = 1
jreg1[4] = 2
jreg1[5] = 3
jreg1[6] = 4
jreg1[7] = 5
jreg1[8] = -9
jreg1[9] = -7
jreg1[10] = -1
jreg1[11] = 0
jreg1[12] = 1
jreg1[13] = 3
jreg1[14] = -3
jreg1[15] = 0
jreg1[16] = 1
jreg1[17] = 3
jreg1[18] = 17
jreg1[19] = -4
jreg1[20] = 0
jreg1[21] = 6
jreg1[22] = -5
jreg1[23] = -2
jreg1[24] = 10
jreg1[25] = -8
jreg1[26] = -11
jreg1[27] = -6
jreg1[28] = -29
jreg1[29] = -31
jreg1[30] = -38
jreg1[31] = -39
jreg1[32] = -40
jreg1[33] = -41

nreg1=np.zeros((34,1))
nreg1[0] = 0.14632971213167
nreg1[1] = -0.84548187169114
nreg1[2] = -3.756360367204
nreg1[3] = 3.3855169168385
nreg1[4] = -0.95791963387872
nreg1[5] = 0.15772038513228
nreg1[6] = -0.016616417199501
nreg1[7] = 8.1214629983568E-04
nreg1[8] = 2.8319080123804E-04
nreg1[9] = -6.0706301565874E-04
nreg1[10] = -0.018990068218419
nreg1[11] = -0.032529748770505
nreg1[12] = -0.021841717175414
nreg1[13] = -5.283835796993E-05
nreg1[14] = -4.7184321073267E-04
nreg1[15] = -3.0001780793026E-04
nreg1[16] = 4.7661393906987E-05
nreg1[17] = -4.4141845330846E-06
nreg1[18] = -7.2694996297594E-16
nreg1[19] = -3.1679644845054E-05
nreg1[20] = -2.8270797985312E-06
nreg1[21] = -8.5205128120103E-10
nreg1[22] = -2.2425281908E-06
nreg1[23] = -6.5171222895601E-07
nreg1[24] = -1.4341729937924E-13
nreg1[25] = -4.0516996860117E-07
nreg1[26] = -1.2734301741641E-09
nreg1[27] = -1.7424871230634E-10
nreg1[28] = -6.8762131295531E-19
nreg1[29] = 1.4478307828521E-20
nreg1[30] = 2.6335781662795E-23
nreg1[31] = -1.1947622640071E-23
nreg1[32] = 1.8228094581404E-24
nreg1[33] = -9.3537087292458E-26
    
# AddIn InitFieldsreg2[]
j0reg2=np.zeros((9,1))
j0reg2[0] = 0
j0reg2[1] = 1
j0reg2[2] = -5
j0reg2[3] = -4
j0reg2[4] = -3
j0reg2[5] = -2
j0reg2[6] = -1
j0reg2[7] = 2
j0reg2[8] = 3

n0reg2=np.zeros((9,1))
n0reg2[0] = -9.6927686500217
n0reg2[1] = 10.086655968018
n0reg2[2] = -0.005608791128302
n0reg2[3] = 0.071452738081455
n0reg2[4] = -0.40710498223928
n0reg2[5] = 1.4240819171444
n0reg2[6] = -4.383951131945
n0reg2[7] = -0.28408632460772
n0reg2[8] = 0.021268463753307

ireg2=np.zeros((43,1))
ireg2[0] = 1
ireg2[1] = 1
ireg2[2] = 1
ireg2[3] = 1
ireg2[4] = 1
ireg2[5] = 2
ireg2[6] = 2
ireg2[7] = 2
ireg2[8] = 2
ireg2[9] = 2
ireg2[10] = 3
ireg2[11] = 3
ireg2[12] = 3
ireg2[13] = 3
ireg2[14] = 3
ireg2[15] = 4
ireg2[16] = 4
ireg2[17] = 4
ireg2[18] = 5
ireg2[19] = 6
ireg2[20] = 6
ireg2[21] = 6
ireg2[22] = 7
ireg2[23] = 7
ireg2[24] = 7
ireg2[25] = 8
ireg2[26] = 8
ireg2[27] = 9
ireg2[28] = 10
ireg2[29] = 10
ireg2[30] = 10
ireg2[31] = 16
ireg2[32] = 16
ireg2[33] = 18
ireg2[34] = 20
ireg2[35] = 20
ireg2[36] = 20
ireg2[37] = 21
ireg2[38] = 22
ireg2[39] = 23
ireg2[40] = 24
ireg2[41] = 24
ireg2[42] = 24

jreg2=np.zeros((43,1))
jreg2[0] = 0
jreg2[1] = 1
jreg2[2] = 2
jreg2[3] = 3
jreg2[4] = 6
jreg2[5] = 1
jreg2[6] = 2
jreg2[7] = 4
jreg2[8] = 7
jreg2[9] = 36
jreg2[10] = 0
jreg2[11] = 1
jreg2[12] = 3
jreg2[13] = 6
jreg2[14] = 35
jreg2[15] = 1
jreg2[16] = 2
jreg2[17] = 3
jreg2[18] = 7
jreg2[19] = 3
jreg2[20] = 16
jreg2[21] = 35
jreg2[22] = 0
jreg2[23] = 11
jreg2[24] = 25
jreg2[25] = 8
jreg2[26] = 36
jreg2[27] = 13
jreg2[28] = 4
jreg2[29] = 10
jreg2[30] = 14
jreg2[31] = 29
jreg2[32] = 50
jreg2[33] = 57
jreg2[34] = 20
jreg2[35] = 35
jreg2[36] = 48
jreg2[37] = 21
jreg2[38] = 53
jreg2[39] = 39
jreg2[40] = 26
jreg2[41] = 40
jreg2[42] = 58

nreg2=np.zeros((43,1))
nreg2[0] = -1.7731742473213E-03
nreg2[1] = -0.017834862292358
nreg2[2] = -0.045996013696365
nreg2[3] = -0.057581259083432
nreg2[4] = -0.05032527872793
nreg2[5] = -3.3032641670203E-05
nreg2[6] = -1.8948987516315E-04
nreg2[7] = -3.9392777243355E-03
nreg2[8] = -0.043797295650573
nreg2[9] = -2.6674547914087E-05
nreg2[10] = 2.0481737692309E-08
nreg2[11] = 4.3870667284435E-07
nreg2[12] = -3.227767723857E-05
nreg2[13] = -1.5033924542148E-03
nreg2[14] = -0.040668253562649
nreg2[15] = -7.8847309559367E-10
nreg2[16] = 1.2790717852285E-08
nreg2[17] = 4.8225372718507E-07
nreg2[18] = 2.2922076337661E-06
nreg2[19] = -1.6714766451061E-11
nreg2[20] = -2.1171472321355E-03
nreg2[21] = -23.895741934104
nreg2[22] = -5.905956432427E-18
nreg2[23] = -1.2621808899101E-06
nreg2[24] = -0.038946842435739
nreg2[25] = 1.1256211360459E-11
nreg2[26] = -8.2311340897998
nreg2[27] = 1.9809712802088E-08
nreg2[28] = 1.0406965210174E-19
nreg2[29] = -1.0234747095929E-13
nreg2[30] = -1.0018179379511E-09
nreg2[31] = -8.0882908646985E-11
nreg2[32] = 0.10693031879409
nreg2[33] = -0.33662250574171
nreg2[34] = 8.9185845355421E-25
nreg2[35] = 3.0629316876232E-13
nreg2[36] = -4.2002467698208E-06
nreg2[37] = -5.9056029685639E-26
nreg2[38] = 3.7826947613457E-06
nreg2[39] = -1.2768608934681E-15
nreg2[40] = 7.3087610595061E-29
nreg2[41] = 5.5414715350778E-17
nreg2[42] = -9.436970724121E-07

# AddIn InitFieldsreg3[]
ireg3=np.zeros((40,1))
ireg3[0] = 0
ireg3[1] = 0
ireg3[2] = 0
ireg3[3] = 0
ireg3[4] = 0
ireg3[5] = 0
ireg3[6] = 0
ireg3[7] = 0
ireg3[8] = 1
ireg3[9] = 1
ireg3[10] = 1
ireg3[11] = 1
ireg3[12] = 2
ireg3[13] = 2
ireg3[14] = 2
ireg3[15] = 2
ireg3[16] = 2
ireg3[17] = 2
ireg3[18] = 3
ireg3[19] = 3
ireg3[20] = 3
ireg3[21] = 3
ireg3[22] = 3
ireg3[23] = 4
ireg3[24] = 4
ireg3[25] = 4
ireg3[26] = 4
ireg3[27] = 5
ireg3[28] = 5
ireg3[29] = 5
ireg3[30] = 6
ireg3[31] = 6
ireg3[32] = 6
ireg3[33] = 7
ireg3[34] = 8
ireg3[35] = 9
ireg3[36] = 9
ireg3[37] = 10
ireg3[38] = 10
ireg3[39] = 11

jreg3=np.zeros((40,1))
jreg3[0] = 0
jreg3[1] = 0
jreg3[2] = 1
jreg3[3] = 2
jreg3[4] = 7
jreg3[5] = 10
jreg3[6] = 12
jreg3[7] = 23
jreg3[8] = 2
jreg3[9] = 6
jreg3[10] = 15
jreg3[11] = 17
jreg3[12] = 0
jreg3[13] = 2
jreg3[14] = 6
jreg3[15] = 7
jreg3[16] = 22
jreg3[17] = 26
jreg3[18] = 0
jreg3[19] = 2
jreg3[20] = 4
jreg3[21] = 16
jreg3[22] = 26
jreg3[23] = 0
jreg3[24] = 2
jreg3[25] = 4
jreg3[26] = 26
jreg3[27] = 1
jreg3[28] = 3
jreg3[29] = 26
jreg3[30] = 0
jreg3[31] = 2
jreg3[32] = 26
jreg3[33] = 2
jreg3[34] = 26
jreg3[35] = 2
jreg3[36] = 26
jreg3[37] = 0
jreg3[38] = 1
jreg3[39] = 26

nreg3=np.zeros((40,1))
nreg3[0] = 1.0658070028513
nreg3[1] = -15.732845290239
nreg3[2] = 20.944396974307
nreg3[3] = -7.6867707878716
nreg3[4] = 2.6185947787954
nreg3[5] = -2.808078114862
nreg3[6] = 1.2053369696517
nreg3[7] = -8.4566812812502E-03
nreg3[8] = -1.2654315477714
nreg3[9] = -1.1524407806681
nreg3[10] = 0.88521043984318
nreg3[11] = -0.64207765181607
nreg3[12] = 0.38493460186671
nreg3[13] = -0.85214708824206
nreg3[14] = 4.8972281541877
nreg3[15] = -3.0502617256965
nreg3[16] = 0.039420536879154
nreg3[17] = 0.12558408424308
nreg3[18] = -0.2799932969871
nreg3[19] = 1.389979956946
nreg3[20] = -2.018991502357
nreg3[21] = -8.2147637173963E-03
nreg3[22] = -0.47596035734923
nreg3[23] = 0.0439840744735
nreg3[24] = -0.44476435428739
nreg3[25] = 0.90572070719733
nreg3[26] = 0.70522450087967
nreg3[27] = 0.10770512626332
nreg3[28] = -0.32913623258954
nreg3[29] = -0.50871062041158
nreg3[30] = -0.022175400873096
nreg3[31] = 0.094260751665092
nreg3[32] = 0.16436278447961
nreg3[33] = -0.013503372241348
nreg3[34] = -0.014834345352472
nreg3[35] = 5.7922953628084E-04
nreg3[36] = 3.2308904703711E-03
nreg3[37] = 8.0964802996215E-05
nreg3[38] = -1.6557679795037E-04
nreg3[39] = -4.4923899061815E-05

# AddIn InitFieldsreg4(]
nreg4=np.zeros((10,1))
nreg4[0] = 1167.0521452767
nreg4[1] = -724213.16703206
nreg4[2] = -17.073846940092
nreg4[3] = 12020.82470247
nreg4[4] = -3232555.0322333
nreg4[5] = 14.91510861353
nreg4[6] = -4823.2657361591
nreg4[7] = 405113.40542057
nreg4[8] = -0.23855557567849
nreg4[9] = 650.17534844798
    
#AddIn Sub InitFieldsbound(]
nbound=np.zeros((5,1))
nbound[0] = 348.05185628969
nbound[1] = -1.1671859879975
nbound[2] = 1.0192970039326E-03
nbound[3] = 572.54459862746
nbound[4] = 13.91883977887

# AddIn Sub InitFieldsvisc(]
n0visc=np.zeros((4,1))
n0visc[0] = 1 
n0visc[1] = 0.978197
n0visc[2] = 0.579829
n0visc[3] = -0.202354

ivisc=np.zeros((19,1))
ivisc[0] = 0
ivisc[1] = 0
ivisc[2] = 0
ivisc[3] = 0
ivisc[4] = 1
ivisc[5] = 1
ivisc[6] = 1
ivisc[7] = 1
ivisc[8] = 2
ivisc[9] = 2
ivisc[10] = 2
ivisc[11] = 3
ivisc[12] = 3
ivisc[13] = 3
ivisc[14] = 3
ivisc[15] = 4
ivisc[16] = 4
ivisc[17] = 5
ivisc[18] = 6

jvisc=np.zeros((19,1))
jvisc[0] = 0
jvisc[1] = 1
jvisc[2] = 4
jvisc[3] = 5
jvisc[4] = 0
jvisc[5] = 1
jvisc[6] = 2
jvisc[7] = 3
jvisc[8] = 0
jvisc[9] = 1
jvisc[10] = 2
jvisc[11] = 0
jvisc[12] = 1
jvisc[13] = 2
jvisc[14] = 3
jvisc[15] = 0
jvisc[16] = 3
jvisc[17] = 1
jvisc[18] = 3

nvisc=np.zeros((19,1))
nvisc[0] = 0.5132047
nvisc[1] = 0.3205656
nvisc[2] = -0.7782567
nvisc[3] = 0.1885447
nvisc[4] = 0.2151778
nvisc[5] = 0.7317883
nvisc[6] = 1.241044
nvisc[7] = 1.476783
nvisc[8] = -0.2818107
nvisc[9] = -1.070786
nvisc[10] = -1.263184
nvisc[11] = 0.1778064
nvisc[12] = 0.460504
nvisc[13] = 0.2340379
nvisc[14] = -0.4924179
nvisc[15] = -0.0417661
nvisc[16] = 0.1600435
nvisc[17] = -0.01578386
nvisc[18] = -0.003629481

# AddIn Sub InitFieldsthcon[]
n0thcon=np.zeros((4,1))
n0thcon[0] = 1
n0thcon[1] = 6.978267
n0thcon[2] = 2.599096
n0thcon[3] = -0.998254

nthcon=np.zeros((5,6))
nthcon[0, 0] = 1.3293046
nthcon[0, 1] = -0.40452437
nthcon[0, 2] = 0.2440949
nthcon[0, 3] = 0.018660751
nthcon[0, 4] = -0.12961068
nthcon[0, 5] = 0.044809953
nthcon[1, 0] = 1.7018363
nthcon[1, 1] = -2.2156845
nthcon[1, 2] = 1.6511057
nthcon[1, 3] = -0.76736002
nthcon[1, 4] = 0.37283344
nthcon[1, 5] = -0.1120316
nthcon[2, 0] = 5.2246158
nthcon[2, 1] = -10.124111
nthcon[2, 2] = 4.9874687
nthcon[2, 3] = -0.27297694
nthcon[2, 4] = -0.43083393
nthcon[2, 5] = 0.13333849
nthcon[3, 0] = 8.7127675
nthcon[3, 1] = -9.5000611
nthcon[3, 2] = 4.3786606
nthcon[3, 3] = -0.91783782
nthcon[3, 4] = 0 
nthcon[3, 5] = 0 
nthcon[4, 0] = -1.8525999
nthcon[4, 1] = 0.9340469
nthcon[4, 2] = 0 
nthcon[4, 3] = 0 
nthcon[4, 4] = 0 
nthcon[4, 5] = 0 

#Copyright 2017 Martin Mittermaier
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    [at your option] any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Dieses Programm ist Freie Software: Sie können es unter den Bedingungen
#    der GNU General Public License, wie von der Free Software Foundation,
#    Version 3 der Lizenz oder [nach Ihrer Wahl] jeder neueren
#    veröffentlichten Version, weiterverbreiten und/oder modifizieren.
#
#    Dieses Programm wird in der Hoffnung, dass es nützlich sein wird, aber
#    OHNE JEDE GEWÄHRLEISTUNG, bereitgestellt sogar ohne die implizite
#    Gewährleistung der MARKTFÄHIGKEIT oder EIGNUNG FÜR EINEN BESTIMMTEN ZWECK.
#    Siehe die GNU General Public License für weitere Details.
#
#    Sie sollten eine Kopie der GNU General Public License zusammen mit diesem
#    Programm erhalten haben. Wenn nicht, siehe <http://www.gnu.org/licenses/>.