import sys

from objects import Line
from PyInquirer import prompt
from typing import Tuple, List
from examples import custom_style_2
from prompt_toolkit.validation import Validator, ValidationError


def delete_last_lines(n=1):
    CURSOR_UP_ONE = '\x1b[1A'
    ERASE_LINE = '\x1b[2K'

    sys.stdout.write((CURSOR_UP_ONE + ERASE_LINE) * n)


class NumberValidator(Validator):

    def validate(self, document):
        try:
            int(document.text)
        except ValueError:
            raise ValidationError(message="Prosim zadej cislo",
                                  cursor_position=len(document.text))


class RangeValidator(Validator):

    def validate(self, document):
        try:
            _min, _max = get_range_data(document.text)

            if _min >= _max:
                raise ValidationError(message="Staniceni zacatku musi byt mensi nez konce",
                                      cursor_position=len(document.text))

        except (ValueError, IndexError):
            raise ValidationError(message="Prosim zadej rozsah ve spravnem formatu",

                                  cursor_position=len(document.text))


class DepthsValidator(Validator):

    def validate(self, document):
        try:
            _max, _min = get_depths_data(document.text)

            if _min > 0 or _max > 0:
                raise ValidationError(message="Hloubky musi byt zaporne nebo rovne 0",
                                      cursor_position=len(document.text))

            if abs(_min) >= abs(_max):
                raise ValidationError(message="Maximalni hlobka musi byt vetsi nez minimalni",
                                      cursor_position=len(document.text))

        except (ValueError, IndexError):
            raise ValidationError(message="Prosim zadej hlobky ve spravnem formatu",
                                  cursor_position=len(document.text))


def get_range_data(input_text: str):
    # range format :  float-float

    split_data = input_text.split("-")

    return float(split_data[0]), float(split_data[1])


def inq_get_range() -> Tuple[float, float]:

    answ = prompt({
        'type': "input",
        "name": "stn_range",
        "message": "Zadej staniceni na kterem chces upravit lini.\n Ve formatu zacatek-konec (např. 55.43-101.22) : ",
        "validate": RangeValidator,
    }, style=custom_style_2)

    return get_range_data(answ["stn_range"])


def inq_line_selection(lines_in_range: List[Line]) -> int:

    answ = prompt({
        'type': "list",
        "name": "line_name",
        "message": "Vyberte linii kterou chcete upravit : ",
        "choices": [repr(_l) for _l in lines_in_range]
    }, style=custom_style_2)

    for idx, _l in enumerate(lines_in_range):
        if repr(_l) == answ["line_name"]:
            return idx


def get_depths_data(input_text: str):
    # range format :  float-float

    split_data = input_text.split(",")

    return float(split_data[0]), float(split_data[1])


def inq_get_depths(_range: tuple) -> Tuple[float, float]:

    answ = prompt({
        'type': "input",
        "name": "depths_data",
        "message": f"Zadej nove hloubky pro zadany usek ({_range[0]}-{_range[1]}) ve formatu <max_h>,<min_h> (např. -0.12,-0.01) : ",
        "validate": DepthsValidator,
    }, style=custom_style_2)

    return get_depths_data(answ["depths_data"])
