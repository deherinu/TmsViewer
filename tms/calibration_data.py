"""
Hold structures containing data and calibration results
"""

from __future__ import division
import datetime
from collections import namedtuple

Calibration = namedtuple("Calibration", ["Pointer", "Coil"])

"""
NOTE: The important date is the date where an incident leading to a re-calibration happened, NOT the date of
the calibration itself
"""
INCIDENT_DATES = [datetime.date(2013, 3, 15),  # System startup
                  datetime.date(2013, 4, 24),  # recalibration
                  datetime.date(2013, 5, 27),  # Broken coil arm
                  datetime.date(2013, 9, 18),  # Change of cameras
                  datetime.date(2013, 11, 18),  # Broken coil arm
                  datetime.date(2014, 4, 23),  # Cameras moved to check license
]

INCIDENT2CALIB = {datetime.date(2013, 3, 15): datetime.date(2013, 4, 11),
                  datetime.date(2013, 4, 24): datetime.date(2013, 4, 24),
                  datetime.date(2013, 5, 27): datetime.date(2013, 7, 3),
                  datetime.date(2013, 9, 18): datetime.date(2013, 9, 18),
                  datetime.date(2013, 11, 18): datetime.date(2013, 11, 20),
                  datetime.date(2014, 04, 23): datetime.date(2014, 07, 31),
}

CALIB_DATES = [datetime.date(2013, 4, 11),
               datetime.date(2013, 4, 24),
               datetime.date(2013, 7, 3),
               datetime.date(2013, 9, 18),
               datetime.date(2013, 11, 20),
               datetime.date(2014, 05, 20),
               datetime.date(2014, 07, 31)
]

CALIB_SAMPLES = {datetime.date(2013, 4, 11): Calibration(Pointer=["1002", "1003", "1004", "1005", "10021",
                                                                  "10031", "10032"],
                                                         Coil=["1006", "1007", "1008", "1009"]),
                 datetime.date(2013, 4, 24): Calibration(Pointer=["1201", "1202", "1203", "1204", "1207",
                                                                  "1208", "1209"],
                                                         Coil=["1210", "1212", "1213", "1214", "1215", "1216"]),
                 datetime.date(2013, 7, 3): Calibration(Pointer=[],  # Pointer was not affected by incident
                                                        Coil=[80001, 80003, 80004, 80006]),
                 datetime.date(2013, 9, 18): Calibration(Pointer=['5000', '5001', '5002', '5003', '5004'],
                                                         Coil=['5005', '5006', '5007', '5008']),
                 datetime.date(2013, 11, 20): Calibration(Pointer=['50000', '50100', '50200'],
                                                          Coil=['50300', '50400', '50500', '50600']),
                 datetime.date(2014, 05, 20): Calibration(Pointer=
                                                          ['89100', '89200', '89300', '89400', '89500', '89600',
                                                           '89700', '89800', '89900', '89910', '89920'],
                                                          Coil=['40600', '40700', '40800', '40900', '50100']
                 ),
                 datetime.date(2014, 07, 31): Calibration(
                     Pointer=["60000", "61000", "62000", "65000", "66000"],
                     Coil=["72000", "74000", "75000", "76000", "77000", "78000"]
                 ),
                 }

RULER_SAMPLES = ["67000","68000","70000","79000","80000"]

DISTANCE_CONSTANT = 0.808683002347

CalibrationResults = namedtuple("CalibrationResults",
                                ["Pointer_v", "Pointer_score", "Coil_vc", "Coil_vt", "Coil_v2_score"])
CALIB_RESULTS = {
    datetime.date(2013, 4, 11): CalibrationResults((0.098375330930390123, 0.083144699264077554, -0.15265044232796784),
                                                   0.143546943395,
                                                   (0.01136029497968935, 0.117976304258855, -0.012214941030153723),
                                                   (
                                                       -0.0078032050711651299, 0.019829730384275462,
                                                       -0.012108009645751169),
                                                   0.241601601215),

    datetime.date(2013, 4, 24): CalibrationResults((-0.13408449309806408, -0.042839431502549027, 0.086647120191742269),
                                                   0.000441893111878,
                                                   (0.063354348063529548, -0.054615370245580462, 0.03545699782235532),
                                                   (0.064260296056680918, -0.13756625923128699, 0.091298968756185206),
                                                   2.14738156758),

    datetime.date(2013, 7, 3): CalibrationResults((-0.13408449309806408, -0.042839431502549027, 0.086647120191742269),
                                                  0.000441893111878,  # Pointer was not affected by incident
                                                  (0.031305959253347428, -0.073765063359274408, -0.060189329861594462),
                                                  (0.030812382353119699, -0.17359378111224416, -0.066019054921502354),
                                                  0.0230167171146),

    datetime.date(2013, 9, 18): CalibrationResults((0.097689363263547921, 0.01811019714562951, -0.14216691067117207),
                                                   0.0593785878064,
                                                   (0.086146638225653938, 0.020844548463599302, 0.020055091547824574),
                                                   (0.1285699533510111, -0.018603615176119508, 0.10156646081684417),
                                                   0.0486461288349),
    datetime.date(2013, 11, 20): CalibrationResults((0.097689363263547921, 0.01811019714562951, -0.14216691067117207),
                                                    0.0593785878064,  # Pointer was not affected by incident,
                                                    # and these samples look fishy
                                                    (0.011881178669345965, -0.058307213663444477,
                                                     -0.0095281081458971507),
                                                    (
                                                        -0.023452352830150566, 0.0038519822945396382,
                                                        0.060384538491877651),
                                                    9.17018508408e-09),  # very strange, only one good sample
    datetime.date(2014, 5, 20): CalibrationResults(
        (-0.0034266019861622773, 0.14676623217464224, -0.0067530244406257345),
        0.398133337989,
        None,
        None,
        None),
        datetime.date(2014, 7, 31): CalibrationResults(
        (0.015612569292322808, 0.10491035286175734, -0.018835798313621827) ,
        0.330283650093 ,
        #(-0.0034266019861622773, 0.14676623217464224, -0.0067530244406257345),
        #0.398133337989,
        (0.044005793418885705, -0.0019669601204190517, 0.033948302653644867) ,
        (0.076988920064578817, 0.082906645305554846, -0.0073867231250567648) ,
        7.56540036715e-05 ),
}



