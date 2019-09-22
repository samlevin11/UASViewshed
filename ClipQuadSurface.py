# Clip study area quad surface from full UTD surface raster.
# Revised 16 April 2018

import arcpy
arcpy.CheckOutExtension('Spatial')
arcpy.CheckExtension('3D')


# Clip full study UTD study area surface to quad
# Surface raster with all obstructions (entire campus)
surface = "C:\\Users\\sjl170230\\Documents\\UTD_Viewshed_V3\\UTD_Viewshed_SEV1.gdb\\surface_1m_V2"
# Polygon of quad study area
StudyArea = "C:\\Users\\sjl170230\\Documents\\UTD_Viewshed_V3\\UTD_Viewshed_SEV1.gdb\\StudyArea_SE"
# Quad surface raster, clipped to study area
Surface_quad = "C:\\Users\\sjl170230\\Documents\\UTD_Viewshed_V3\\UTD_Viewshed_SEV1.gdb\\Surface_SE"

desc = arcpy.Describe(StudyArea)
extent = desc.extent
extent = [str(extent.XMin), str(extent.YMin), str(extent.XMax), str(extent.YMax)]
extent = ' '.join(extent)
print(type(extent))
print(extent)


arcpy.Clip_management(surface, extent, Surface_quad,
                      StudyArea, "-3.402823e+38", "NONE", "NO_MAINTAIN_EXTENT")
print('Surface clipped to study area.')
print('\n')

#Aggregate 1m surface raster to 2m for computing efficiency
agg2m = arcpy.sa.Aggregate(Surface_quad,2,'MAXIMUM')
agg2m.save("C:\\Users\\sjl170230\\Documents\\UTD_Viewshed_V3\\UTD_Viewshed_SEV1.gdb\\Surface_SE_2m")
#Surface_quad_2m = "C:\\Users\\sjl170230\\Documents\\UTD_Viewshed_V3\\UTD_Viewshed_SWV1.gdb\\Surface_SW_2m"
print('Surface aggregated to 2m resolution.')
