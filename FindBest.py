# --------------------------------------------------------
# Final script for running viewshed best observation analysis
# Revised 28 April 2018
# Written by Samuel Levin
# --------------------------------------------------------

import arcpy
import pandas as pd
import CumulativeVS
import BestObservers


surface = "C:\\Users\\sjl170230\\Documents\\UTD_Viewshed_V3\\UTD_Viewshed_SEV1.gdb\\Surface_SE_2m"
mask = "C:\\Users\\sjl170230\\Documents\\UTD_Viewshed_V3\\UTD_Viewshed_SEV1.gdb\\BldgVegMask_V2_bin"
path = "C:\\Users\\sjl170230\\Documents\\UTD_Viewshed_V3\\UTD_Viewshed_SEV1.gdb\\"

flightpts = 'C:\\Users\\sjl170230\\Documents\\UTD_Viewshed_V3\\UTD_Viewshed_SEV1.gdb\\FlightPts_SE'
n = int(arcpy.GetCount_management(flightpts).getOutput(0))
unseen_fltpts = list(range(1,n+1))

count = 0
best = pd.DataFrame()

passvis = {}

while len(unseen_fltpts) > 0 and count < 10:
    count += 1
    print('\n')
    print('PASS {}'.format(count))
    CumulativeVS.calcVS(unseen_fltpts,mask,count,path)
    best = BestObservers.findbestobs(count,path,best)
    best_x= best.iloc[count-1]['POINT_X']
    best_y= best.iloc[count-1]['POINT_Y']
    passviewed = BestObservers.findvisible(path,unseen_fltpts,best_x,best_y)
    passvis[count] = passviewed
    unseen_fltpts = [us for us in unseen_fltpts if us not in passviewed]
    print('REMAINING UNSEEN: {}'.format(len(unseen_fltpts)))

savebest = "C:\\Users\\sjl170230\\Documents\\UTD_Viewshed_V3\\OutTables\\bestobservers.csv"
best.to_csv(savebest)
print('Best observers CSV exported to: {}'.format(savebest))
print('\n')
print('PROCESS COMPLETE.')
print('BEST OBSERVERS: ')
print(best)
for pv in passvis:
    print(pv)
    print('\n')
