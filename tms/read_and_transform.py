"""
Utilities for reading a csv files, and for transforming the points according to a calibration
"""
from __future__ import division
import datetime

import numpy as np

import tms_utils as tms
import calibration_data
import calibration_commands
from tms_utils import PointWithRef
from tms.quat import Quaternion


__author__ = 'Diego'
# labels 1: Vertex, 2:Right temple, 3:Left temple, 4: Nasion
CALIBRATION_LABELS = {"nasion" : 4, "vertex" : 1, "right" : 2, "left" : 3}
nombre_archivo = ''

def read_csv_file(file_path):
    """
    Reads a csv file
    :param file_path: path to the csv file
    :return: A list of points with ref
    """
    with open(file_path) as input_file:
        points = [tms.PointWithRef(l.split(";")) for l in input_file]
    return points


def normalize_to_ref(points, ref):
    """
    All the points will be normalized such that their reference matches the reference of ref
    :param points: raw data
    :param ref: point to be used as a reference
    :return: normalized points
    """
    out_points = [normalize_point_to_ref(p, ref) for p in points]
    print 'Puntos normalizados a la referencia'
    print out_points
    return out_points


def normalize_point_to_ref(point, ref):
    out_point = point.copy()

    ref_pos = np.array(ref.ref_pos)
    ref_or = np.array(ref.ref_or)

    point_uni_pos = np.array(point.ref_pos)
    point_uni_or = np.array(point.ref_or)
    point_pos = np.array(point.point_pos)
    point_or = np.array(point.point_or)

    # v1 is the vector between the unicorn and the position
    v1 = point_pos - point_uni_pos

    # normalize position
    pos_delta = ref_pos - point_uni_pos

    # normalize orientation
    ref_q = Quaternion(ref_or)
    point_uni_q = Quaternion(point_uni_or)
    point_q = Quaternion(point_or)
    v1_q = Quaternion([0, v1[0], v1[1], v1[2]])

    delta_q = ref_q * point_uni_q.inv()

    #left multiply everything by delta_q
    new_point_uni_q = delta_q * point_uni_q
    new_point_q = delta_q * point_q
    new_v1_q = delta_q * v1_q * delta_q.conj()

    new_v1 = new_v1_q.x[1:]

    #save results
    out_point.ref_pos = tuple(point_uni_pos + pos_delta)
    out_point.point_pos = tuple(out_point.ref_pos + new_v1)

    out_point.ref_or = new_point_uni_q.x
    out_point.point_or = new_point_q.x

    return out_point


def extract_calibration_samples(points):
    """
    Extracts the positions of the nasion,vertex,and temples from a list of points
    If the measures are repeated, the last one of each kind is taken
    :param points:
    :return:
    """
    calibs = {}
    for p in points:
        t = p.type
        if t == 0:
            break
        calibs[t] = p
    return calibs


def extract_coil_samples(points):
    out = [p for p in points if p.type == 0]
    return out


def get_pointer_transform_function(date):
    """
    Returns the appropriate function to transform samples to pointed_points based on the date
    :param date: Date of capture
    :return: A function that maps points with_ref to points in space, the reference is ignored
    """
    best_date = find_best_date(date)
    point_f = calibration_commands.get_pointer_point_function(best_date)

    def point_f2(point):
        assert point.type != 0
        point_prime = calibration_commands.transform_sample_no_ref(point)
        return point_f(point_prime.pos,point_prime.orn)

    return point_f2


