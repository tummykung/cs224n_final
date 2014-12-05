import json
import random

def latLng(latCenter, lngCenter, size):
    """random latitude and longitude near SF"""
    latitude = random.gauss(latCenter, size)
    longitude = random.gauss(lngCenter, size)
    return (latitude, longitude)

def sentics(e1Center, e2Center, e3Center, e4Center, random_func):
    """random sentics"""
    sentic = lambda x: max(-1, min(1, random_func(x, 0.3)))
    return (sentic(e1Center), sentic(e2Center), sentic(e3Center), sentic(e4Center))


def genRegion(latCenter, lngCenter, size, e1Center, e2Center, e3Center, e4Center):
    points = []
    for i in range(2000):
        (lat, lng) = latLng(latCenter, lngCenter, size)
        (e1, e2, e3, e4) = sentics(e1Center, e2Center, e3Center, e4Center, random.gauss)
        points.append({"lat": lat, "lng": lng,
                       "pleasantness": e1,
                       "aptitude": e2,
                       "attention": e3,
                       "sensitivity": e4})
    return points

mission = genRegion(37.761044, -122.413831, 0.005, 0.0, 0.4, 1.0, 0.0)
tumsHouse = genRegion(37.755125, -122.424324, 0.0005, 1.0, 0.0, -0.5, 0.0)
soma = genRegion(37.778211, -122.409968, 0.5, 0.002, 0.5, 0.0, -0.2)
nobHill = genRegion(37.789540, -122.418637, 0.003, 0.0, 1.0, -0.3, 0.1)
goldenGatePark = genRegion(37.768781, -122.487473, 0.01, 0.0, 0.5, 0.2, 0.1)


tumsPaloAltoHouse = genRegion(37.426098, -122.157878, 0.0005, 1.0, 0.0, -0.5, 0.0)

print json.dumps(mission + tumsHouse + soma + nobHill + goldenGatePark)
