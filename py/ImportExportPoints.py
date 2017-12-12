# Import the coordinates of point from a text file.
"""Import the coordinates of point from a text file.
  Inputs:
    filename: The filename. (sring)
  Outputs:
    points: The list of points. (list of point)
"""
import rhinoscriptsyntax as rs 

def ImportPoints(filename):
    if not filename: return
    
    #read each line from the file
    file = open(filename, "r")
    contents = file.readlines()
    file.close()

    # local helper function    
    def __point_from_string(text):
        items = text.strip("()\n").split(",")
        x = float(items[0])
        y = float(items[1])
        z = float(items[2])
        return x, y, z

    contents = [__point_from_string(line) for line in contents]
    points=rs.AddPoints(contents)
    return points

def ExportPoints(objectIds,filename):
    if( objectIds==None ): return
    if( filename==None ): return
    """
    Using a 'with' loop to open the file, we do not need to clean
    up or close the file when we are done, Python takes care of it.
    Here, we'll write the points with a line break, otherwise
    all the points will end up on one line.
    """
    with open(filename, "w")as file:
        for id in objectIds:
            #process point clouds
            if( rs.IsPointCloud(id) ):
                points = rs.PointCloudPoints(id)
                for pt in points:
                    # convert the point list to a string, 
                    # add a new line character, and write to the file
                    file.write(str(pt)+ "\n")
            elif( rs.IsPoint(id) ):
                point = rs.PointCoordinates(id)
                file.write(str(point)+ "\n")