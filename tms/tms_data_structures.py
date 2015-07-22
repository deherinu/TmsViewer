from __future__ import division

import numpy as np
import re
import csv
import read_and_transform
from tms import tms_geom
import tms_timing
import Blocks

__author__ = 'Diego'


class TmsSample(object):
    def __init__(self, point_data):
        # data
        self.point_data = point_data
        self.timing_error = None
        self.ignored = False

        # geometry
        self.sphere_intersection = None
        self.coil_center = None
        self.coil_top = None

        coil_fun = read_and_transform.get_coil_transform_function(point_data.date)
        self.coil_center, self.coil_top = coil_fun(point_data)

        #recalculate coil_center, coil_top


        self.calculate_timing_error()

    @property
    def date(self):
        return self.point_data.date

    def calculate_timing_error(self):
        self.timing_error = tms_timing.estimate_timing_errors(self.point_data)

    def calculate_sphere_intersection(self, sphere_r, sphere_center):
        ctr, top = self.coil_center, self.coil_top
        self.sphere_intersection = tms_geom.intersect_point_with_sphere(ctr, top - ctr, sphere_r, sphere_center)


class TmsBlock(object):
    __BLOCK_TYPES_DICT = {
        "UNKNOWN": 0,
        "ACCEPTED": 1,
        "REJECTED": 2,
        "IGNORED": 3,
    }
    BLOCK_TYPES = ("UNKNOWN", "ACCEPTED", "REJECTED", "IGNORED",)


    def __init__(self, points):
        # data
        self.samples = [TmsSample(p) for p in points]
        self.start = min((p.date for p in self.samples))
        self.end = max((p.date for p in self.samples))
        self.position_error = None
        self.max_timing_error = None
        self.hemisphere = None
        self.__block_type = 0

        # geometry
        self.circle_radius = None
        self.circle_relative_center = None

        self.mean_intersection = None
        self.mean_coil_center = None

        self.update_timing_error()

    @property
    def block_type(self):
        return self.BLOCK_TYPES[self.__block_type]

    @block_type.setter
    def block_type(self, val):
        self.__block_type = self.__BLOCK_TYPES_DICT[val.upper()]

    def update_timing_error(self):
        good_samples = [s.timing_error for s in self.samples if not s.ignored]
        if len(good_samples) == 0:
            self.max_timing_error = np.nan
        else:
            self.max_timing_error = np.max(good_samples)

    def calculate_sphere_intersection(self, sphere_r, sphere_center):
        #print 'Calculate sphere intersection'
        for s in self.samples:
            s.calculate_sphere_intersection(sphere_r, sphere_center)
        self.recalculate_mean_and_error(sphere_r, sphere_center)


    def recalculate_mean_and_error(self, sphere_r, sphere_center):
        #print 'Recalculate mean and error'
        coil_centers = [p.coil_center for p in self.samples if not p.ignored]
        points_on_sphere = [p.sphere_intersection for p in self.samples if not p.ignored]
        points_on_sphere = filter(lambda x: x is not None, points_on_sphere)
        #print '1'
        if len(points_on_sphere) < 2:
            #print '2'
            v,r = np.array((0,0,0)),0
            self.mean_intersection = np.zeros(3)
            self.mean_coil_center = np.zeros(3)
        else:
            #print '3'
            v, r = tms_geom.circle_from_points_in_sphere(points_on_sphere, sphere_r, sphere_center)
            #print '4'
            self.mean_intersection = np.mean(points_on_sphere, axis=0)
            #print '5'
            self.mean_coil_center = np.mean(coil_centers, axis=0)
        #print '6'
        self.circle_radius = r
        self.circle_relative_center = v
        self.position_error = r



    def find_hemisphere(self, calib_points, sphere_center):
        v1 = calib_points["vertex"] - sphere_center
        v2 = calib_points["nasion"] - sphere_center
        v3 = np.cross(v1, v2)
        if np.dot(v3, self.mean_intersection - sphere_center) >= 0:
            self.hemisphere = "l"
        else:
            self.hemisphere = "r"


