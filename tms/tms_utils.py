from __future__ import division

__author__ = 'Diego'

import datetime


class PointWithRef(object):
    "Hold point and reference data with position and orientation"

    def __init__(self, array=None):
        if (array == None):
            self.date = datetime.datetime(2999, 1, 1)
            self.ref_date = datetime.datetime(2999, 1, 1)
            self.point_date = datetime.datetime(2999, 1, 1)
            self.ref_pos = (0, 0, 0)
            self.point_pos = (0, 0, 0)
            self.ref_or = (1, 0, 0, 0)
            self.point_or = (1, 0, 0, 0)
            self.type = -1
        else:
            self.fromArray(array)

    def fromArray(self, array):
        """
        Set the attributes from an array containing
        [type,date, refdate, refposX,refposY,refposZ,refOr0,refOr1,refOr2,refOr3,
        pointdate,pointPosX,pointPosY,pointPosZ,pointOr0,pointOr1,pointOr2,pointOr3]"
        :param array: array
        :return: Nothing
        """
        self.type = int(array[0])
        self.date = datetime.datetime.strptime(array[1], "%a %b %d %H:%M:%S COT %Y")
        self.ref_date = datetime.datetime.strptime(array[2], "%a %b %d %H:%M:%S COT %Y")
        self.point_date = datetime.datetime.strptime(array[10], "%a %b %d %H:%M:%S COT %Y")
        self.ref_pos = tuple(map(float, array[3:6]))
        #Fix orientation -> The system gives x,y,z,w but normally it should be w,x,y,z
        self.ref_or = tuple(map(float, array[9:10]+array[6:9]))
        self.point_pos = tuple(map(float, array[11:14]))
        #Fix orientation -> The system gives x,y,z,w but normally it should be w,x,y,z
        self.point_or = tuple(map(float, array[17:18]+array[14:17]))

    def copy(self):
        new_point = PointWithRef()
        new_point.type = self.type
        new_point.date = self.date
        new_point.ref_date = self.ref_date
        new_point.point_date = self.point_date

        new_point.ref_pos = tuple(self.ref_pos)
        new_point.point_pos =tuple( self.point_pos)

        new_point.ref_or =tuple( self.ref_or)
        new_point.point_or = tuple(self.point_or)

        return new_point


    def __str__(self):
        return "\n".join(
            ["Point with reference:",
             "=====================",
             "Type: %d"%self.type,
             "Capture Time : %s"%self.date.strftime("%a %b %d %H:%M:%S COT %Y"),
             "Refer.  Time : %s"% self.ref_date.strftime("%a %b %d %H:%M:%S COT %Y"),
             "Object  Time : %s"% self.point_date.strftime("%a %b %d %H:%M:%S COT %Y"),
             "Ref.    pos  : %s" % (" , ".join("%.2f"%p for p in self.ref_pos)),
             "Ref.    orn  : %s" % (" , ".join("%.2f"%p for p in self.ref_or)),
             "object  pos  : %s" % (" , ".join("%.2f"%p for p in self.point_pos)),
             "object  orn  : %s" % (" , ".join("%.2f"%p for p in self.point_or)),
            ])+"\n"

    def __repr__(self):
        return "("+",".join(map(str,(self.type,self.date,self.point_date,self.point_pos,self.point_or,
        self.ref_date,self.ref_pos,self.ref_or)))+")"