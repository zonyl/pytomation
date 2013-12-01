import datetime

def crontime_in_range(item, start, end):
    startDt = datetime.datetime.strptime("{2}:{1}:{0}".format(*start[0:3]), '%H:%M:%S')
    endDt = datetime.datetime.strptime("{2}:{1}:{0}".format(*end[0:3]), '%H:%M:%S')
    itemDt = datetime.datetime.strptime("{2}:{1}:{0}".format(*item[0:3]), '%H:%M:%S')

    if startDt > endDt:
        endDt=endDt + datetime.timedelta(days=1)
        if itemDt < startDt:
            itemDt = itemDt + datetime.timedelta(days=1)

    if startDt <= itemDt <= endDt:
        #should technically check dates in cron as well.. for another day
        return True

    return False