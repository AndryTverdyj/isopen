import pytest
import json
import datetime
from collections import namedtuple
from fastapi.testclient import TestClient
from .main import (
    app,
    make_base_schedule,
    make_point_line,
    make_intervals
    )


@pytest.fixture(scope="module")
def test_app():
    client = TestClient(app)
    yield client


def test_initial(test_app):
    response = test_app.get('/stations/10/isopen/')
    assert response.status_code == 200


def test_incorest_id_str(test_app):
    response = test_app.get('/stations/string/isopen/')
    assert response.status_code == 422


def test_incorest_id_float(test_app):
    response = test_app.get('/stations/10.7/isopen/')
    assert response.status_code == 422


def test_incorest_id_other(test_app):
    response = test_app.get('/stations/@/isopen/')
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_make_base_schedule():
    test_data = [
        {'id':1, 'station_id': 10, 'start': '09/30/00', 'end': '13/00/00', 'day':1 },
        {'id':2, 'station_id': 10, 'start': '13/30/00', 'end': '19/00/00', 'day':1 },
        {'id':11, 'station_id': 11, 'start': '09/30/00', 'end': '13/00/00', 'day':1 },
        {'id':12, 'station_id': 11, 'start': '13/30/00', 'end': '19/00/00', 'day':1 },
        {'id':23, 'station_id': 12, 'start': '09/30/00', 'end': '13/00/00', 'day':1 },
        {'id':24, 'station_id': 12, 'start': '13/30/00', 'end': '19/00/00', 'day':1 },
    ]
    test_day_1 = datetime.datetime(2020, 7, 6, 13, 47, 45)
    test_day_2 = datetime.datetime(2020, 7, 9, 13, 47, 45)
    test_data_station_10 = [*filter(lambda x: x.get('station_id') == 10, test_data)]
    test_data_station_20 = [*filter(lambda x: x.get('station_id') == 20, test_data)]
    per = namedtuple('per', 'id, station_id, start, end, day, day_week_year')

    assert await make_base_schedule(test_data_station_10, test_day_1) == [
         per(id=1, station_id=10, start='09/30/00', end='13/00/00', day=1, day_week_year='1-27-2020'),
         per(id=2, station_id=10, start='13/30/00', end='19/00/00', day=1, day_week_year='1-27-2020'),
         per(id=1, station_id=10, start='09/30/00', end='13/00/00', day=1, day_week_year='1-28-2020'),
         per(id=2, station_id=10, start='13/30/00', end='19/00/00', day=1, day_week_year='1-28-2020')
    ]
    assert await make_base_schedule(test_data_station_20, test_day_1) == []
    assert await make_base_schedule(test_data_station_10, test_day_2) == []
    assert await make_base_schedule(test_data_station_20, test_day_2) == []

@pytest.mark.asyncio
async def test_make_point_line():
    per = namedtuple('per', 'id, station_id, start, end, day, day_week_year')
    test_data = [
         per(id=1, station_id=10, start='09/30/00', end='13/00/00', day=1, day_week_year='1-27-2020'),
         per(id=2, station_id=10, start='13/30/00', end='19/00/00', day=1, day_week_year='1-27-2020'),
         per(id=1, station_id=10, start='09/30/00', end='13/00/00', day=1, day_week_year='1-28-2020'),
         per(id=2, station_id=10, start='13/30/00', end='19/00/00', day=1, day_week_year='1-28-2020')
    ]
    test_result = [
        ('opened', '09/30/00', '1-27-2020'),
        ('closed', '13/00/00', '1-27-2020'),
        ('opened', '13/30/00', '1-27-2020'),
        ('closed', '19/00/00', '1-27-2020'),
        ('opened', '09/30/00', '1-28-2020'),
        ('closed', '13/00/00', '1-28-2020'),
        ('opened', '13/30/00', '1-28-2020'),
        ('closed', '19/00/00', '1-28-2020')
    ]

    assert await make_point_line(test_data) == test_result

@pytest.mark.asyncio
async def test_make_intervals():
    test_data = [
        ('opened', '09/30/00', '1-27-2020'),
        ('closed', '13/00/00', '1-27-2020'),
        ('opened', '13/30/00', '1-27-2020'),
        ('closed', '19/00/00', '1-27-2020'),
        ('opened', '09/30/00', '1-28-2020'),
        ('closed', '13/00/00', '1-28-2020'),
        ('opened', '13/30/00', '1-28-2020'),
        ('closed', '19/00/00', '1-28-2020')
    ]
    test_result = [
        ('09/30/00', '13/00/00', 'closed', '1-27-2020'),
        ('13/00/00', '13/30/00', 'opened', '1-27-2020'),
        ('13/30/00', '19/00/00', 'closed', '1-27-2020'),
        ('19/00/00', '09/30/00', 'opened', '1-28-2020'),
        ('09/30/00', '13/00/00', 'closed', '1-28-2020'),
        ('13/00/00', '13/30/00', 'opened', '1-28-2020'),
        ('13/30/00', '19/00/00', 'closed', '1-28-2020'),
    ]

    assert await make_intervals(test_data) == test_result
