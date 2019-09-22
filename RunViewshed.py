# --------------------------------------------------------
# Run Viewshed analysis on each individual flight point
# Revised 28 April 2018
# Written by Samuel Levin
# --------------------------------------------------------

import arcpy
arcpy.CheckOutExtension('Spatial')
arcpy.CheckOutExtension('3D')

# get number of flight point features
flightpts = 'C:\\Users\\sjl170230\\Documents\\UTD_Viewshed_V3\\UTD_Viewshed_SEV1.gdb\\FlightPts_SE'
n = int(arcpy.GetCount_management(flightpts).getOutput(0))
print('Running viewshed analysis on {} flight points...'.format(n))

for p in range(1,n+1):

    # variables:
    surface = "C:\\Users\\sjl170230\\Documents\\UTD_Viewshed_V3\\UTD_Viewshed_SEV1.gdb\\Surface_SE_2m"
    fltpt_ = "C:\\Users\\sjl170230\\Documents\\UTD_Viewshed_V3\\UTD_Viewshed_SEV1.gdb\\fltpt_" + str(p)
    vs_ = "C:\\Users\\sjl170230\\Documents\\UTD_Viewshed_V3\\UTD_Viewshed_SEV1.gdb\\vs_" + str(p)
    Output_above_ground_level_raster = ""
    Output_observer_region_relationship_table = ""

    print('Running viewshed analysis on fltpt_{}'.format(p))
    # Refractivity coeff = 0.13 (default), Surface Offet = 1.63, Outer radius 500 meters(3D distance), -90 to 0 vertical
    arcpy.gp.Viewshed2_sa(surface, fltpt_, vs_, Output_above_ground_level_raster, "FREQUENCY", "0 Meters",
                          Output_observer_region_relationship_table, "0.13", "1.63 Meters", "Altitude", "0 Meters", "",
                          "GROUND", "500 Meters", "3D", "0", "360", "0", "-90", "ALL_SIGHTLINES")
    print('fltpt_{} viewshed complete.'.format(p))

print('\n')
print('All viewshed processes executed.')
