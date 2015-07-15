from __future__ import division
import numpy as np
from scipy import optimize

__author__ = 'Diego'


def adjust_sphere(points):
    np_points = np.array(list(points))
    mean_point = np_points.mean(axis=0)

    # initial guess
    ctr = mean_point
    ds = [np.linalg.norm(p - ctr) for p in np_points]
    r = np.mean(ds)
    guess = np.array((ctr[0], ctr[1], ctr[2], r))

    def error_function(guess):
        r = guess[3]
        ctr = guess[:3]
        ds = [(np.linalg.norm(p - ctr) - r)**2 for p in np_points]
        error = sum(ds)
        return error

    ans = optimize.minimize(error_function, guess)
    assert ans.success
    final_guess = ans.x
    r = final_guess[3]
    ctr = final_guess[:3]
    return r, ctr


def intersect_point_with_sphere(point, vector, sphere_r, sphere_ctr,both_sides=True):
    """
    Calculates the intersection of a line defined by a starting point and a direction vector, with a sphere
    :param point: starting point of line
    :param vector: direction vector
    :param sphere_r: radius of sphere
    :param sphere_ctr: center of sphere
    :return: point of intersection between line and sphere, or None if there is no intersection
    """
    ctr = np.array(sphere_ctr)
    pt = np.array(point)
    r = sphere_r
    v = np.array(vector)
    v /= np.linalg.norm(v)

    d = pt - ctr

    a = np.dot(v, v)
    b = 2 * np.dot(d, v)
    c = np.dot(d, d) - r * r

    disc = b ** 2 - 4 * a * c
    if disc < 0:
        return None
    elif disc == 0:
        t = -1 * b / (2 * a)
    else:
        sq_disc = disc ** (0.5)
        t1 = (-1 * b - sq_disc) / (2 * a)
        if t1 > 0:
            t = t1
        else:
            t = (-1 * b + sq_disc) / (2 * a)
    if both_sides or t >= 0:
        intersect = pt + v * t
        return intersect
    else:
        return None


def circle_from_points_in_sphere(points, sphere_r, sphere_ctr):
    """
    Calculates the smallest circle such that all points are located at one side of the circle. The function returns
    the vector from the center of the sphere to the center of the circle. The circle will be in a plane perpendicular to
    this vector.
    :param points: Points in the surface of a sphere
    :param sphere_r: radius of the sphere
    :param sphere_ctr: center of the sphere
    :return: the vector from the center of the sphere to the center of the circle, the radius of the circle
    """
    # center points
    #print 'Circle from points in sphere'
    ctr = sphere_ctr
    pts = np.array([np.subtract(p, ctr) for p in points])

    guess = pts.mean(0)
    guess /= np.linalg.norm(guess)
    distances = [np.dot(guess, p) for p in pts]
    m_dist = min(distances)

    if m_dist < 0:
        raise Exception("All points should be concentrated in the same side of the sphere")
    guess *= m_dist * 0.5
    constraints = []

    def all_up_plane(candidate):
        vs = pts - candidate
        dots = np.dot(vs, candidate)
        return np.min(dots)

    assert all_up_plane(guess) >= 0
    cons = {"type": "ineq", "fun": all_up_plane}
    constraints.append(cons)
    guess_0 = guess.copy()
    constraints.append({"type": "ineq", "fun": lambda x: np.dot(x, guess_0)})
    assert np.dot(guess, guess_0) > 0

    def error_fun(x): return sphere_r ** 2 - np.dot(x, x)

    ans = optimize.minimize(error_fun, guess, constraints=constraints, method="COBYLA")

    #print 'ans %s'%ans
    #assert ans.success

    vec = ans.x
    magnitude = np.linalg.norm(vec)
    circle_radius = np.sqrt(sphere_r ** 2 - magnitude ** 2)
    #print 'vec %s'%vec
    #print 'circle_radius %s'%circle_radius
    return vec, circle_radius

def distance_to_plane(point,plane_point,plane_normal):
    v1 = np.subtract(point,plane_point)
    d = np.abs(np.dot(v1,plane_normal)/np.linalg.norm(plane_normal))
    return d

def __test_adjust_sphere():
    import vtk

    n_points = 4
    points = []
    for i in xrange(n_points):
        p = np.random.random(3) * 100
        points.append(p)
    r, ctr = adjust_sphere(points)
    r2 = r / 10
    ren_win = vtk.vtkRenderWindow()
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    iren.SetRenderWindow(ren_win)
    ren = vtk.vtkRenderer()
    ren_win.AddRenderer(ren)
    # draw points
    for p in points:
        __add_sphere_to_ren(p, r2, ren)
    #draw big sphere
    ac = __add_sphere_to_ren(ctr, r, ren)
    ac.GetProperty().SetColor((1, 0, 0))

    iren.Initialize()
    iren.Start()


def __add_sphere_to_ren(ctr, radius, ren):
    import vtk

    p = ctr
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


def __test_intersect_point_with_sphere():
    import vtk
    from itertools import izip

    ctr = (0, 0, 0)
    r = 10
    points = []
    vectors = []
    n_points = 10
    for i in xrange(n_points):
        v = np.random.random(3)
        v /= np.linalg.norm(v)
        p = ctr - 15 * v
        v2 = np.random.random(3) * 3
        v2 /= np.linalg.norm(v2)
        v2 *= 10  # guarantee that it touches sphere if in right direction
        if np.dot(v, v2) < 0:
            v2 *= -1
        points.append(p)
        vectors.append(v2)

    intersects = [intersect_point_with_sphere(p, v, r, ctr) for p, v in izip(points, vectors)]

    ren_win = vtk.vtkRenderWindow()
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    iren.SetRenderWindow(ren_win)
    ren = vtk.vtkRenderer()
    ren_win.AddRenderer(ren)

    # draw sphere
    ac = __add_sphere_to_ren(ctr, r, ren)
    ac.GetProperty().SetColor((1, 0, 0))
    #draw points
    r2 = 1
    for p in points:
        __add_sphere_to_ren(p, r2, ren)


    #draw vecs
    for p, v in izip(points, vectors):
        __add_line_to_ren(p, v, ren)
    #draw intersection
    for p in intersects:
        if p is not None:
            ac = __add_sphere_to_ren(p, r2, ren)
            ac.GetProperty().SetColor((0, 1, 0))
            ac.GetProperty().SetOpacity(0.5)

    iren.Initialize()
    iren.Start()


def __test_std_in_sphere():
    import vtk
    from itertools import izip

    ctr = (0, 0, 0)
    r = 10
    points = []
    n_points = 50
    for i in xrange(n_points):
        v = np.random.random(3)
        v /= np.linalg.norm(v)
        v *= r
        p = ctr + v
        points.append(p)

    normal, intersect_r = circle_from_points_in_sphere(points, r, ctr)
    print intersect_r
    ren_win = vtk.vtkRenderWindow()
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    iren.SetRenderWindow(ren_win)
    ren = vtk.vtkRenderer()
    ren_win.AddRenderer(ren)

    # draw sphere
    ac = __add_sphere_to_ren(ctr, r, ren)
    ac.GetProperty().SetColor((1, 0, 0))
    #draw points
    r2 = 1
    for p in points:
        __add_sphere_to_ren(p, r2, ren)

    #draw plane
    plane_ctr = ctr + np.array(normal)
    __add_plane_to_ren(plane_ctr, normal, 2 * r, ren)
    iren.Initialize()
    iren.Start()


if __name__ == "__main__":
    __test_adjust_sphere()
    __test_intersect_point_with_sphere()
    __test_std_in_sphere()



