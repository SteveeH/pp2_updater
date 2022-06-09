from __future__ import annotations

import os
import copy
import math

from datetime import datetime
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
        self.sta = None          # staniceni
        self.normal_dist = None  # kolma vzdalenost k linii
        self.cls_axis_id = None  # ID nejblizsiho bodu na ose

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

    def get_point2line_info(self, line: Line | Axis, previous_point: Point = None) -> tuple(float, float):
        """

        Args:
            line (Line | Axis): _description_

        Returns:
            stationing          (float) : staniceni bodu na linii
            normal_distance     (float) : orientovana velikost kolmice k bodu (+ vpravo || - vlevo)  
            line_closest_point_id (int) : ID nejblizsiho bodu linie
        """

        # nalezeni dvou nejblizsich bodu linie
        closest_points = [p[1] for p in line.find_closest_point(
            self, 2, previous_point.cls_axis_id if isinstance(previous_point, Point) else None)]
        # serazeni podle ID
        closest_points.sort(key=lambda p: p.id)

        # urceni uhlu mezi vektory
        a_vec = Vector(closest_points[0], closest_points[1])  # primka z linie
        b_vec = Vector(closest_points[0], self)  # bod primky a tento bod
        fi = a_vec.angle(b_vec)

        #  vypocet informaci
        line_closest_point_id = closest_points[0].id
        stationing = closest_points[0].sta + b_vec.d * math.cos(fi)
        normal_dist = -b_vec.d * math.sin(fi)

        return stationing, normal_dist, line_closest_point_id

    def __str__(self) -> str:
        return f"{self.id},{self.x:.4f},{self.y:.4f},{self.z:.4f},{self.hmax:.4f},{self.hmin:.4f}"

    def __repr__(self) -> str:
        return f"Point__id__{self.id}"


class Axis:

    def __init__(self, points: List[Point] = [], file_name: str = None) -> None:
        # nazev
        self.id = None
        self.type = None
        self.obj = None
        self.position = 0
        #
        self.points = points
        self.file_name = file_name
        self._sta = (None, None)

        if self.file_name is not None:
            self._process_input()

        self.calc_axis_sta()

    def _process_input(self) -> None:

        if not os.path.exists(self.file_name):
            raise FileNotFoundError

        self.get_name_data()

        self.points = []
        with open(self.file_name, "r") as file:
            for line in file.readlines():
                try:
                    p = Point.process_input(line)
                    p.cls_axis_id = p.id
                    p.normal_dist = 0.0
                    self.points.append(p)
                except Exception as err:
                    print(
                        f"Data :: '{line}' v souboru ::  '{self.file_name}' nemohli byt ulozeny jako Point.\n{err}")

    def get_name_data(self) -> None:

        _, name = os.path.split(self.file_name)

        self.id, self.type, self.obj = (name.split(".")[0]).split("_")

    def calc_axis_sta(self) -> None:

        if len(self.points) < 2:
            print("Linie nema dostatek bodu")
            return (None, None)

        self.points[0].sta = 0

        for idx in range(1, len(self.points)):
            self.points[idx].sta = self.points[idx - 1].sta + \
                self.points[idx - 1].p2p_dist(self.points[idx])

        self._sta = (self.points[0].sta, self.points[-1].sta)

    def find_closest_point(self, test_point: Point, instance_count: int = 2, cls_id_next_point: int = None, id_area: int = 5) -> List[Point]:
        """Nalezeni nejblizsich vrcholu linie k zadanemu bodu

        Args:
            test_point (Point): Testovany bod
            instance_count (int, optional): Pocet hledanych vrcholu. Defaultne 2.

        Returns:
            List[(float,Point), ...]: Nejblizsi vrcholy serazene podle vzdalenosti
        """

        tmp_list = []

        # urceni vyhledavaciho okna
        idx_start = 0
        idx_end = -1

        if cls_id_next_point is not None:

            ts = cls_id_next_point - id_area
            te = cls_id_next_point + id_area

            idx_start = ts if ts > 0 else 0
            idx_end = te if te < len(self.points) else -1

        for line_point in self.points[idx_start:idx_end]:
            tmp_list.append((line_point.p2p_dist(test_point), line_point))

        # serazeni bodu podle vzdalenosti
        tmp_list.sort(key=lambda tup: tup[0])

        return tmp_list[0:instance_count]

    def __repr__(self) -> str:
        return f"{self.id}_{self.type.capitalize()}::({self._sta[0]:.3f},{self._sta[1]:.3f}) -- {'><' if self.position == 0 else ('vlevo' if self.position < 0 else 'vpravo' ) }"


class Line(Axis):

    def __init__(self, axis: Axis, points: List[Point] = [], file_name: str = None) -> None:
        self.axis = axis
        super().__init__(points, file_name)

    def calc_axis_sta(self):

        position = 0

        for idx, line_point in enumerate(self.points):

            sta, normal_dist, cls_axis_id = line_point.get_point2line_info(
                self.axis, None if idx == 0 else self.points[idx - 1])

            line_point.sta = sta
            line_point.normal_dist = normal_dist
            line_point.cls_axis_id = cls_axis_id

            if normal_dist > 0:
                position += 1
            elif normal_dist < 0:
                position -= 1
            else:
                # bod primo na ose
                pass

        self.position = position
        self._sta = (self.points[0].sta, self.points[-1].sta)


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

        if isinstance(other, (int, float)):
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

    start_time = datetime.utcnow()

    folder_path = "test_data"

    files = [os.path.join(folder_path, f)
             for f in os.listdir(path=folder_path)]

    f_axis = [f for f in files if "Axis" in f][0]

    lines = []

    axis = Axis(file_name=f_axis)

    for line_file in [f for f in files if ("Axis" not in f and "Crossfall" not in f)]:
        lines.append(Line(axis, file_name=line_file))

    print(files)
    print(f_axis)
    print(lines)

    """
    # Testing

    p = Point.process_input(
        "1,575504.78508,5022315.944132,203.217282,-0.15,0")

    p2 = Point.process_input(
        "2,575504.785568,5022315.964437,203.215959,-0.15,0")

    p3 = Point.process_input(
        "3,575504.786916,5022316.020465,203.212,-0.15,0")

    a = Axis(file_name="test_data/1_Axis_L.txt")



    l = Line(a, file_name="test_data/2_Fix_L.txt")
    l = Line(a, file_name="test_data/2_Fix_L.txt")

    print(repr(a))
    print(repr(l))
    v = Vector(p, p2)
    v2 = Vector(p, p3)

    print(p2.y - p.y)
    print(v)
    print(v * 3)
    print(v * v2)
    print(p.x)

    print(p.p2p_dist(p2))

    print(a._sta)

    a = Point.process_input("1,0,0,203.217282,-0.15,0")
    b = Point.process_input("2,1,0,203.217282,-0.15,0")
    x = Point.process_input("3,0,-0.1,203.217282,-0.15,0")

    v_ab = Vector(a, b)
    v_ax = Vector(a, x)

    print(v_ab.angle(v_ax) * (180 / math.pi)) """

    end_time = datetime.utcnow()

    print(f"Vypocet trval {(end_time-start_time).total_seconds():.1f} vterin")