def get_coil_transform_function(date):
    """
    Returns the appropriate function to trasform samples into coil position and direction. Ref is ignored
    :param date: Date of capture
    :return: A function transforms points_with ref to a point and an unit vector indicating the direction the coil
    """
    print 'Get coil transform function'
    best_date = find_best_date(date)
    vc = calibration_data.CALIB_RESULTS[best_date].Coil_vc
    vt = calibration_data.CALIB_RESULTS[best_date].Coil_vt
    ctr_fun = calibration_commands.get_point_function(vc)
    top_fun = calibration_commands.get_point_function(vt)

    def transform_coil(coil_point):
        print 'Find center and top coil point'
        assert coil_point.type == 0
        pos, orn = calibration_commands.transform_sample_no_ref(coil_point)
        ctr = ctr_fun(pos, orn)
        top = top_fun(pos, orn)

        #cambiar valores de ctr y top

        print 'centros %s'%ctr
        print 'top %s'%top

        #Cambiar centros y top

        temp = np.array([[1.8604, 0, 0, 0],[0, 1.8646, 0, 0],[0, 0, 1.7924, 0],[0, 0, 0, 0.0010]]);
        scaling_Matrix = temp*1000;
        #print 'escalar %s'%scaling_Matrix

        temp2=np.array([[0.000069290850432, 0.000014065274787, -0.000997497341396, -1.602921071482849],[-0.000087906973422, 0.000996097050862, 0.000007939098642, -1.949566260937091],
                               [0.000993715825611, 0.000087136865382, 0.000070256847504, -1.294088648339655],[0, 0, 0, 0.001]])
        rigid_Matrix=temp2*1000;
        #print 'rotacion %s'%rigid_Matrix

        aja=np.array([0.80286295, 1.3191538, -0.8674157, 1])
        aja2=np.dot(scaling_Matrix, aja)
        aja3=np.dot(rigid_Matrix, aja2)
        print 'estos son %s'%aja3

        ctr2= np.insert(ctr, 3, 1)

        new_Scaled = np.dot(scaling_Matrix, ctr2)
        new_Point = np.dot(rigid_Matrix, new_Scaled)
        new_Point = np.delete(new_Point, 3, 0)
        #print 'New point ctr %s'%new_Point

        top2= np.insert(top, 3, 1)

        new_Scaled_top = np.dot(scaling_Matrix, top2)
        new_Point_top = np.dot(rigid_Matrix, new_Scaled_top)
        new_Point_top = np.delete(new_Point_top, 3, 0)
        #print 'New point top %s'%new_Point_top

        #ctr = new_Point
        #top = new_Point_top

        return ctr, top

    return transform_coil


def find_best_date(date):
    print 'Find best date'
    possible_dates = calibration_data.INCIDENT_DATES
    for d in reversed(possible_dates):
        dt = datetime.datetime(d.year, d.month, d.day)
        if date >= dt:
            calibration_date = calibration_data.INCIDENT2CALIB[d]
            return calibration_date


def rotate_vector(v, q):
    if not isinstance(q, Quaternion):
        q = Quaternion(q)
    v_q = Quaternion([0, v[0], v[1], v[2]])
    v_2_q = q * v_q * q.conj()
    v2 = v_2_q.x[1:]
    return v2


def __test_calib_samples():
    import os
    import vtk

    test_dir = os.path.join(os.path.dirname(__file__), "data")
    test_file = os.path.join(test_dir, "TMS-758.csv")

    points = read_csv_file(test_file)
    for i in xrange(0, 10):
        print points[i]
    calibs = extract_calibration_samples(points)
    assert set(calibs.keys()) == {1, 2, 3, 4}
    ref = calibs[1]
    calibs_norm = dict(((k, normalize_point_to_ref(v, ref) ) for k, v in calibs.iteritems() ))
    colors = {1: (1, 1, 1), 2: (1, 0, 0), 3: (0, 0, 1), 4: (1, 1, 0)}
    # labels 1: Vertex, 2:Right temple, 3:Left temple, 4: Nasion

    ren_win = vtk.vtkRenderWindow()
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    iren.SetRenderWindow(ren_win)
    ren = vtk.vtkRenderer()
    ren_win.AddRenderer(ren)

    for k in xrange(1, 5):
        __draw_point_and_uni(calibs[k], colors[k], ren)
        __draw_point_and_uni(calibs_norm[k], colors[k], ren)

    iren.Initialize()
    iren.Start()

    print find_best_date(ref.date)

    __draw_calibration_net(calibs_norm, ren)

    iren.Start()


def __test_normalize():
    import vtk

    ref_point = PointWithRef()
    point2 = PointWithRef()
    for p in (ref_point, point2):
        p.point_pos = np.random.random(3) * 15 / 100
        p.ref_pos = np.random.random(3) * 15 / 100
        p.point_or = tuple(Quaternion.from_v_theta(np.random.random(3), np.random.random()).x)
        p.ref_or = tuple(Quaternion.from_v_theta(np.random.random(3), np.random.random()).x)

    ren_win = vtk.vtkRenderWindow()
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    iren.SetRenderWindow(ren_win)
    ren = vtk.vtkRenderer()
    ren_win.AddRenderer(ren)

    # draw ref
    __draw_point_and_uni(ref_point, (1, 1, 1), ren)

    # draw original point
    __draw_point_and_uni(point2, (0, 1, 0), ren)

    #normalize
    point2_n = normalize_point_to_ref(point2, ref_point)
    __draw_point_and_uni(point2_n, (1, 0, 0), ren)

    iren.Initialize()
    iren.Start()


