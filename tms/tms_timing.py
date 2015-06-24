from __future__ import division

import numpy as np
import scipy.stats

from tms import read_and_transform


__author__ = 'Diego'


def estimate_vrpn_clock_drift(points):
    # clocks = [map(np.datetime64,(p.date,p.ref_date,p.point_date)) for p in points]
    clocks = [(p.date, p.ref_date, p.point_date) for p in points]
    real_date, uni_date, obj_date = map(np.array, zip(*clocks))
    get_seconds = np.vectorize(lambda x: x.total_seconds())
    uni_obj = get_seconds(uni_date - obj_date)
    good_sample = uni_obj == 0
    good_real = real_date[good_sample]
    good_uni = uni_date[good_sample]
    assert good_uni.shape[0] > 0
    good_drift = good_real - good_uni
    mode_drift = scipy.stats.mode(good_drift)
    return mode_drift[0][0]


def add_time_drift_to_vrpn(point, drift):
    point.point_date = point.point_date + drift
    point.ref_date = point.ref_date + drift
    return point


def fix_vrpn_time_drift(points):
    drift = estimate_vrpn_clock_drift(points)
    for p in points:
        add_time_drift_to_vrpn(p, drift)
    return drift


def estimate_timing_errors(point, corrected=True):
    internal_error = abs((point.ref_date - point.point_date).total_seconds())
    if corrected:
        uni_error = abs((point.date - point.ref_date).total_seconds())
        obj_error = abs((point.date - point.point_date).total_seconds())
        return uni_error + obj_error + internal_error
    else:
        return internal_error


def __test():
    import os

    test_dir = os.path.join(os.path.dirname(__file__), "data")
    test_file = os.path.join(test_dir, "TMS-758.csv")
    test_file = os.path.join(test_dir, "TMS-441.csv")
    # test_file = os.path.join(test_dir, "TMS-310.csv")

    points = read_and_transform.read_csv_file(test_file)
    fix_vrpn_time_drift(points)
    print points[0]
    errors = [estimate_timing_errors(p, True) for p in points]
    mean_error = np.mean(errors)
    print "mean error:\t", mean_error
    print "std error:\t", np.std(errors)
    max_error = np.max(errors)
    print "max error:\t", max_error
    print "above 10% max:\t", len(filter(lambda x: x > max_error / 10, errors))


if __name__ == "__main__":
    __test()
