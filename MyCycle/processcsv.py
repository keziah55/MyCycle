"""
Provides functions to read csv data and supply it in html format for MyCycle
"""

import calendar
import re
import itertools
import sys


def head_tail(text):
    """ Return list of column headers and list of rows of data. """
    
    # split into individual lines
    lines = text.split('\n')
    
    # first non-empty line is taken to contain names
    match = None
    n = 0
    while True:
        match = re.match('\w', lines[n])
        if match is not None:
            break
        else:
            n += 1
            
    # split line containing column names into names
    names = lines[n].split(',')
    
    # remove empty lines
    # NB in the generic case, a different function should be supplied
    # _filter_csv returns True for lines which begin with a number
    lines = list(filter(_filter_csv, lines))
    
    return names, lines
    
    
def get_unique(text, which, case=True):
    """ Return unique values from either given column in csv text.
    
        Parameters
        ----------
        text : str
            string of csv data
        which : str, int
            name of index of column to analyse
        case : bool
            if True, `which` is case sensitive. If False it is not. 
            Default is True.
            
        Returns
        -------
        list of unique strings
    """
    
    names, lines = head_tail(text)
    
    # if column name was given...
    if isinstance(which, str):
        # if case insensitive
        if case is False:
            names = [name.lower() for name in names]
            which = which.lower()    
        
        if which not in names:
            raise ValueError('No column named "{}".'.format(which))
            sys.exit()
        else:
            idx = names.index(which)
            
    # ...or if column index was given
    elif isinstance(which, int):
        idx = which
    
    else:
        raise TypeError("'which' must be string or int")
        sys.exit(1)
    
    # get all values from column
    all_values = [line.split(',')[idx] for line in lines]
    
    # reduce to unique values
    unique = list(set(all_values))
    
    return unique


def get_hr_min_sec(total_sec):
    
    hr = total_sec // 3600
    rem = total_sec % 3600
    
    mn = rem // 60
    rem = rem % 60
    
    sc = rem
    
    hms = '{:02d}:{:02d}.{:02d}'.format(hr, mn, sc)
    
    return hms
    

def csv_to_html(text):
    """ Read given csv file and write html string."""
    
    html = ''
    
    html += get_preamble()
    
    if not text.strip():
        html += get_empty()
    
    else:
        keys, groups = _read_csv(text)
        
        for idx, key in enumerate(keys):
            
            # groups[idx] =  month, date, time, dist, cal, odo, time_sec
            
            total_time = sum(groups[idx][n][-1] for n in range(len(groups[idx])))
            total_time = get_hr_min_sec(total_time)
            
            total_cal = sum(groups[idx][n][4] for n in range(len(groups[idx])))
            
            total_dist = sum(groups[idx][n][3] for n in range(len(groups[idx])))
            
            data = [g[1:-1] for g in groups[idx]]
            
            # key is month
            html += get_header(len(data), key, total_time, total_cal, total_dist)
            html += get_table(data)
                
    html += get_close()
    
    return html


def _parse_line(line):
    """ Take line from csv and extract/reformat where necessary."""
    
    date, time, dist, cal, odo, gear, weight = re.split(',', line.strip())
    
    # date is in YYYY-MM-DD order, want DD Month YY, where Month is abbreviation
    date_list = re.split('-', date)
    date_list.reverse()
    
    # get month abbreviation and full name
    month_num = int(date_list[1])
    month_short = calendar.month_abbr[month_num]
    month_full = calendar.month_name[month_num]
    year = date_list[2]
    month = month_full + ' ' + year
    
    date_list[1] = month_short
    date_list[2] = date_list[2][-2:]  # remove century from year
    date = ' '.join(date_list)
    
    # if time is scalar, this is exact number of minutes
    if len(time.split(':')) == 1:
        time += ':00'
        
    min_sec = [int(t) for t in time.split(':')]
    
    # format time
    time = '{:02d}:{:02d}'.format(*min_sec)
    
    # get duration in seconds
    time_sec = min_sec[0]*60 + min_sec[1]
    
    dist, cal, odo = list(map(float, [dist, cal, odo]))
    
    
    return [month, date, time, dist, cal, odo, gear, weight, time_sec]

        
def _read_csv(text):

    _, lines = head_tail(text)
    
    lines.sort(reverse=True)
    
    # reformat date and get Month Year and pay
    for idx, line in enumerate(lines):
        lines[idx] = _parse_line(line)
        
    # group by month
    groups = []
    keys = []
    
    for k, g in itertools.groupby(lines, lambda l : l[0]):
        groups.append(list(g))
        keys.append(k)
        
    # put in reverse order
#    keys.reverse(), groups.reverse()
    
    return keys, groups

    
def _filter_csv(lst):
    """ Return True of element in list begins with string of numbers."""
    for l in lst:
        if re.match('\d+', l):
            return True
        else:
            return False
        
        
def get_preamble():
    
    preamble = '''
<!DOCTYPE html>
<html>
<head>
<style>

th {
    padding: 10px;
}
td {
    text-align: center;
}
header > h1 { display: inline-block; }
header span { font-size:25px; }
              
</style>
</head>
<body>
'''   
    return preamble


def get_close():
    return '\n</body>\n</html>'


def get_header(num, monthyear, total_time, total_cal, total_dist):
    
    space = '&nbsp;'
    
    h1 = '<h1>{}</h1>'.format(monthyear)

    lst = [f"{num} sessions", total_time, f"{total_dist:.2f} km", 
           f"{total_cal:.2f} cal"]
    h2 = f",{space}".join(lst)
    h2 = f"<h2>{h2}</h2>"

    header = h1+h2

    return header


def get_table(data):
    
    table_head = '''
<table>
    <tr>
        <th width=14.25%>Date</th>
        <th width=14.25%>Time</th>
        <th width=14.25%>Distance (km)</th>
        <th width=14.25%>Calories</th>
        <th width=14.25%>Odometer (km)</th>
        <th width=14.25%>Gear</th>
        <th width=14.25%>Weight (kg)</th>
    </tr>'''
    
    table_body = ''
    for row in data:
        table_body += '''
        <tr>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
        </tr>'''.format(*row)
    
    table_end = '''</table>'''
    
    table = table_head + table_body + table_end

    return table


def get_empty():
    
    message = '<p> There are no data to display.</p>'

    return message

