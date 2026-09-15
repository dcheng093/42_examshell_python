import contextlib
import importlib.util
import io
import runpy
import sys
from collections import Counter


def load_candidate(question, path):
    spec = importlib.util.spec_from_file_location(question, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(module)
    return module


def check(name, condition):
    if not condition:
        raise AssertionError(f"{name}: unexpected result")
    print(f"{name}: PASS")


def test_alternate_case(module):
    cases = [
        ("hello world", "HeLlO wOrLd"),
        ("42madrid", "42MaDrId"),
        ("", ""),
    ]
    for value, expected in cases:
        check("alternate_case", module.alternate_case(value) == expected)


def test_atoi(module):
    cases = [("42", 42), ("  -42abc", -42), ("+123", 123), ("abc", 0), ("", 0)]
    for value, expected in cases:
        check("atoi", module.atoi(value) == expected)


def test_brackets(module):
    cases = [
        ("()", True),
        ("([{}])", True),
        ("(]", False),
        ("([)", False),
        ("abc", True),
    ]
    for value, expected in cases:
        check("brackets", module.brackets(value) == expected)


def test_capitalize_words(module):
    cases = [
        ("hello world", "Hello World"),
        ("  multiple   spaces ", "  Multiple   Spaces "),
        ("mixed CASE letters", "Mixed Case Letters"),
    ]
    for value, expected in cases:
        check("capitalize_words", module.capitalize_words(value) == expected)


def test_convert_base(module):
    cases = [
        (("ff", 16, 2), "11111111"),
        (("10", 2, 10), "2"),
        (("z", 36, 10), "35"),
        (("1g", 16, 10), "ERROR"),
        (("10", 1, 10), "ERROR"),
    ]
    for args, expected in cases:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = module.convert_base(*args)
        check(
            "convert_base",
            output.getvalue().strip() == expected and result is None,
        )


def test_custom_sort(module):
    value = [3, 1, 2]
    result = module.custom_sort(value)
    check("customSortString", result == [1, 2, 3] and value == [3, 1, 2])


def test_merge_and_sort_desc(module):
    first, second = [10, 2], [3, 7, 2]
    result = module.merge_and_sort_desc(first, second)
    check(
        "merge_and_sort_desc",
        result == [10, 7, 3, 2, 2]
        and first == [10, 2]
        and second == [3, 7, 2],
    )


def test_mirror_matrix(module):
    value = [[1, 2, 3], [4, 5, 6]]
    result = module.mirror_matrix(value)
    check(
        "mirror_matrix",
        result == [[3, 2, 1], [6, 5, 4]]
        and value == [[1, 2, 3], [4, 5, 6]],
    )


def test_mirror_matrix_vertical(module):
    value = [[1, 2], [3, 4]]
    result = module.mirror_matrix_vertical(value)
    check(
        "mirror_matrix_vertical",
        result == [[3, 4], [1, 2]] and value == [[1, 2], [3, 4]],
    )


def test_py_echo_validator(module):
    cases = [
        ("Was it a car or a cat I saw?", True),
        ("tab a cat", False),
        ("", True),
    ]
    for value, expected in cases:
        check("py_echo_validator", module.py_echo_validator(value) == expected)


def test_py_pattern_tracker(module):
    cases = [("12a34", 2), ("1234", 3), ("a1b2c3", 0), ("98", 0)]
    for value, expected in cases:
        check("py_pattern_tracker", module.pattern_tracker(value) == expected)


def test_rotate_90(module):
    value = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    expected = [[7, 4, 1], [8, 5, 2], [9, 6, 3]]
    result = module.rotate_90(value)
    check(
        "rotate_90",
        result == expected and value == [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
    )


def test_sorted(path):
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        runpy.run_path(path, run_name="__main__")
    expected = [
        "['fig', 'kiwi', 'banana']",
        "[('Ana', 8.5), ('Luis', 6.0)]",
        "[('Marta', 18), ('Ana', 20), ('Luis', 20)]",
    ]
    check("sorted", output.getvalue().splitlines() == expected)


def test_top_k_frequent(module):
    result = module.topKFrequent([1, 2, 2, 3, 3, 3], 2)
    frequencies = Counter([1, 2, 2, 3, 3, 3])
    check("topKFrequent", set(result) == {2, 3} and len(result) == 2)
    check("topKFrequent", frequencies[result[0]] >= frequencies[result[1]])


def test_two_sum(module):
    check("twoSum", module.twoSum([2, 7, 11, 15], 9) == [0, 1])
    check("twoSum", module.twoSum([5, 5], 10) == [0, 1])
    check("twoSum", module.twoSum([1, 2], 8) == [])


def test_valid_anagram(module):
    cases = [
        ("racecar", "carrace", True),
        ("jar", "jam", False),
        ("", "", True),
    ]
    for first, second, expected in cases:
        check("valid_anagram", module.valid_anagram(first, second) == expected)


def test_whisper_lipher(module):
    cases = [
        ("Hello, World!", 3, "Khoor, Zruog!"),
        ("abc", 1, "bcd"),
        ("xyz", 2, "zab"),
        ("A1!", 26, "A1!"),
    ]
    for text, shift, expected in cases:
        check("whisper_lipher", module.whisper_lipher(text, shift) == expected)


TESTS = {
    "alternate_case": test_alternate_case,
    "atoi": test_atoi,
    "brackets": test_brackets,
    "capitalize_words": test_capitalize_words,
    "convert_base": test_convert_base,
    "customSortString": test_custom_sort,
    "merge_and_sort_desc": test_merge_and_sort_desc,
    "mirror_matrix": test_mirror_matrix,
    "mirror_matrix_vertical": test_mirror_matrix_vertical,
    "py_echo_validator": test_py_echo_validator,
    "py_pattern_tracker": test_py_pattern_tracker,
    "rotate_90": test_rotate_90,
    "sorted": test_sorted,
    "topKFrequent": test_top_k_frequent,
    "twoSum": test_two_sum,
    "valid_anagram": test_valid_anagram,
    "whisper_lipher": test_whisper_lipher,
}


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in TESTS:
        print("Usage: tester.py QUESTION CANDIDATE", file=sys.stderr)
        return 2
    question, path = sys.argv[1:]
    try:
        if question == "sorted":
            TESTS[question](path)
        else:
            TESTS[question](load_candidate(question, path))
    except (
        AssertionError,
        AttributeError,
        FileNotFoundError,
        TypeError,
        ValueError,
    ) as error:
        print(f"{question}: FAIL - {error}")
        return 1
    print(f"{question}: PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
