from __future__ import division

import numpy as np

import read_and_transform as tms_rt
from tms import tms_geom


def __test_one():
    import os
    import vtk
    from itertools import izip

    test_dir = os.path.join(os.path.dirname(__file__), "data")
    test_file = os.path.join(test_dir, "TMS-441.csv")
    test_file = os.path.join(test_dir, "TMS-758.csv")
    #test_file = os.path.join(test_dir, "TMS-310.csv")

    points = tms_rt.read_csv_file(test_file)
    calibs = tms_rt.extract_calibration_samples(points)
    assert set(calibs.keys()) == {1, 2, 3, 4}
    ref = calibs[3]
    calibs_norm = dict(((k, tms_rt.normalize_point_to_ref(v, ref) ) for k, v in calibs.iteritems() ))

    ren_win = vtk.vtkRenderWindow()
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    iren.SetRenderWindow(ren_win)
    ren = vtk.vtkRenderer()
    ren_win.AddRenderer(ren)

    date = ref.date

    pointer_fun = tms_rt.get_pointer_transform_function(date)
    calib_points = [pointer_fun(p) for p in calibs_norm.itervalues()]

    r,ctr = tms_geom.adjust_sphere(calib_points)

    for p in calib_points:
        __add_sphere_to_ren(p,r/20,ren)

    ac = __add_sphere_to_ren(ctr,r,ren)
    ac.GetProperty().SetColor(1,0,0)
    #fit sphere to calibration

    coil_samples = tms_rt.extract_coil_samples(points)[:50]
    coil_samples_norm = tms_rt.normalize_to_ref(coil_samples, ref)
    coil_function = tms_rt.get_coil_transform_function(date)
    coil_pairs = [coil_function(p) for p in coil_samples_norm]
    cc = (0, 1, 0)
    cc2 = (0.2,0.7,0.2)
    for (c, t),p in izip(coil_pairs,coil_samples_norm):
        ac = __add_sphere_to_ren(c, 0.002, ren)
        ac.GetProperty().SetColor(cc)
        ac = __add_line_to_ren(c, np.subtract(t, c), ren)
        ac.GetProperty().SetColor(cc)

    #draw intersection with sphere
    intersects = [tms_geom.intersect_point_with_sphere(c,np.subtract(t,c),r,ctr) for c,t in coil_pairs]
    for p in intersects:
        ac = __add_sphere_to_ren(p, 0.001, ren)
        ac.GetProperty().SetColor(cc2)
        ac.GetProperty().SetOpacity(0.5)

    #find plane
    vec,  circle_radius = tms_geom.circle_from_points_in_sphere(intersects,r,ctr)
    __add_plane_to_ren(ctr+vec,vec,r,ren)

    iren.Initialize()
    iren.Start()


def __add_sphere_to_ren(ctr, radius, ren):
    import vtk

    p = ctr
    r = radius
    source = vtk.vtkSphereSource()
    source.SetCenter(*p)
    source.SetRadius(r)
    source.SetPhiResolution(40)
    source.SetThetaResolution(40)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(source.GetOutputPort())
    ac = vtk.vtkActor()
    ac.SetMapper(mapper)
    ren.AddActor(ac)
    return ac


def __add_plane_to_ren(center, normal, length, ren):
    import vtk

    center = np.array(center)
    source = vtk.vtkPlaneSource()
    source.SetOrigin(0, 0, 0)
    source.SetPoint1(length, 0, 0)
    source.SetPoint2(0, length, 0)
    source.SetCenter(*center)
    source.SetNormal(*normal)
    source.Update()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(source.GetOutputPort())
    ac = vtk.vtkActor()
    ac.SetMapper(mapper)
    ren.AddActor(ac)
    return ac


def __add_line_to_ren(origin, vec, ren):
    import vtk

    p1 = origin
    p2 = np.array(origin) + np.array(vec)
    source = vtk.vtkLineSource()
    source.SetPoint1(p1)
    source.SetPoint2(p2)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(source.GetOutputPort())
    ac = vtk.vtkActor()
    ac.SetMapper(mapper)
    ren.AddActor(ac)
    return ac

if __name__ == "__main__":
    __test_one()

__author__ = 'Diego'
