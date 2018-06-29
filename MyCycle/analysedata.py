"""
Provides functions to analyse a DataObject
"""

from calendar import month_name

def _round(n):
    return int(round(n))

def minsec_to_hr(s):
    mn_sc = s.split(':')
    mn, sc = [int(i) for i in mn_sc]
    hr = (mn+sc/60)/60
    return hr


def hr_to_hrminsec(f):
    hr = int(f)
    mn = int(60*(f%1))
    sc = _round(60*((60*(f%1))%1))
    return '{}:{}.{}'.format(hr, mn, sc)


def _minsec_to_sec(s):
    
    s_spl = s.split(':')
    s_spl = list(map(int, s_spl))
    
    try:
        mns, sec = s_spl
    except ValueError:
        mns = s_spl[0]
        sec = 0
        
    total = 60 * mns + sec
    
    return total


def _normalise(time, value, wrt='min'):
    # Normalise a value 
    # `time` should be in seconds
    # `wrt` should be 'sec', 'min' or 'hr'
    
    factor = {'sec':1, 'min':60, 'hr':3600}
    
    mult = factor[wrt]
    
    return mult * value / time


def get_best_session(data):
    
    when = ''
    best = 0
    
    for d in data:
        time = minsec_to_hr(d[1])
        avg_speed = d[2]/time
        if avg_speed > best:
            best = avg_speed
            year, mnth, day = d[0].split('-')
            when = day + 'th ' + month_name[int(mnth)] + ' ' + year
            
    return best, when


def get_best_month(data):
    
    months = split_by_month(data)
    
    best = 0
    when = ''
    
    for month in months:
        
        dist = sum([m[2] for m in month])
        
        if dist > best:
            
            best = dist
            
            year, mnth, _ = month[0][0].split('-')
            when = month_name[int(mnth)] + ' ' + year
            
            time = sum([minsec_to_hr(item[1]) for item in month])
            time = hr_to_hrminsec(time)
            cal = sum([m[3] for m in month])
    
    return best, when, time, cal
    

def split_by_month(data):
    
    result = []
    prev_month = ''
    this_month = []
    
    for idx, item in enumerate(data.getColumn(0)):
        _, month, _ = item.split('-')
        if month == prev_month:
            this_month.append(data[idx])
            prev_month = month
        else:
            result.append(this_month)
            this_month = [data[idx]]
            prev_month = month
            
    result.append(this_month)
            
    result.pop(0)
    
    return result



    
    
    