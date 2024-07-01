# This script is used in a tool for splitting the points layer into three layers

import arcpy
import os

# Input parameters
input_points = arcpy.GetParameterAsText(0)  # Input points layer
output_workspace = arcpy.GetParameterAsText(1)  # Output geodatabase where new layers will be saved

# Manually assign types to each group
group1_types = ["east entrance", "north entrance", "northeast entrance", "northwest entrance", "south entrance", "southwest entrance", "southeast entrance", "west entrance", "keyless entry", "exit only"]
group2_types = ["bathroom", "baggage claim", "camera", "crawl space", "elevator", "escalator", "hazmat", "stairs", "fire extinguisher", "AED", "fire alarm", "first aid", "water shutoff", "electrical shutoff", "knox box", "roof access", "gas main", "sprinkler shutoff", "fire department connection", "riser", "natural gas shutoff", "emergency generator", "post indicator valve", "annunciator panel", "attic access", "standpipe connection", "fire pump", "vehicle storage", "concessions", "press box", "bus pickup/dropoff", "parent pickup/dropoff", "SRO office", "loading dock", "main office", "parking", "evac chair", "sprinkler", "smoke detector", "emergency vehicle access"]
group3_types = ["water shutoff", "electrical shutoff", "gas main", "hydrant", "natural gas shutoff", "emergency generator"]

# Dictionary to map group number to descriptive name
group_names = {
    1: "ExteriorEntrances",
    2: "PublicSafetyPoints",
    3: "SitePoints"
}

try:
    # Check if the output workspace (geodatabase) exists, create if not
    if not arcpy.Exists(output_workspace):
        arcpy.CreateFileGDB_management(os.path.dirname(output_workspace), os.path.basename(output_workspace))

    # Function to create feature classes for a group of types
    def create_feature_class_for_group(group_types, group_number):
        if group_types:
            type_expression = "Type IN (" + ", ".join([f"'{t}'" for t in group_types]) + ")"
            output_fc_name = f"{group_names[group_number]}"
            output_fc = os.path.join(output_workspace, output_fc_name)

            # Create the feature class
            arcpy.CreateFeatureclass_management(output_workspace, output_fc_name, "POINT", input_points)

            # Select points and append to the feature class
            arcpy.Select_analysis(input_points, output_fc, type_expression)

            return output_fc

        else:
            arcpy.AddWarning(f"No types assigned to {group_names[group_number]}. No output created.")

    # Create feature classes for each group
    fc_group1 = create_feature_class_for_group(group1_types, 1)
    fc_group2 = create_feature_class_for_group(group2_types, 2)
    fc_group3 = create_feature_class_for_group(group3_types, 3)

    # Add the layers to the ArcGIS Pro project
    aprx = arcpy.mp.ArcGISProject("CURRENT")
    map = aprx.listMaps()[0]
    map.addDataFromPath(fc_group1)
    map.addDataFromPath(fc_group2)
    map.addDataFromPath(fc_group3)

    arcpy.AddMessage("Layers added to the map.")

except arcpy.ExecuteError:
    arcpy.AddError(arcpy.GetMessages(2))
except Exception as e:
    arcpy.AddError(str(e))

finally:
    arcpy.ResetEnvironments()  # Reset any arcpy environment settings to their default state
