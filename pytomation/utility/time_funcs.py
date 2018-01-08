from datetime import datetime, timedelta

def to_datetime(now, string):
    if len(string) != 6:
        return None

    # if any field is '*' then make it equal to current time
    if string[0] == '*':
        secs = now.second
    else:
        secs = string[0]
    if string[1] == '*':
        mins = now.minute
    else:
        mins = string[1]
    if string[2] == '*':
        hours = now.hour
    else:
        hours = string[2]
    if string[3] == '*':
        dom = now.day
    else:
        dom = string[3]
    if string[4] == '*':
        mon = now.month
    else:
        mon = string[4]
    if string[5] == '*':
        dow = now.weekday()
    else:
        dow = string[5]
    
    return (datetime(now.year,mon,dom,hours,mins,secs))


def crontime_in_range(now, start, end):
    dt_start = to_datetime(now, start)
    dt_end = to_datetime(now, end,)
    if dt_start == None or dt_end == None:
        return False
        
    # take care of weekday
    dw_start = start[5]
    dw_end = end[5]
    if dw_start != '*' and dw_end != '*':
        if dw_start == dw_end != now.weekday():
            return False
        elif dw_start > dw_end:
            dt_end = dt_end + timedelta(weeks=1)
            if now.weekday() < dw_start:
                now = now + timedelta(weeks=1)
        else:
            if dw_start <= now.weekday() <= dw_end:
                dt_end = dt_end + timedelta(days=dw_end - dw_start)
            
    if dt_start > dt_end:
        dt_end = dt_end + timedelta(days=365)
        if now < dt_start:
            now = now + timedelta(days=365)
            
    if dt_start <= now <= dt_end:
        return True

    return False

