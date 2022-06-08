from __future__ import annotations

import os
import copy
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

    @staticmethod
    def process_input(input_str) -> Point:

        try:
            args = [int(arg) if idx == 0 else float(arg)
                    for idx, arg in enumerate(input_str.split(","))]

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

    """ def line_normal_point(self, line: Line | Axis) -> Point:
        Nalezeni bodu na linii odpovidajici kolmici k tomuto bodu

        Args:
            line (Line | Axis): linie na ktere se hleda kolmice

        Returns:
            Point: bod kolmice


        # nalezeni dvou nejblizsich bodu linie
        closest_points = [p[1] for p in line.find_closest_point(
            self, 2)]
        # serazeni podle ID
        closest_points.sort(key=lambda p: p.id)

        print("closest")
        print(closest_points)

        return closest_points

    def p2l_dist(self, line: Line | Axis) -> float:

        pass

    def p_axis_sta(self, axis: Axis) -> float:
        pass 
    """

    def get_point2line_info(self, line: Line | Axis) -> tuple(float, float):
        """_summary_

        Args:
            line (Line | Axis): _description_

        Returns:
            stationing      (float) : staniceni bodu na linii
            normal_distance (float) : orientovana velikost kolmice k bodu (+ vpravo || - vlevo)  
        """

        # nalezeni dvou nejblizsich bodu linie
        closest_points = [p[1] for p in line.find_closest_point(
            self, 2)]
        # serazeni podle ID
        closest_points.sort(key=lambda p: p.id)

        # urceni uhlu mezi vektory
        a_vec = Vector(closest_points[0], closest_points[1])  # primka z linie
        b_vec = Vector(closest_points[0], self)  # bod primky a tento bod
        fi = a_vec.angle(b_vec)

        #  vypocet informaci
        stationing = closest_points[0].sta + b_vec.d * math.cos(fi)
        normal_dist = -b_vec.d * math.sin(fi)

        return stationing, normal_dist

    def __str__(self) -> str:
        return f"{self.id},{self.x:.4f},{self.y:.4f},{self.z:.4f},{self.hmax:.4f},{self.hmin:.4f}"

    def __repr__(self) -> str:
        return f"Point__id__{self.id}"


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


class Vector:

    def __init__(self, start: Point, end: Point) -> None:

        self.dx: float = end.x - start.x
        self.dy: float = end.y - start.y
        self.d: float = math.sqrt(self.dx**2 + self.dy**2)

    def angle(self, vector: Vector) -> float:
        """ pravotocivy uhel mezi vektory
          X
          ^
          |   fi
          | \ 
        A *---------->B

        Args:
            self              : vyjadruje hlavni smer AB 
            vector_2 (Vector) : smer k bodu X

        Returns:
            angle (float) - uhel mezi vektory
        """

        _angle = math.acos((vector * self) / (vector.d * self.d))

        # urceni kvadrantu podle determinantu

        det = vector.dx * self.dy - vector.dy * self.dx

        return 2 * math.pi - _angle if det > 0 else _angle

    def __mul__(self, other: int | float | Vector):

        if isinstance(other, int):
            new_vector = copy.deepcopy(self)
            new_vector.dx *= other
            new_vector.dy *= other
            return new_vector

        elif isinstance(other, Vector):
            return self.dx * other.dx + self.dy * other.dy
        else:
            raise TypeError(
                "Vector muze by nasoben pouze temito typy [int,float,Vector]")

    __rmul__ = __mul__

    def __str__(self) -> str:
        return f"({self.dx:.3f},{self.dy:.4f})"


class Crosfall:
    """ asi nebude zatim potreba """
    pass


if __name__ == "__main__":

    # Testing
    """ 
    p = Point.process_input(
        "1,575504.78508,5022315.944132,203.217282,-0.15,0")

    p2 = Point.process_input(
        "2,575504.785568,5022315.964437,203.215959,-0.15,0")

    p3 = Point.process_input(
        "3,575504.786916,5022316.020465,203.212,-0.15,0")

    a = Axis(file_name="test_data/1_Axis_L.txt")

    v = Vector(p, p2)
    v2 = Vector(p, p3)

    print(p2.y - p.y)
    print(v)
    print(v * 3)
    print(v * v2)
    print(p.x)

    print(p.p2p_dist(p2))

    print(a._stat) """

    a = Point.process_input("1,0,0,203.217282,-0.15,0")
    b = Point.process_input("2,1,0,203.217282,-0.15,0")
    x = Point.process_input("3,0,-0.1,203.217282,-0.15,0")

    v_ab = Vector(a, b)
    v_ax = Vector(a, x)

    print(v_ab.angle(v_ax) * (180 / math.pi))
