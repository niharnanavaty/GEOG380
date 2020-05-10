# Justin Jones
# Nihar Nanavaty
# 5/10/2020
# Import arcpy module
import arcpy

# This could be changed to false if the code was added so that the user could give routes unique names
# to save every time after running
arcpy.env.overwriteOutput = True

# The workspace should be changed to wherever the user is storing the geodatabase.
arcpy.env.workspace = "C:/Users/Documents/GTKArcGIS/380FinProject/FinalProject.gdb"

# This function allows the user to input a list of locations and hit DONE when they are finished.
# Order is not important
def InputLocations():
    print('Input locations as exact matches. Hit Return After Each. When you are finished enter "DONE" and hit return.')
    KeepGoing = True
    LocationList = []
    while(KeepGoing == True):
        in_txt = raw_input()
        if(in_txt == "DONE"):
            return(LocationList)
        else:
            LocationList.append(in_txt)
    return(LocationList)

# This function lets the user query the list of locations by start letter.
def SearchBasedOnLetter():
    print("Please input a letter to print locations beginning with that letter.")
    in_txt = raw_input()
    fc = 'C:/Users/Documents/GTKArcGIS/380FinProject/FinalProject.gdb/DCLandMarks'
    fields = ['NAME']
    SearchLetter = in_txt
    with arcpy.da.SearchCursor(fc, fields) as cursor:
        for row in cursor:
            if(row[0][0] == SearchLetter):
                print(row[0])

print("Welcome to the routing program. We are here to help to optmize your trip. If you would like to see a list of locations press Y. If not press N.")
in_txt = raw_input()

if (in_txt == 'Y'):
    KeepLooking = True
    while(KeepLooking == True):
        SearchBasedOnLetter()
        print("Would you like to search through another letter? Y or N.")
        in_txt = raw_input()
        if(in_txt == "N"):
            KeepLooking = False

# This is the array of final chosen locations from the user
FinalList = []

if (in_txt == 'N'):
    print('Please begin entering locations.')
    FinalList = InputLocations()
        
# Local variables:
# Most of these variables would be created on thier own, but having them here helps to reduce issues.
RoadNetwork_ND = "RoadNetwork_ND"
RoadNetwork_ND_Routing = "RoadNetwork_ND_Routing"
RoadNetwork_ND_Routing_w_Locations = RoadNetwork_ND_Routing
DCLandMarksAll = "DCLandMarks"
arcpy.MakeFeatureLayer_management(DCLandMarksAll, "DCLandMarksAll_lyr")


DCLandMarksPoint = "DCLandMarksAsPoint"
Final_Route = RoadNetwork_ND_Routing_w_Locations
Solve_Succeeded = "true"

# If the user wants to call thier final output something else or store it not in the geodatabase they can change the path here.
Routes = Final_Route
Routes_Layer = "Routes_Layer"
RouteForDisplay = "C:/Users/Documents/GTKArcGIS/380FinProject/FinalProject.gdb/RouteForDisplay"

# Process: Make Route Layer
arcpy.MakeRouteLayer_na(RoadNetwork_ND, "RoadNetwork_ND_Routing", "Length", "FIND_BEST_ORDER", "PRESERVE_BOTH", "NO_TIMEWINDOWS", "", "ALLOW_UTURNS", "", "NO_HIERARCHY", "", "TRUE_LINES_WITH_MEASURES", "")

# Process: Select Layer By Attribute
# In this step we have to use conditional formatting in order for the SQL query to work properly.
# The commands join the array with the correct format.
placeholders= "', '".join(FinalList)
Expression = "NAME IN ('%s')" % placeholders
arcpy.SelectLayerByAttribute_management("DCLandMarksAll_lyr", "NEW_SELECTION", Expression)

# Process: Feature To Point
# Network analyst only works with points not polygons!
arcpy.FeatureToPoint_management("DCLandMarksAll_lyr", DCLandMarksPoint, "CENTROID")
        
# Process: Add Locations
arcpy.AddLocations_na(RoadNetwork_ND_Routing, "Stops", DCLandMarksPoint, "Name Name #", "5000 Meters", "", "DCRoads2 SHAPE;RoadNetwork_ND_Junctions SHAPE", "MATCH_TO_CLOSEST", "APPEND", "NO_SNAP", "5 Meters", "INCLUDE", "DCRoads2 #;RoadNetwork_ND_Junctions #")

# Process: Solve
# Network analyst is an extension, the best practice is to check it in and out.
arcpy.CheckOutExtension("Network")
arcpy.Solve_na(RoadNetwork_ND_Routing_w_Locations, "SKIP", "TERMINATE", "", "")
arcpy.CheckInExtension("Network")

# Process: Select Data
arcpy.SelectData_management(Final_Route, "Routes")

# Process: Make Feature Layer
# Needed to use the copy features tool
arcpy.MakeFeatureLayer_management("Routes", Routes_Layer)

# Process: Copy Features
# Copies the features into a shapefile for display
arcpy.CopyFeatures_management(Routes_Layer, RouteForDisplay, "", "0", "0", "0")
