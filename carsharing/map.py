import math

import requests
import polyline


R = 6378.137


def get_route(pickup_lon, pickup_lat, dropoff_lon, dropoff_lat):
    loc = "{},{};{},{}".format(pickup_lon, pickup_lat, dropoff_lon, dropoff_lat)
    url = "http://router.project-osrm.org/route/v1/driving/"
    r = requests.get(url + loc)
    if r.status_code != 200:
        return {}
    res = r.json()
    routes = polyline.decode(res['routes'][0]['geometry'])

    start_point = [res['waypoints'][0]['location'][1], res['waypoints'][0]['location'][0]]
    end_point = [res['waypoints'][1]['location'][1], res['waypoints'][1]['location'][0]]
    distance = res['routes'][0]['distance']

    out = {
        'route': routes,
        'start_point': start_point,
        'end_point': end_point,
        'distance': distance
    }

    return routes, out


def get_line(lat1, lon1, lat2, lon2):
    dLat = lat2 * math.pi / 180 - lat1 * math.pi / 180
    dLon = lon2 * math.pi / 180 - lon1 * math.pi / 180

    a = math.sin(dLat / 2) * math.sin(dLat / 2) + \
        math.cos(lat1 * math.pi / 180) * math.cos(lat2 * math.pi / 180) * \
        math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c * 1000


def is_too_far_away(routes, point_n) -> bool:
    for point1, point2 in zip(routes, routes[1:]):
        a = point_n[0] - point2[0]
        b = point_n[1] - point2[1]
        c = point2[0] - point1[0]
        d = point2[1] - point1[1]

        dot = a * c + b * d
        len_sq = c * c + d * d

        param = -1
        if len_sq != 0:
            param = dot / len_sq

        if param < 0:
            xx, yy = point1
        elif param > 1:
            xx, yy = point2
        else:
            xx, yy = point1[0] + param * c, point1[1] + param * d

        distance = get_line(*point_n, xx, yy)
        if distance < 10_000:
            return False
    return True

