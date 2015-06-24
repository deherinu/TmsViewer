__author__ = 'Diego'
import os
import glob
import datetime

def find_all_calibration_dates():
    files_dir = r"C:\Users\jc.forero47\Dropbox\VaBD\ProyectoSavingBrains\TMS-Optitracking\TMS Data Mayo 2014\TMS_Data"
    pattern = "TMS-*.csv"
    full_path = os.path.join(files_dir,pattern)
    all_files = glob.iglob(full_path)

    calibration_dates = {}

    THRESHOLD = 10000

    for f in all_files:
        size = os.stat(f).st_size
        if size <= THRESHOLD:
            date = get_date(f)
            calibration_dates.setdefault(date,[]).append(f)

    possible_dates = [(k,len(v)) for k,v in calibration_dates.iteritems()]
    possible_dates.sort(key=lambda x:x[1],reverse=True)
    for k,v in possible_dates:
        print "%s : \t%d"%(k,v)

    for k,v in calibration_dates.iteritems():
        print "%s: %s"%(k,map(os.path.basename,v))

def get_date(file_name):
    with open(file_name) as f:
        line = f.readline()
        if len(line) == 0:
            return None
        tokens = line.split(";")
        date_str = tokens[1]
        date_and_time = datetime.datetime.strptime(date_str, "%a %b %d %H:%M:%S COT %Y")
        date = datetime.date(date_and_time.year,date_and_time.month,date_and_time.day)
        return date

if __name__ == "__main__":
    find_all_calibration_dates()