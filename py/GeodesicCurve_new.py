import rhinoscriptsyntax as rs


def PolylineLength(arrVertices):
    PolylineLength = 0.0
    for i in range(0, len(arrVertices) - 1):
        PolylineLength = PolylineLength + rs.Distance(arrVertices[i], arrVertices[i + 1])
    # print PolylineLength
    return PolylineLength


def SubDividePolyline(arrV):
    print 'SubDividePolyline'
    print len(arrV)
    arrSubD = []
    for i in range(0, len(arrV) - 1):
        # copy the original vertex location'''
        arrSubD.append(arrV[i])
        # 'compute the average of the current vertex and the next one'''
        arrSubD.append([(arrV[i][0] + arrV[i + 1][0]) / 2.0, (arrV[i][1] + arrV[i + 1][1]) / 2.0,
                        (arrV[i][2] + arrV[i + 1][2]) / 2.0])
    # 'copy the last vertex (this is skipped by the loop)
    arrSubD.append(arrV[len(arrV) - 1])
    print len(arrSubD)
    return arrSubD


def GetR2PathOnSurface(surface_id, segments, prompt1, prompt2):
    start_point = rs.GetPointOnSurface(surface_id, prompt1)
    if not start_point: return

    end_point = rs.GetPointOnSurface(surface_id, prompt2)
    if not end_point: return

    if rs.Distance(start_point, end_point) == 0.0: return

    uva = rs.SurfaceClosestPoint(surface_id, start_point)
    uvb = rs.SurfaceClosestPoint(surface_id, end_point)

    path = []
    for i in range(segments + 1):
        t = i / segments
        u = uva[0] + t * (uvb[0] - uva[0])
        v = uva[1] + t * (uvb[1] - uva[1])
        pt = rs.EvaluateSurface(surface_id, u, v)
        path.append(pt)
    return path


def ProjectPolyline(vertices, surface_id):
    polyline = []
    for vertex in vertices:
        pt = rs.BrepClosestPoint(surface_id, vertex)
        if pt: polyline.append(pt[0])
    return polyline


def SmoothPolyline(vertices):
    smooth = []
    smooth.append(vertices[0])

    for i in range(1, len(vertices) - 1):
        prev = vertices[i - 1]
        this = vertices[i]
        next = vertices[i + 1]
        pt = [(prev[0] + this[0] + next[0]) / 3.0, (prev[1] + this[1] + next[1]) / 3.0,
              (prev[2] + this[2] + next[2]) / 3.0]
        smooth.append(pt)
    smooth.append(vertices[-1])
    return smooth


def GeodesicFit(vertices, surface_id, tolerance):
    length = PolylineLength(vertices)
    while True:
        vertices = SmoothPolyline(vertices)
        # print ('GeodesicFit')
        # print (len(vertices))
        vertices = ProjectPolyline(vertices, surface_id)
        # print ('ProjectPolyline')
        # print (len(vertices))
        newlength = PolylineLength(vertices)
        # print newlength
        if abs(newlength - length) < tolerance: return vertices
        length = newlength


def GeodesicCurve(surface_id,vertices):

    tolerance = rs.UnitAbsoluteTolerance() / 10
    length = 1e300

    while True:
        print("Solving geodesic fit for %d samples" % len(vertices))
        vertices = GeodesicFit(vertices, surface_id, tolerance)

        newlength = PolylineLength(vertices)
        if abs(newlength - length) < tolerance: break
        if len(vertices) > 1000: break
        vertices = SubDividePolyline(vertices)
        length = newlength

    geodesicPolyline = rs.AddPolyline(vertices)
    print "Geodesic curve added with length: ", newlength
    return geodesicPolyline

'''
def GeodesicCurve():
    surface_id = rs.GetObject("Select surface for geodesic curve solution", 8, True, True)
    if not surface_id: return

    vertices = GetR2PathOnSurface(surface_id, 10, "Start of geodes curve", "End of geodes curve")
    if not vertices: return
    GeodesicCurve(surface_id,vertices)
'''

if __name__ == "__main__":
    geodesicCurve=GeodesicCurve(surface,points)