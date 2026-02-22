"""
Geofence and route deviation utilities.

This module implements simple geometric checks to determine whether a
given GPS coordinate lies inside a polygonal geofence and whether it
deviates significantly from a defined patrol route. These functions
use basic algorithms suited to demonstration purposes; for production
use a geospatial library (e.g. Shapely or GeoPandas) is recommended.
"""

from typing import List, Tuple


def point_in_polygon(point: Tuple[float, float], polygon: List[Tuple[float, float]]) -> bool:
    """Return True if a point lies within a polygon using ray casting."""
    x, y = point
    inside = False
    n = len(polygon)
    if n < 3:
        return False
    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if min(p1y, p2y) < y <= max(p1y, p2y) and x <= max(p1x, p2x):
            if p1y != p2y:
                xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
            if p1x == p2x or x <= xinters:
                inside = not inside
        p1x, p1y = p2x, p2y
    return inside


def is_on_route(
    point: Tuple[float, float], route: List[Tuple[float, float]], threshold: float = 0.0005
) -> bool:
    """Return True if the point is within a threshold of any point on the route.

    This simplistic implementation measures absolute differences on
    latitude and longitude axes separately. A production system should
    compute geodesic distances.

    Args:
        point: (lat, lon) tuple for current location.
        route: List of (lat, lon) tuples representing planned path.
        threshold: Acceptable deviation in degrees.
    """
    px, py = point
    for rx, ry in route:
        if abs(px - rx) <= threshold and abs(py - ry) <= threshold:
            return True
    return False