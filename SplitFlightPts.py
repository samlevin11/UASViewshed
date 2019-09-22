# --------------------------------------------------------
# Split all flight points into invididual feature classes by OBJECTID
# Revised 28 April 2018
# Written by Samuel Levin
# --------------------------------------------------------

import arcpy

# set flightpts equal to quadrant flight points feature class
flightpts = 'C:\\Users\\sjl170230\\Documents\\UTD_Viewshed_V3\\UTD_Viewshed_SEV1.gdb\\FlightPts_SE'
# get number of flight point features
n = int(arcpy.GetCount_management(flightpts).getOutput(0))
print('Splitting {} flight points...'.format(n))


# add OID_orig field with original OBJECTID. Uses so that original flight point location can be retained
arcpy.AddField_management(flightpts,'OID_orig', 'SHORT')
arcpy.CalculateField_management(flightpts,'OID_orig','!OBJECTID!','PYTHON')
print('OID_orig field populated.')

# split flightpts into individual feature classes of 1 point each
for i in range(1,n+1):
    out_path = 'C:\\Users\\sjl170230\\Documents\\UTD_Viewshed_V3\\UTD_Viewshed_SEV1.gdb'
    out_name = 'fltpt_' + str(i)
    #where = 'Split = ' + "'{}'".format(str(b[0]))
    where = 'OID_orig = {}'.format(i)
    print('Exporting flight point where {}'.format(where))
    arcpy.FeatureClassToFeatureClass_conversion(flightpts, out_path, out_name, where)
    print('Feature class {} exported'.format(out_name))

print('Process complete. All flight points split.')
