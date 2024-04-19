import arcpy

# Set the workspace and enable overwrite output
arcpy.env.workspace = r"D:\ARC PRO\Qibla\Qibla.gdb"
arcpy.env.overwriteOutput = True

# Get the input feature class from user input
inputFeature = arcpy.GetParameterAsText(0)

# Merge input feature classes into a single feature class named "Merge"
input_feature_classes = [inputFeature, "Mecca"]
arcpy.Merge_management(input_feature_classes, "Merge")

# Create a line feature class from the merged features named "Line"
arcpy.management.PointsToLine("Merge", "Line")

# Calculate the directional mean of the line feature class and store the result in a table named "Lineqibla"
input_feature_class = "Line"
output_table = "Lineqibla"
arcpy.stats.DirectionalMean(input_feature_class, output_table, "DIRECTION")

# Add fields "Direction" and "Position" to the "Lineqibla" table
arcpy.management.AddField(output_table, "Direction", "TEXT")
arcpy.management.AddField(output_table, "Position", "TEXT")

# Calculate values for the "Direction" and "Position" fields based on the "CompassA" field
# Define the expression and code blocks for field calculation
expression = """calculate_direction(!CompassA!)"""
code = """def calculate_direction(CompassField):
    if CompassField <= 180:
        value = 180 - CompassField
    elif CompassField <= 270:
        value = 270 - CompassField
    elif CompassField <= 360:
        value = 360 - CompassField
    else:
        value = CompassField
    return value"""
arcpy.management.CalculateField(output_table, "Direction", expression, "PYTHON3", code)

expression1 = """calculate_position(!CompassA!)"""
code1 = """def calculate_position(CompassField):
    if CompassField <= 180:
        return "SE"
    elif CompassField <= 270:
        return "SW"
    elif CompassField <= 360:
        return "NW"
    else:
        return "NE" """
arcpy.management.CalculateField(output_table, "Position", expression1, "PYTHON3", code1)

# Print a message indicating successful completion of field calculations
print("Field calculation for 'Direction' and 'Position' completed successfully.")

# Retrieve values of "Direction" and "Position" fields from the "Lineqibla" table using search cursors
direction_values = [row[0] for row in arcpy.da.SearchCursor(output_table, "Direction")]
position_values = [row[0] for row in arcpy.da.SearchCursor(output_table, "Position")]

# Add a message to ArcGIS indicating the direction and position values
arcpy.AddMessage("The Direction is {0} Angle {1}".format(direction_values, position_values))

# Access the current ArcGIS project and its map
aprx = arcpy.mp.ArcGISProject("CURRENT")
map = aprx.listMaps()[0]

# Add the "Lineqibla" layer to the map
layer_file = r"D:\ARC PRO\Qibla\Qibla.gdb\Lineqibla"
map.addDataFromPath(layer_file)
