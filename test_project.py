from project import get_file, Fibonacci_numbers_generator, locator
from pytest import raises
import sys


def test_get_file_invalid_extension(monkeypatch):
    test_args = ["program_name", "-f", "data.txt", "-c", "Score", "-v", "87", "-t", "int"]
    monkeypatch.setattr(sys, "argv", test_args)
    with raises(ValueError, match=r'Filename must have an extension'):
        get_file()


def test_Fibonacci_numbers_generator():
    assert Fibonacci_numbers_generator(5) == [0, 1, 1, 2, 3, 5]
    assert Fibonacci_numbers_generator(12) == [0, 1, 1, 2, 3, 5, 8, 13]


def test_locator():
    assert locator(['sample_data.csv', 'Score', 'float', '83.89']) == 0
