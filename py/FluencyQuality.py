list of point)
    spls: the Singular Points with less degree.    (list of point)
    pk:编号为k的点.    (point)
    bNaked:所有点是否裸露      （list[bool]）
    bSingular:所有点是否奇异   （list[bool]）
    sumAngles：所有点各自的总角度和，list[float]
    angleEqualIndexes0:所有节点的对角差异值（list[float]）
    angleEqualIndexes:理想点的对角的差异值（list[float]）
    angle180Indexes0：所有节点的相对边所成角与180度的差异值（list[float]）
    angle180Indexes：理想点的相对边所成角与180度的差异值（list[float]）
    valences:所有节点的价（度）（list[int]）
    adjustedValences:所有节点调整后的价，实际仅裸露点的价可能被调整（list[int]）
    valenceIndex：衡量网格节点调整价和理想价的差异大小的量
    fluencyIndex：流畅度
"""

import rhinoscriptsyntax as rs
import clr
import math

clr.AddReference("Plankton")
clr.AddReference("PlanktonGh")
import Plankton as pk
import PlanktonGh as pkg

# 基本参数
valences = []  # 原价
adjustedValences = []  # 修正价
sumAngles = []  # 各顶点的总角度和，list
meshPoints = []  # 网格点，list[point3d]
bNaked = []  # 是否裸露
nakedPoints = []  # 裸露点
nakedVertices = []
interiorPoints = []  # 内部点，list[point3d]
interiorVertices = []
sps = []  # 指定点周围的点，list[list]
bSingular = []
regularPoints = []  # 理想点
interiorRegularPoints = []  # 内部理想点
singularPoints = []  # 奇异点list[point3d]
spms = []  # 多价奇异点list[point3d]
spls = []  # 少价奇异点list[point3d]
angleEqualIndexes0 = []  # 点的相对角的差异值,所有点
angleEqualIndexes = []  # 点的相对角的差异值
angle180Indexes0 = []  # 点的相对边所成角与180度的差异值,所有点
angle180Indexes = []  # 点的相对边所成角与180度的差异值
angleIndexes = []  # angleEqualIndexes和angle180Indexes的平方和开根号
R = 0  # 流畅度计算时，表征节点价和理解节差异总大小的值
N = 0  # 流畅度计算时，表征经权值调整后的总点数
pmesh = pkg.RhinoSupport.ToPlanktonMesh(mesh)
meshVertices = rs.MeshVertices(mesh)  # list[point3d]
bNakedPoints = []
bNakedVertices = list(rs.MeshNakedEdgePoints(mesh))  # list[point3d]
if rs.MeshQuadCount(mesh) > rs.MeshTriangleCount(mesh) :
    VOT = 4  # 理想价，6或者4
else:
    VOT = 6
for i, vertex in enumerate(meshVertices):
    if bNakedVertices[i]:
        nakedVertices.append(vertex)
    else:
        interiorVertices.append(vertex)


# 确定裸露点的价需要增加的修正值
def AddNakedValences(angle, VOT):
    if VOT == 6:
        for k in [1, 2, 3, 4, 5]:
            ak = 60 * ((k * (k + 1)) ** 0.5)
            #        print ak
            if angle < ak:
                addV = 6 - k - 1
                break
        else:
            addV = 0
    if VOT == 4:
        for k in [1, 2, 3]:
            ak = 90 * ((k * (k + 1)) ** 0.5)
            #        print ak
            if angle < ak:
                addV = 4 - k - 1
                break
        else:
            addV = 0
    return addV


for i, v in enumerate(pmesh.Vertices):
    v = pmesh.Vertices[i]
    p0 = pkg.RhinoSupport.ToPoint3d(v)
    meshPoints.append(p0)
    sumAngle = 0
    angles = []
    angle180s = []
    sp = []  # 与i点相连的顶点，有序，list[point3d]
    ihe = pmesh.Vertices.GetHalfedges(i)  # 以i点为起点的半边的编号
    for j in ihe:
        ih = pmesh.Halfedges[pmesh.Halfedges[j].NextHalfedge].StartVertex
        pp = pkg.RhinoSupport.ToPoint3d(pmesh.Vertices[ih])
        sp.append(pp)
    valence = pmesh.Vertices.GetValence(i)
    valences.append(valence)
    if p0 in nakedVertices:
        bNakedPoints.append(True)
        nakedPoints.append(p0)
        for j in range(len(sp) - 1):
            angle = rs.Angle2((p0, sp[j]), (p0, sp[j + 1]))
            angles.append(angle[0])
            sumAngle = angle[0] + sumAngle
        angleEqualIndexes0.append(-1)
        adjustedValence = valence + AddNakedValences(sumAngle, VOT)
        angle180Indexes0.append(-2)
    else:
        bNakedPoints.append(False)
        interiorPoints.append(p0)
        adjustedValence = valence
        for j in range(len(sp)):
            if j != (len(sp) - 1):
                angle = rs.Angle2((p0, sp[j]), (p0, sp[j + 1]))
            else:
                angle = rs.Angle2((p0, sp[len(sp) - 1]), (p0, sp[0]))
            angles.append(angle[0])
            sumAngle = angle[0] + sumAngle
        if valence == VOT:
            tmp = 0
            interiorRegularPoints.append(p0)
            for i in range(int(VOT / 2)):
                tmp = tmp + (angles[i] - angles[i + int(VOT / 2)]) ** 2
            angle03Index = math.sqrt(tmp / (VOT / 2))
            angleEqualIndexes0.append(angle03Index)
            angleEqualIndexes.append(angle03Index)
            tmp = 0
            for i in range(int(VOT / 2)):
                angle180 = rs.Angle2((p0, sp[i]), (p0, sp[i + int(len(sp) / 2)]))
                angle180s.append(angle180[0])
                tmp += (angle180[0] - 180) ** 2
            angle180Index = (tmp / len(angle180s)) ** 0.5
            angle180Indexes0.append(angle180Index)
            angle180Indexes.append(angle180Index)
            angleIndex = (angle03Index ** 2 + angle180Index ** 2) ** 0.5
            angleIndexes.append(angleIndex)
        else:
            angleEqualIndexes0.append(-2)
            angle180Indexes0.append(-2)
            pass
    sps.append(sp)
    sumAngles.append(sumAngle)

    if adjustedValence != VOT:
        w = interiorWeight
        if bNakedPoints[i]:
            w = 1 - interiorWeight
        R = R + w * (adjustedValence - VOT) ** 2
        singularPoints.append(p0)
        bSingular.append(False)
    else:
        regularPoints.append(p0)
        bSingular.append(True)
    if adjustedValence > VOT:
        spms.append(p0)
    if adjustedValence < VOT:
        spls.append(p0)
    adjustedValences.append(adjustedValence)
    valenceSumSqu = (adjustedValence - VOT) ** 2
N = interiorWeight * len(interiorPoints) + (1 - interiorWeight) * len(nakedPoints)
valenceIndex = (R / N) ** 0.5
if len(angleIndexes) != 0:
    # print i
    angleIndexes_average = round(sum(angleIndexes) / len(angleIndexes), 3)
else:
    print "the angleIndexes of the %d-th point is zero" % i
fluencyIndex = valenceIndex + 1 / 60 * angleIndexes_average * len(interiorRegularPoints) * interiorWeight / N
print  meshVertices == meshPoints
print  nakedVertices == nakedPoints
print  interiorVertices == interiorPoints
# 根据编号k求点
if not k:
    k = 0
k = int(k)
pk = meshPoints[k]
