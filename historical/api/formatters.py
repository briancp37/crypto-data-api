import datetime
import time
import calendar

class TS:
    def __init__(self):
        pass

    def str_to_unix(self, str_ts):
        datetime_obj = datetime.datetime.strptime(str_ts, '%Y-%m-%d %H:%M:%S')
        unix = time.mktime(datetime_obj.timetuple()) * 1000
        return unix

    def str_to_unix1(self, str_ts, timezone='UTC'):
        if timezone == 'UTC':
            return calendar.timegm(str_ts.timetuple()) * 1000.0
        else:
            return time.mktime(str_ts.timetuple()) * 1000.0

    def dt_to_unix(self, dt, timezone='UTC'):
        if timezone == 'UTC':
            return calendar.timegm(dt) * 1000.0
        else:
            return time.mktime(dt) * 1000.0

    def current_ts_str(self):
        dt = datetime.datetime.utcnow().replace(minute=0, second=0)
        ts_cur_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        return ts_cur_str

