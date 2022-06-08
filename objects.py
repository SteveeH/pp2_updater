from __future__ import annotations

import os
import math
from typing import List


class Point:
    """_summary_
    """

    def __init__(self, id: int = None, x: float = None, y: float = None, z: float = None, hmax: float = None, hmin: float = None):
        self.id = id
        self.x = x
        self.y = y
        self.z = z
        self.hmax = hmax
        self.hmin = hmin
        self.sta = 0
        self.axis_sta = 0

    @staticmethod
    def process_input(input_str) -> Point:

        try:
            # get of ID from string
            args = [float(arg) for arg in input_str.split(",")]

            if (pocet := len(args)) != 6:
                raise Exception(
                    f"Neplatny pocet vstupu :: {pocet} , musi jich byt 6")

            return Point(*args)

        except Exception as err:
            print(
                f"Retezec '{input_str}' neni validni vstup pro tridu Point.\n{err}")

    def p2p_dist(self, point: Point) -> float:
        """ point-to-point distance (horizontal)

        Args:
            point (Point)

        Returns:
            float: horizontalni vzdalenos
        """
        if not isinstance(point, Point):
            raise "Vzdalenost muze byt vypoctena poze mezi dvemi instancemi Point"
        return math.sqrt((point.x - self.x)**2 + (point.y - self.y)**2)

    def p2l_dist(self, line: Line | Axis) -> float:
        pass

    def p_axis_sta(self, axis: Axis) -> float:
        pass

    def __str__(self) -> str:
        return f"{self.x:.4f},{self.y:.4f},{self.z:.4f},{self.hmax:.4f},{self.hmin:.4f}"


class Line:

    def __init__(self, points: List[Point] = [], file_name: str = None) -> None:
        self.points = points
        self.file_name = file_name
        self._stat = (None, None)

        if self.file_name is not None:
            self._process_input()

    def _process_input(self) -> None:

        if not os.path.exists(self.file_name):
            raise FileNotFoundError

        self.points = []
        with open(self.file_name, "r") as file:
            for line in file.readlines():
                try:
                    self.points.append(Point.process_input(line))
                except Exception as err:
                    print(
                        f"Data :: '{line}' v souboru ::  '{self.file_name}' nemohli byt ulozeny jako Point.\n{err}")

    def calc_axis_sta(self, axis: Axis):
        """ Priradi k jednotlivym bodum linie staniceni vztazene k prilozene ose

        Args:
            axis (Axis)
        """
        pass

    def get_line_position(self, axis: Axis) -> int:
        """Pozice linie vuci ose:

        - -1  = linie je vlevo od osy

        -  0  = linie je totozna s osou nebo ma stejny pocet budu vlevo i vpravo

        -  1  = linie je vpravo od osy

        Args:
            axis (Axis)

        Returns:
            int: -1 | 0 | 1
        """
        pass

    def update_points(self):
        pass

    def find_closest_point(self, test_point: Point, count: int = 2) -> List[Point]:

        tmp_list = []
        # urceni vzdalenosti jednotlivych bodu linie -> [(12.11, Point), (13.22, Point), ...]
        for line_point in self.points:
            tmp_list.append((line_point.p2p_dist(test_point), line_point))

        # serazeni bodu
        tmp_list.sort(key=lambda tup: tup[0])

        return tmp_list[0:count]


class Axis(Line):

    def calc_axis_sta(self):
        if len(self.points) < 2:
            print("Linie nema dostatek bodu")
            return (None, None)

        for idx in range(1, len(self.points)):
            self.points[idx].sta = self.points[idx - 1].sta + \
                self.points[idx - 1].p2p_dist(self.points[idx])

        self._stat = (self.points[0].sta, self.points[-1].sta)
        return self._stat

    def _process_input(self) -> None:
        super()._process_input()
        self.calc_axis_sta()


class Crosfall:
    """ asi nebude zatim potreba """
    pass


if __name__ == "__main__":

    # Testing

    p = Point.process_input(
        "1,575504.78508,5022315.944132,203.217282,-0.15,0")

    p2 = Point.process_input(
        "2,575504.785568,5022315.964437,203.215959,-0.15,0")

    print(p.x)

    print(p.p2p_dist(p2))

    a = Axis(file_name="test_data\\1_Axis_L.txt")
    print(a._stat)

    closest = a.find_closest_point(p)
    print(closest)
