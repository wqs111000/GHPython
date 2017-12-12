"""
import sys
file='H:/3rd year/mesh generation based on rhino and grasshopper/python/py'
sys.path.append(file)
import GetSingularPoint
reload(GetSingularPoint)
sPoints=GetSingularPoint.GetSingularPoint(mesh)
"""

import rhinoscriptsyntax as rs
import clr
clr.AddReference("Plankton")
clr.AddReference("PlanktonGh")
import Plankton as pk
import PlanktonGh as pkg
def GetSingularPoint(mesh):
    """Get the Singular Points of  a  Mesh
Inputs:
    mesh: . (mesh)
Outputs:
    sPoints: the Singular Points of  the  Mesh. (list of point)
"""
    pmesh = pkg.RhinoSupport.ToPlanktonMesh(mesh)
    sPoints = []
    for i, v in enumerate(pmesh.Vertices):
        # print v
        valence = pmesh.Vertices.GetValence(i)
        if valence != 6:
            p = pkg.RhinoSupport.ToPoint3d(v)
            sPoints.append(p)
    return sPoints
