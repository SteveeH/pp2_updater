from __future__ import annotations


import math
from typing import List


class Point:
    """_summary_
    """

    def __init__(self, x: float = None, y: float = None, z: float = None, hmax: float = None, hmin: float = None):

        self.x = x
        self.y = y
        self.z = z
        self.hmax = hmax
        self.hmin = hmin
        self.sta = 0

    @staticmethod
    def process_input(input_str) -> Point:

        try:
            # get of ID from string
            args = [float(arg) for idx, arg in enumerate(
                input_str.split(",")) if idx != 0]

            if len(args) != 5:
                raise Exception("Invalid count of arguments, must be 5")

            return Point(*args)

        except Exception as err:
            print(
                f"String '{input_str}' isnt valid input for class Point.\n{err}")

    def p2p_dist(self, point: Point) -> float:
        """ point-to-point distance (horizontal)

        Args:
            point (Point)

        Returns:
            float: horizontal distance
        """
        if not isinstance(point, Point):
            raise "Distance can be calculated between two Point instances"
        return math.sqrt((point.x - self.x)**2 + (point.y - self.y)**2)

    def __str__(self) -> str:
        return f"{self.x:.4f},{self.y:.4f},{self.z:.4f},{self.hmax:.4f},{self.hmin:.4f}"


class Line:

    def __init__(self) -> None:
        self.points: List[Point] = []
        self._stat = (None, None)

    @property
    def stat(self):

        if self._stat[0] is None:
            self.calc_sta()

        return self._stat

    @stat.setter
    def stat(self, *args, **kwargs):

        print("Atribute stat cannot be set")

    def calc_sta(self):

        if len(self.points) <= 1:
            return (None, None)

        # calc attr

        for idx in enumerate(1, len(self.points)):
            self.points[idx].sta = self.points[idx - 1] + \
                self.points[idx - 1].p2p_dist(self.points[idx])

        return ()

    def update_points(self):
        pass


class Crosfall:
    pass


if __name__ == "__main__":

    p = Point.process_input(
        "1,575504.78508,5022315.944132,203.217282,-0.15,0,0")

    p2 = Point.process_input(
        "2,575504.785568,5022315.964437,203.215959,-0.15,0")

    print(p.x)
    print(p.y)
    print(p.z)
    print(p)

    print(p.p2p_dist(p2))
