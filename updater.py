from msilib.schema import Error
import os
from typing import List
from objects import Axis, Line, Crosfall

from inquirer import inq_get_range, inq_get_depths, delete_last_lines, inq_line_selection


class Updater:

    def __init__(self, pp2_line_dir: str) -> None:

        self.axis: Axis = None
        self.crossfall: Crosfall = None
        self.lines: List[Line] = []

        if not os.path.exists(pp2_line_dir) or not os.path.isdir(pp2_line_dir):
            raise FileNotFoundError(
                f"Zadana cesta {pp2_line_dir} neexistuje nebo se nejdna o slozku")

        self.project_dir: str = pp2_line_dir

        self.run()

    def load_project(self) -> None:

        all_files = [os.path.join(self.project_dir, f)
                     for f in os.listdir(path=self.project_dir)]

        # rozrazeni souboru podle jednotlivych typu
        f_sort = {
            "axis": [],
            "line": [],
            "crossfall": [],
            "unknown": [],
        }

        for file in all_files:
            f_sort[self.file_sort(file)].append(file)

        if len(f_sort["axis"]) != 1 or len(f_sort["crossfall"]) != 1:
            raise Exception(
                "Ve slozce muze byt pouze jedna osa a jeden crossfall")

        # nacteni dat ze souboru
        self.axis = Axis(file_name=f_sort["axis"][0])
        self.crossfall = Crosfall(file_name=f_sort["crossfall"][0])

        for line_file in f_sort["line"]:
            self.lines.append(Line(self.axis, file_name=line_file))

    def run(self) -> None:
        user_input = ""
        self.load_project()

        while user_input.capitalize() not in ["N", "NO"]:
            self.process_data()
            user_input = input(
                "Chcete pokracovat zadani dalsi oblasti: [y/n] : ")

        self.save_changed_lines()

    def process_data(self) -> None:

        user_input = ""
        # nalezeni lini v oblasti zadane uzivatelem
        user_range = inq_get_range()
        lines_in_range = self.find_lines_in_range(user_range)
        delete_last_lines(2)

        if len(lines_in_range) == 0:
            print("Rozsahu neodpovidaji zadne linie")

        while user_input.capitalize() not in ["N", "NO"] and len(lines_in_range) > 0:

            selected_index = inq_line_selection(lines_in_range)
            selected_line = lines_in_range.pop(selected_index)
            # ziskani novych hlobek
            hmax, hmin = inq_get_depths(user_range)

            # nastaveni novych hloubek
            selected_line.change_point_data(user_range, hmax, hmin)

            user_input = input(
                "Chcete vybrat dalsi lini: [y/n] : ")
            delete_last_lines(2)

    def find_lines_in_range(self, _range: tuple) -> List[Line]:

        return [line for line in self.lines if line.has_point_range(_range)]

    def save_changed_lines(self):

        print("Linie ktere byly upraveny:")

        for changed_line in [l for l in self.lines if l.is_changed]:
            print(repr(changed_line))
            changed_line.save()

    @staticmethod
    def file_sort(file_path) -> str:
        _, file = os.path.split(file_path)
        file_n, extension = os.path.splitext(file)
        file_n_split = file_n.split("_")

        if extension != ".txt":
            return "unknown"

        if len(file_n_split) == 3 and any([w in file_n for w in ["Fix", "Free"]]):
            return "line"
        elif len(file_n_split) == 3 and "Axis" in file_n:
            return "axis"
        elif len(file_n_split) == 2 and "Crossfall" in file_n:
            return "crossfall"
        else:
            return "unknown"
