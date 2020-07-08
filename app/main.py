import logging, functools
from fastapi import FastAPI
from datetime import datetime, timedelta


##################################################
# Common variables
##################################################

NOW = datetime.now

logger = logging.getLogger("app")

app = FastAPI()

fake_db = [
    {'id':1, 'station_id': 10, 'start': '09/30/00', 'end': '13/00/00', 'day':1 },
    {'id':2, 'station_id': 10, 'start': '13/30/00', 'end': '19/00/00', 'day':1 },
    {'id':3, 'station_id': 10, 'start': '09/30/00', 'end': '13/00/00', 'day':2 },
    {'id':4, 'station_id': 10, 'start': '13/30/00', 'end': '19/00/00', 'day':2 },
    {'id':5, 'station_id': 10, 'start': '09/30/00', 'end': '13/00/00', 'day':3 },
    {'id':6, 'station_id': 10, 'start': '13/30/00', 'end': '19/00/00', 'day':3 },
    {'id':7, 'station_id': 10, 'start': '09/30/00', 'end': '13/00/00', 'day':4 },
    {'id':8, 'station_id': 10, 'start': '13/30/00', 'end': '19/00/00', 'day':4 },
    {'id':9, 'station_id': 10, 'start': '09/30/00', 'end': '13/00/00', 'day':5 },
    {'id':10, 'station_id': 10, 'start': '13/30/00', 'end': '19/00/00', 'day':5 },
    {'id':11, 'station_id': 11, 'start': '09/30/00', 'end': '13/00/00', 'day':1 },
    {'id':12, 'station_id': 11, 'start': '13/30/00', 'end': '19/00/00', 'day':1 },
    {'id':13, 'station_id': 11, 'start': '09/30/00', 'end': '13/00/00', 'day':2 },
    {'id':14, 'station_id': 11, 'start': '13/30/00', 'end': '19/00/00', 'day':2 },
    {'id':15, 'station_id': 11, 'start': '09/30/00', 'end': '13/00/00', 'day':3 },
    {'id':16, 'station_id': 11, 'start': '13/30/00', 'end': '19/00/00', 'day':3 },
    {'id':17, 'station_id': 11, 'start': '09/30/00', 'end': '13/00/00', 'day':4 },
    {'id':18, 'station_id': 11, 'start': '13/30/00', 'end': '19/00/00', 'day':4 },
    {'id':19, 'station_id': 11, 'start': '09/30/00', 'end': '13/00/00', 'day':5 },
    {'id':20, 'station_id': 11, 'start': '13/30/00', 'end': '19/00/00', 'day':5 },
    {'id':21, 'station_id': 11, 'start': '09/30/00', 'end': '13/00/00', 'day':6 },
    {'id':22, 'station_id': 11, 'start': '13/30/00', 'end': '19/00/00', 'day':6 },
    {'id':23, 'station_id': 12, 'start': '09/30/00', 'end': '13/00/00', 'day':1 },
    {'id':24, 'station_id': 12, 'start': '13/30/00', 'end': '19/00/00', 'day':1 },
    {'id':25, 'station_id': 12, 'start': '09/30/00', 'end': '13/00/00', 'day':3 },
    {'id':26, 'station_id': 12, 'start': '13/30/00', 'end': '19/00/00', 'day':3 },
    {'id':27, 'station_id': 12, 'start': '09/30/00', 'end': '13/00/00', 'day':5 },
    {'id':28, 'station_id': 12, 'start': '13/30/00', 'end': '19/00/00', 'day':5 },
]

exception_db = [
    {'id':1, 'station_id': 10, 'start': '2020-07-09:09/30/00', 'end': '2020-07-11:09/30/00'},
    {'id':2, 'station_id': 11, 'start': '2020-07-08:09/30/00', 'end': '2020-07-08:13/30/00'},
    {'id':3, 'station_id': 12, 'start': '2020-07-07:09/30/00', 'end': '2020-07-08:09/30/00'}
]
################################################################################
# utils
################################################################################
def check_exception_date():
    def wrapper(func):
        @functools.wraps(func)
        async def decorated_func(*args):
            id, day = args[0], args[1]
            exception = [*filter(lambda x: x.get('station_id')==int(id) and datetime.strptime(x.get('start'), "%Y-%m-%d:%H/%M/%S").date() <= day.date() and datetime.strptime(x.get('end'), "%Y-%m-%d:%H/%M/%S") > day , exception_db)]
            if len(exception) > 0:
                return False, exception[0]
            else:
                return await func(*args)
        return decorated_func
    return wrapper


async def make_base_schedule(base_schedule, day):
    for i,point in enumerate(base_schedule):
        if point.get('day') == day.isoweekday():
            return base_schedule[i:i+5]


async def make_point_line(base_schedule):
    point_line = []
    for p in base_schedule:
        point_line.append(('opened', p.get('start')))
        point_line.append(('closed', p.get('end')))
    return point_line


async def make_intervals(point_line):
    intervals = []
    for i in range(len(point_line)-1):
        intervals.append((point_line[i][1], point_line[i+1][1], point_line[i+1][0]))
    return intervals


async def next_action(intervals, today):
    _,at,action = [*filter(lambda x: datetime.strptime(x[0], "%H/%M/%S").time() < today.time() and datetime.strptime(x[1], "%H/%M/%S").time() > today.time(), intervals)][0]
    return f"Station will be {action} at {at}"

@check_exception_date()
async def check_is_open(id, today) -> bool:
    p = [*filter(lambda x: x.get('station_id')==int(id) and x.get('day')==int(today.isoweekday()) and datetime.strptime(x.get('start'), "%H/%M/%S").time() < today.time() and datetime.strptime(x.get('end'), "%H/%M/%S").time() > today.time(), fake_db)]
    return (True, None) if len(p)>0 else (False, None)

@check_exception_date()
async def request_next_action(id, today):
    station_schedule = [*filter(lambda x: x.get('station_id') == int(id), fake_db)]
    base_schedule = await make_base_schedule(station_schedule, today)
    point_line = await make_point_line(base_schedule)
    intervals = await make_intervals(point_line)
    return_action = await next_action(intervals, today)
    return True,return_action

################################################################################
# Endpoints
################################################################################

@app.get('/stations/{id}/isopen/')
async def station_is_open(id: int):
    today = NOW()
    is_open,_ = await check_is_open(id, today)
    return {"is_open": is_open}


@app.get('/stations/{id}/next/')
async def station_next_action(id: int):
    today = NOW()
    check,return_action = await request_next_action(id, today)
    if check:
        return {"msg": return_action}
    else:
        return {"msg": f"Station will be opened at {return_action.get('end')}"}
