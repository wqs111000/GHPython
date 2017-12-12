# Export the coordinates of point to a text file.
"""Export the coordinates of point to a text file.
  Inputs:
    filename: The filename. (sring)
    points: The list of points. (list of point)
  Outputs:
"""
import rhinoscriptsyntax as rs

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

if( __name__ == '__main__' ):
    path='H:\\3rd year\\mesh generation based on rhino and grasshopper\\python\\py\\ghpython-const\\'
    filename=path+str(filename)+'.txt'
    print filename
    ExportPoints(points,filename)