class TmsExperiment(object):

    def __init__(self):
        # data
        self.blocks = None
        self.calibration = None
        self.mid_date = None
        self.total_duration = None
        self.raw_points = None
        self.normalized_points = None

        # geometry
        self.sphere_center = None
        self.sphere_radius = None
        self.calibration_points = None

        #hacks
        self.hacks = None

    def set_points(self, points,file_name, normalize=True,hacks = None):
        self.hacks = hacks
        self.raw_points = points
        self.total_duration = points[-1].date - points[0].date
        self.mid_date = points[len(points) // 2].date
        self.__correct_time_offset()
        if hacks is not None and hacks.get("Not_Normalize"):
            normalize = False
        if normalize:
            self.__spatially_normalize()
        else:
            self.normalized_points = self.raw_points
        self.__calculate_calibration(file_name)
        self.__create_blocks(file_name)
        print "done loading"

    def _create_csv(self,filenamecsv):
        textlist = []
        with open(filenamecsv, 'rb') as csvfile:
            textlist = csv.reader(csvfile).next()

        textlist[0]
        datalist = []

        type_re = re.compile('Type: (\d)')
        capture_re = re.compile('Capture Time : (.*?)\\n')
        refertime_re = re.compile('Refer.  Time : (.*?)\\n')
        objecttime_re = re.compile('Object  Time : (.*?)\\n')
        refpos_re = re.compile('Ref.    pos  : (.*?)\\n')
        reforn_re = re.compile('Ref.    orn  : (.*?)\\n')
        objectpos_re = re.compile('object  pos  : (.*?)\\n')
        objectorn_re = re.compile('object  orn  : (.*?)\\n')

        for r in textlist:
            _type = type_re.search(r).group(1)
            _capture = capture_re.search(r).group(1)
            _capture = ''.join(_capture.splitlines())
            _refertime = refertime_re.search(r).group(1)
            _refertime = ''.join(_refertime.splitlines())
            _objecttime = objecttime_re.search(r).group(1)
            _objecttime = ''.join(_objecttime.splitlines())
            _refpos = refpos_re.search(r).group(1)
            _refpos = ''.join(_refpos.splitlines())
            _refpositions = _refpos.split(',')
            _reforn = reforn_re.search(r).group(1)
            _reforn = ''.join(_reforn.splitlines())
            _reforns = _reforn.split(',')
            _objectpos = objectpos_re.search(r).group(1)
            _objectpos = ''.join(_objectpos.splitlines())
            _object_positions = _objectpos.split(',')
            _objectorn = objectorn_re.search(r).group(1)
            _objectorn = ''.join(_objectorn.splitlines())
            _object_orns = _objectorn.split(',')
            datalist.append([_type, _refpositions[0], _refpositions[1], _refpositions[2], _reforns[0], _reforns[1], _reforns[2], _reforns[3], _object_positions[0], _object_positions[1], _object_positions[2], _object_orns[0], _object_orns[1], _object_orns[2], _object_orns[3]])
        with open(filenamecsv, 'wb') as f:
            writer = csv.writer(f, delimiter=',', lineterminator='\n')
            writer.writerows(datalist)

    def _create_new_data(self,coil_points,file_name):
        #Method create new list (coil data)

        #Create csv file with new coil positions
        temp = file_name.split('/')
        lastone = len(temp)
        newfile_data_csv = temp[lastone-1]
        print newfile_data_csv
        textlist = []
        with open('calib_data/calib_points/new_pos/'+newfile_data_csv, 'rb') as csvfile:
            textlist = csv.reader(csvfile, delimiter=',', lineterminator='\n')
            my_list=list(textlist)

        #Asign new coil points
        for i in range(0,coil_points.__len__()):
           coil_points[i].point_pos = (float(my_list[i][0]), float(my_list[i][1]), float(my_list[i][2]))
           coil_points[i].ref_pos = (float(my_list[i][3]), float(my_list[i][4]), float(my_list[i][5]))

        return coil_points


    def __create_blocks(self,file_name):
        coil_points = read_and_transform.extract_coil_samples(self.normalized_points)
        #print "Tamano coil: %s" %len(coil_points)

        #Get file name
        temp = file_name.split('/')
        lastone = len(temp)
        newfile = temp[lastone-1]
        csvfile="calib_data/calib_points/"+newfile

        #Save file with calib coil_points
        with open(csvfile, "w") as output:
            writer = csv.writer(output, lineterminator='\n')
            writer.writerows([coil_points])

        #Generate new coil points
        self._create_csv(csvfile)
        coil_points=self._create_new_data(coil_points,csvfile)
        #print 'Nuevos datos coil'
        #print coil_points

        #Generate blocks to visualize
        blocks_indices = Blocks.get_blocks(coil_points, 7)

        # remove small blocks
        blocks_indices = filter(lambda x: len(x) > 5, blocks_indices)
        blocks = []
        for bi in blocks_indices:
            #print 'Creating blocks'
            points = [coil_points[i] for i in bi]
            b = TmsBlock(points)
            b.calculate_sphere_intersection(self.sphere_radius, self.sphere_center)
            b.find_hemisphere(self.calibration_points, self.sphere_center)
            blocks.append(b)
        self.blocks = blocks


    def __calculate_calibration(self,file_name):

        calibration_samples = read_and_transform.extract_calibration_samples(self.normalized_points)
        self.calibration_points = {}
        point_function = read_and_transform.get_pointer_transform_function(self.mid_date)
        for label, index in read_and_transform.CALIBRATION_LABELS.iteritems():
            raw_point = calibration_samples[index]
            tip = point_function(raw_point)
            self.calibration_points[label] = tip

        #Get file name
        temp = file_name.split('/')
        lastone = len(temp)
        newfile = temp[lastone-1]
        datalist=[]

        #Create order list of calibration points
        calibration_names = ['right', 'vertex', 'nasion', 'left']
        for key in calibration_names:
            temp_points = self.calibration_points[key]
            datalist.append([temp_points[0], temp_points[1], temp_points[2]])

        #Write csv file with calibration points
        with open("calib_data/calib_pills/tms/"+newfile, 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(datalist)

        #Matlab method, rigid transformation
        # Input new_data/calib_pills/tms/subject.csv (429.csv)
        # Output new_data/calib_pills/tms/new_pos/subject.csv (TMS-429.csv)
        #
        #
        #
        #

        #Get result of matlab method new pills position
        textlist = []
        with open('calib_data/calib_pills/tms/new_pos/'+newfile, 'rb') as csvfile:
            textlist = csv.reader(csvfile, delimiter=',', lineterminator='\n')
            my_list=list(textlist)

        #Parsing float the list items
        my_list = [[float(i) for i in tt] for tt in my_list]

        #Gen new calibration points
        for newvalue in range(0,self.calibration_points.__len__()):
            if newvalue == 0 :
                self.calibration_points['right'][0] = my_list[newvalue][0]
                self.calibration_points['right'][1] = my_list[newvalue][1]
                self.calibration_points['right'][2] = my_list[newvalue][2]
            if newvalue == 1 :
                self.calibration_points['vertex'][0] = my_list[newvalue][0]
                self.calibration_points['vertex'][1] = my_list[newvalue][1]
                self.calibration_points['vertex'][2] = my_list[newvalue][2]
            if newvalue == 2 :
                self.calibration_points['nasion'][0] = my_list[newvalue][0]
                self.calibration_points['nasion'][1] = my_list[newvalue][1]
                self.calibration_points['nasion'][2] = my_list[newvalue][2]
            if newvalue == 3 :
                self.calibration_points['left'][0] = my_list[newvalue][0]
                self.calibration_points['left'][1] = my_list[newvalue][1]
                self.calibration_points['left'][2] = my_list[newvalue][2]

        print 'Nuevos puntos calibracion'
        print self.calibration_points

        if self.hacks is not None:
            skip = set(self.hacks.get("skip_calib",set()))
            pts = [v for k,v in self.calibration_points.iteritems() if k not in skip]
            r, ctr = tms_geom.adjust_sphere(pts)
        else:
            r, ctr = tms_geom.adjust_sphere(self.calibration_points.itervalues())

        self.sphere_radius, self.sphere_center = r, ctr


    def __spatially_normalize(self):
        n_points = len(self.raw_points)
        mid_point = self.raw_points[n_points // 2]
        self.normalized_points = read_and_transform.normalize_to_ref(self.raw_points, mid_point)

    def __correct_time_offset(self):
        tms_timing.fix_vrpn_time_drift(self.raw_points)

    def update_block(self, block):
        assert isinstance(block, TmsBlock)
        block.recalculate_mean_and_error(self.sphere_radius, self.sphere_center)
        block.update_timing_error()
        block.find_hemisphere(self.calibration_points, self.sphere_center)