def crontime_in_range(item, start, end):
    s_s, s_m, s_h = start[0:3]
    e_s, e_m, e_h = end[0:3]
    i_s, i_m, i_h = item[0:3]
    if e_h >= s_h and e_m >= s_m and e_s >= s_s:
        if i_h >= s_h and i_m >= s_m and i_s >= s_s and \
            i_h <= e_h and i_m <= e_m and i_s <= e_s:
                return True
    else:
        if i_h >= s_h and i_m >= s_m and i_s >= s_s or \
            i_h <= e_h and i_m <= e_m and i_s <= e_s:
                return True
    return False