def __draw_calibration_net(calib_points, ren):
    colors = {1: (1, 1, 1), 2: (1, 0, 0), 3: (0, 0, 1), 4: (1, 1, 0)}
    # labels 1: Vertex, 2:Right temple, 3:Left temple, 4: Nasion

    pointer_fun = get_pointer_transform_function(calib_points[1].date)
    c_points = {}
    for k, v in calib_points.iteritems():
        c_points[k] = pointer_fun(v)
        __draw_sphere(c_points[k], 0.01, colors[k], ren)
        __add_line_to_ren(c_points[k],np.subtract(v.point_pos,c_points[k]),colors[k],ren)
    for k in xrange(2, 5):
        __add_line_to_ren(c_points[1], np.subtract(c_points[k], c_points[1]), colors[1], ren)
    __add_line_to_ren(c_points[2], np.subtract(c_points[3], c_points[2]), colors[1], ren)
    __add_line_to_ren(c_points[2], np.subtract(c_points[4], c_points[2]), colors[1], ren)
    __add_line_to_ren(c_points[3], np.subtract(c_points[4], c_points[3]), colors[1], ren)



def __test_coil():
    import os
    import vtk
    from itertools import izip

    print 'Test coil'

    test_dir = os.path.join(os.path.dirname(__file__), "data")
    test_file = os.path.join(test_dir, "TMS-441.csv")
    test_file = os.path.join(test_dir, "TMS-758.csv")
    #test_file = os.path.join(test_dir, "TMS-310.csv")

    points = read_csv_file(test_file)
    calibs = extract_calibration_samples(points)
    assert set(calibs.keys()) == {1, 2, 3, 4}
    ref = calibs[3]
    calibs_norm = dict(((k, normalize_point_to_ref(v, ref) ) for k, v in calibs.iteritems() ))

    ren_win = vtk.vtkRenderWindow()
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    iren.SetRenderWindow(ren_win)
    ren = vtk.vtkRenderer()
    ren_win.AddRenderer(ren)

    date = ref.date

    #__draw_calibration_net(calibs,ren)
    __draw_calibration_net(calibs_norm, ren)

    coil_samples = extract_coil_samples(points) # [:5]
    coil_samples_norm = normalize_to_ref(coil_samples, ref)
    coil_function = get_coil_transform_function(date)
    #coil_function = lambda x: (x.point_pos,x.point_pos+np.array([0,0,0.1]))
    #coil_pairs = [coil_function(p) for p in coil_samples]
    coil_pairs = [coil_function(p) for p in coil_samples_norm]
    cc = (0, 1, 0)
    cc2 = (0.2,0.7,0.2)
    for (c, t),p in izip(coil_pairs,coil_samples_norm):
        __draw_sphere(c, 0.01, cc, ren)
        #__draw_point_and_uni(p,cc2,ren)
        __add_line_to_ren(c, np.subtract(t, c), cc, ren)
        #__add_line_to_ren(c, np.subtract(p.point_pos, c), (1,1,1), ren)


    print find_best_date(coil_samples_norm[0].date)
    iren.Initialize()
    iren.Start()


def __draw_point_and_uni(p, color, ren):
    print 'Draw point and uni'
    # draw point
    r1 = .02
    r2 = .01
    unit_vector1 = [0, 0, .3]
    unit_vector2 = [0, 0.15, 0]
    # point
    __draw_sphere(p.point_pos, r1, color, ren)
    dir = rotate_vector(unit_vector1, p.point_or)
    __add_line_to_ren(p.point_pos, dir, color, ren)
    dir2 = rotate_vector(unit_vector2, p.point_or)
    __add_line_to_ren(p.point_pos, dir2, color, ren)
    #ref
    __draw_sphere(p.ref_pos, r2, color, ren)
    dir = rotate_vector(unit_vector1, p.ref_or)
    __add_line_to_ren(p.ref_pos, dir, color, ren)
    dir2 = rotate_vector(unit_vector2, p.ref_or)
    __add_line_to_ren(p.ref_pos, dir2, color, ren)
    #connection
    __add_line_to_ren(p.point_pos, np.subtract(p.ref_pos, p.point_pos), color, ren)


def __draw_sphere(center, radius, color, ren):
    import vtk

    print 'Draw sphere'
    p = center
    r = radius
    source = vtk.vtkSphereSource()
    source.SetCenter(*p)
    source.SetRadius(r)
    source.SetPhiResolution(20)
    source.SetThetaResolution(20)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(source.GetOutputPort())
    ac = vtk.vtkActor()
    ac.SetMapper(mapper)
    ren.AddActor(ac)
    ac.GetProperty().SetColor(color)


def __add_line_to_ren(origin, vec, color, ren):
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
    ac.GetProperty().SetColor(color)

def _set_nombre_archivo(n):
    global nombre_archivo
    nombre_archivo=n

def _get_nombre_archivo():
    return nombre_archivo

if __name__ == "__main__":
    #__test_normalize()
    #__test_calib_samples()
    __test_coil()