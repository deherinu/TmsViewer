__author__ = 'jc.forero47'



def get_blocks(coil_points,threshold):
    """
    Returns a list with blocks. Each block contains the number of line in the .csv file
    Each block is created if the difference between samples is greater than threshold (seconds)
    :param coil_points List of points from coil.
    :param threshold difference threshold between blocks in seconds
    """
    blocks=list()
    blocks.append(list())
    b=0
    blocks[0].append(0)
    for i in xrange(len(coil_points)-1):
        date_a=coil_points[i].date
        date_b=coil_points[i+1].date
        dif=(date_b-date_a)
        if dif.total_seconds()>threshold:
            b=b+1
            blocks.append(list())
        blocks[b].append(i+1)
    return blocks
