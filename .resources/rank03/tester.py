import contextlib
import importlib.util
import io
import runpy
import inspect
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


test_number = 0


def check(description, result, expected=None, errors=None):
    global test_number
    test_number += 1

    if expected is None:
        passed = result
    else:
        passed = result == expected

    if passed:
        print(f"test {test_number} || {description}: PASS")
    else:
        print(f"test {test_number} || {description}: FAIL")
        print(f"       || got:      {result!r}")
        print(f"       || expected: {expected!r}")

        if errors:
            for error in errors:
                print(f"       {error}")

        raise SystemExit(1)


def test_alternate_case(module):
    cases = [
        # basic words
        ("hello", "HeLlO"),
        ("world", "WoRlD"),
        ("python", "PyThOn"),
        ("testing", "TeStInG"),
        ("computer", "CoMpUtEr"),
        ("programming", "PrOgRaMmInG"),
        ("abcdef", "AbCdEf"),
        ("abcdefgh", "AbCdEfGh"),
        ("abcdefghi", "AbCdEfGhI"),
        ("abcdefghij", "AbCdEfGhIj"),

        # multiple words
        ("hello world", "HeLlO wOrLd"),
        ("hello python", "HeLlO pYtHoN"),
        ("good morning", "GoOd MoRnInG"),
        ("good night", "GoOd NiGhT"),
        ("test case", "TeSt CaSe"),
        ("alternate case", "AlTeRnAtE cAsE"),
        ("hello there friend", "HeLlO tHeRe FrIeNd"),
        ("this is a test", "ThIs Is A tEsT"),
        ("python is fun", "PyThOn Is FuN"),
        ("i love coding", "I lOvE cOdInG"),

        # empty and whitespace
        ("", ""),
        (" ", " "),
        ("  ", "  "),
        ("   ", "   "),
        ("hello ", "HeLlO "),
        (" hello", " HeLlO"),
        (" hello ", " HeLlO "),
        ("hello  world", "HeLlO  wOrLd"),
        ("hello   world", "HeLlO   wOrLd"),
        ("  hello  world  ", "  HeLlO  wOrLd  "),

        # lowercase input
        ("a", "A"),
        ("ab", "Ab"),
        ("abc", "AbC"),
        ("abcd", "AbCd"),
        ("abcde", "AbCdE"),
        ("abcdef", "AbCdEf"),
        ("abcdefgh", "AbCdEfGh"),
        ("aaaaaaaa", "AaAaAaAa"),
        ("bbbbbbbb", "BbBbBbBb"),
        ("helloworld", "HeLlOwOrLd"),

        # uppercase input
        ("A", "A"),
        ("AB", "Ab"),
        ("ABC", "AbC"),
        ("ABCD", "AbCd"),
        ("ABCDE", "AbCdE"),
        ("ABCDEF", "AbCdEf"),
        ("ABCDEFGH", "AbCdEfGh"),
        ("AAAAAAAA", "AaAaAaAa"),
        ("BBBBBBBB", "BbBbBbBb"),
        ("HELLOWORLD", "HeLlOwOrLd"),

        # mixed input case
        ("hElLo", "HeLlO"),
        ("HeLLo", "HeLlO"),
        ("HELlo", "HeLlO"),
        ("hELLO", "HeLlO"),
        ("PyThOn", "PyThOn"),
        ("PYTHON", "PyThOn"),
        ("python", "PyThOn"),
        ("pYtHoN", "PyThOn"),
        ("TeStInG", "TeStInG"),
        ("tEsTiNg", "TeStInG"),

        # numbers
        ("123", "123"),
        ("12345", "12345"),
        ("1hello", "1HeLlO"),
        ("2world", "2WoRlD"),
        ("42madrid", "42MaDrId"),
        ("123abc", "123AbC"),
        ("abc123", "AbC123"),
        ("1a2b3c", "1A2b3C"),
        ("hello123", "HeLlO123"),
        ("123hello", "123HeLlO"),

        # numbers between letters
        ("hello123world", "HeLlO123wOrLd"),
        ("abc123def", "AbC123dEf"),
        ("12hello34", "12HeLlO34"),
        ("test123case", "TeSt123CaSe"),
        ("123test456", "123TeSt456"),

        # punctuation
        ("hello!", "HeLlO!"),
        ("hello?", "HeLlO?"),
        ("hello.", "HeLlO."),
        ("hello,", "HeLlO,"),
        ("hello-world", "HeLlO-wOrLd"),
        ("hello_world", "HeLlO_wOrLd"),
        ("hello.world", "HeLlO.wOrLd"),
        ("hello/world", "HeLlO/wOrLd"),
        ("hello@world", "HeLlO@wOrLd"),
        ("hello#world", "HeLlO#wOrLd"),

        # punctuation between letters
        ("a!b?c", "A!b?C"),
        ("a-b-c", "A-b-C"),
        ("a_b_c", "A_b_C"),
        ("a.b.c", "A.b.C"),
        ("a/b/c", "A/b/C"),
        ("a+b+c", "A+b+C"),
        ("a=b=c", "A=b=C"),
        ("a:b:c", "A:b:C"),
        ("a;b;c", "A;b;C"),
        ("a,b,c", "A,b,C"),

        # punctuation at beginning/end
        ("!hello", "!HeLlO"),
        ("?hello", "?HeLlO"),
        (".hello", ".HeLlO"),
        ("hello!", "HeLlO!"),
        ("hello?", "HeLlO?"),
        ("!hello!", "!HeLlO!"),
        ("?hello?", "?HeLlO?"),
        ("...hello...", "...HeLlO..."),
        ("---hello---", "---HeLlO---"),
        ("***hello***", "***HeLlO***"),

        # numbers + punctuation
        ("1a2b3c", "1A2b3C"),
        ("1-a-2-b-3-c", "1-A-2-b-3-C"),
        ("42madrid!", "42MaDrId!"),
        ("python3.9 rocks!", "PyThOn3.9 RoCkS!"),
        ("123!abc?456", "123!AbC?456"),
        ("a1!b2?c3", "A1!b2?C3"),
        ("99 bottles", "99 BoTtLeS"),
        ("3blindmice", "3BlInDmIcE"),
        ("version2test", "VeRsIoN2tEsT"),
        ("test123test456test", "TeSt123TeSt456TeSt"),

        # no alphabetic characters
        ("1234567890", "1234567890"),
        ("!@#$%^&*()", "!@#$%^&*()"),
        ("123!@#456", "123!@#456"),
        ("---___---", "---___---"),
        ("...,,,!!!", "...,,,!!!"),

        # longer examples
        (
            "thequickbrownfox",
            "ThEqUiCkBrOwNfOx",
        ),
        (
            "the quick brown fox",
            "ThE qUiCk BrOwN fOx",
        ),
        (
            "abcdefghijklmnopqrstuvwxyz",
            "AbCdEfGhIjKlMnOpQrStUvWxYz",
        ),
        (
            "hello world this is python",
            "HeLlO wOrLd ThIs Is PyThOn",
        ),
        (
            "this is a very long test string",
            "ThIs Is A vErY lOnG tEsT sTrInG",
        ),
        (
            "abcdefghijklmnopqrstuvwxyz 123",
            "AbCdEfGhIjKlMnOpQrStUvWxYz 123",
        ),
        (
            "1234567890abcdefghijklmnopqrstuvwxyz",
            "1234567890AbCdEfGhIjKlMnOpQrStUvWxYz",
        ),
        (
            "hello123world456test789",
            "HeLlO123wOrLd456TeSt789",
        ),
        (
            "a1b2c3d4e5f6",
            "A1b2C3d4E5f6",
        ),
        (
            "Python3.9 is Great!",
            "PyThOn3.9 Is GrEaT!",
        ),
    ]

    for value, expected in cases:
        result = module.alternate_case(value)
        check(
            f"alternate_case({value!r})",
            result,
            expected
        )


def test_atoi(module):
    cases = [
        # basic numbers
        ("0", 0),
        ("1", 1),
        ("2", 2),
        ("9", 9),
        ("10", 10),
        ("42", 42),
        ("123", 123),
        ("999", 999),
        ("1000", 1000),
        ("12345", 12345),

        # positive sign
        ("+0", 0),
        ("+1", 1),
        ("+9", 9),
        ("+10", 10),
        ("+42", 42),
        ("+123", 123),
        ("+999", 999),
        ("+1000", 1000),
        ("+12345", 12345),
        ("+00042", 42),

        # negative numbers
        ("-0", 0),
        ("-1", -1),
        ("-9", -9),
        ("-10", -10),
        ("-42", -42),
        ("-123", -123),
        ("-999", -999),
        ("-1000", -1000),
        ("-12345", -12345),
        ("-00042", -42),

        # leading whitespace
        (" 0", 0),
        (" 1", 1),
        (" 42", 42),
        ("   123", 123),
        ("     999", 999),
        ("\t42", 42),
        ("\n42", 42),
        ("\t 42", 42),
        (" \t 123", 123),
        ("\n\t -42", -42),

        # whitespace + positive sign
        (" +1", 1),
        (" +42", 42),
        ("   +123", 123),
        ("\t+99", 99),
        (" \t+500", 500),
        ("   +00042", 42),
        ("\n+123", 123),
        ("\t +7", 7),
        (" \t +88", 88),
        ("    +9999", 9999),

        # whitespace + negative sign
        (" -1", -1),
        (" -42", -42),
        ("   -123", -123),
        ("\t-99", -99),
        (" \t-500", -500),
        ("   -00042", -42),
        ("\n-123", -123),
        ("\t -7", -7),
        (" \t -88", -88),
        ("    -9999", -9999),

        # stop at letters
        ("42abc", 42),
        ("123abc", 123),
        ("999xyz", 999),
        ("123hello", 123),
        ("-42abc", -42),
        ("+42abc", 42),
        ("  -42abc", -42),
        ("  +123xyz", 123),
        ("123abc456", 123),
        ("-123abc456", -123),

        # stop at punctuation
        ("42!", 42),
        ("123.", 123),
        ("123.45", 123),
        ("99,999", 99),
        ("42-10", 42),
        ("42+10", 42),
        ("123/456", 123),
        ("999#test", 999),
        ("100@home", 100),
        ("77$money", 77),

        # invalid / no digits
        ("", 0),
        ("abc", 0),
        ("hello", 0),
        ("+", 0),
        ("-", 0),
        ("+abc", 0),
        ("-abc", 0),
        ("   ", 0),
        ("\t", 0),
        ("\n", 0),

        # sign followed by whitespace
        ("+ 42", 0),
        ("- 42", 0),
        (" + 42", 0),
        (" - 42", 0),
        ("   +  42", 0),
        ("   -  42", 0),
        ("+\t42", 0),
        ("-\t42", 0),
        ("+ 123abc", 0),
        ("- 123abc", 0),

        # leading zeros
        ("00", 0),
        ("000", 0),
        ("0001", 1),
        ("00042", 42),
        ("00123", 123),
        ("000999", 999),
        ("-0001", -1),
        ("-00042", -42),
        ("+000123", 123),
        ("000000100", 100),

        # very large values
        ("123456789", 123456789),
        ("987654321", 987654321),
        ("1234567890", 1234567890),
        ("9999999999", 9999999999),
        ("-123456789", -123456789),
        ("-987654321", -987654321),
        ("-1234567890", -1234567890),
        ("999999999999", 999999999999),
        ("-999999999999", -999999999999),
        ("123456789012345", 123456789012345),

        # digits followed by whitespace
        ("42 ", 42),
        ("123  ", 123),
        ("999\t", 999),
        ("123\n", 123),
        ("-42 ", -42),
        ("+123 ", 123),
        ("42 abc", 42),
        ("123 hello", 123),
        ("-999 xyz", -999),
        ("+777 test", 777),
    ]

    for value, expected in cases:
        result = module.atoi(value)
        check(
            f"atoi({value!r})",
            result,
            expected
        )


def test_brackets(module):
    cases = [
        # basic valid
        ("", True),
        ("()", True),
        ("[]", True),
        ("{}", True),
        ("abc", True),
        ("123", True),
        ("hello world", True),
        ("a(b)c", True),
        ("a[b]c", True),
        ("a{b}c", True),

        # basic invalid
        ("(", False),
        (")", False),
        ("[", False),
        ("]", False),
        ("{", False),
        ("}", False),
        (")(", False),
        ("][", False),
        ("}{", False),
        ("([)", False),

        # simple matching
        ("()[]{}", True),
        ("[](){}", True),
        ("{}[]()", True),
        ("(){}", True),
        ("[]{}", True),
        ("{}()", True),
        ("()[]", True),
        ("[]()", True),
        ("{}[]", True),
        ("({})", True),

        # nested brackets
        ("(())", True),
        ("[[]]", True),
        ("{{}}", True),
        ("((()))", True),
        ("[[[]]]", True),
        ("{{{}}}", True),
        ("(([]))", True),
        ("[({})]", True),
        ("{[()]}", True),
        ("({[]})", True),

        # deep nesting
        ("(((())))", True),
        ("[[[[]]]]", True),
        ("{{{{}}}}", True),
        ("([({})])", True),
        ("{[({[]})]}", True),
        ("((([[]])))", True),
        ("[[({})]]", True),
        ("{{[()]}}", True),
        ("([{()}])", True),
        ("{({[]})}", True),

        # wrong bracket types
        ("(]", False),
        ("[)", False),
        ("{)", False),
        ("(}", False),
        ("[}", False),
        ("{]", False),
        ("([)]", False),
        ("[(])", False),
        ("{[}]", False),
        ("{(])}", False),

        # extra closing brackets
        (")()", False),
        ("())", False),
        ("())()", False),
        ("][]", False),
        ("[]]", False),
        ("}{}", False),
        ("{}}", False),
        ("abc)", False),
        ("abc]", False),
        ("abc}", False),

        # extra opening brackets
        ("(()", False),
        ("[[]", False),
        ("{{}", False),
        ("((())", False),
        ("[[[]]", False),
        ("{{{}}", False),
        ("abc(", False),
        ("abc[", False),
        ("abc{", False),
        ("hello(world", False),

        # text inside brackets
        ("(abc)", True),
        ("[abc]", True),
        ("{abc}", True),
        ("(hello world)", True),
        ("[hello world]", True),
        ("{hello world}", True),
        ("(a[b]c)", True),
        ("[a{b}c]", True),
        ("{a(b)c}", True),
        ("a(b[c]d)e", True),

        # numbers and symbols
        ("(123)", True),
        ("[123]", True),
        ("{123}", True),
        ("(1[2]3)", True),
        ("[1{2}3]", True),
        ("{1(2)3}", True),
        ("abc{123[xyz]}", True),
        ("abc{[123(xyz)]}", True),
        ("[{adaudna}]", True),
        ("[{adaudna}])", False),

        # spaces and newlines
        ("( )", True),
        ("[ ]", True),
        ("{ }", True),
        ("( [ ] )", True),
        ("{ [ ( ) ] }", True),
        ("hello ( world )", True),
        ("hello [ world ]", True),
        ("hello { world }", True),
        ("(hello [world] test)", True),
        ("( hello [ world ]", False),

        # mixed valid
        ("a(b[c]d)e", True),
        ("a{b[c(d)e]f}g", True),
        ("x(y[z{abc}])", True),
        ("[{()}]", True),
        ("{[()]}", True),
        ("([{}])", True),
        ("{[()()]}", True),
        ("((a)[b]{c})", True),
        ("a(b)c[d]e{f}", True),
        ("abc{[123(xyz)]}", True),

        # mixed invalid
        ("a(b[c)d]e", False),
        ("a{b[c}d]e", False),
        ("x(y[z})]", False),
        ("[{()}]", True),
        ("{[(])}", False),
        ("([{}]", False),
        ("[{}))", False),
        ("{{[()]}", False),
        ("abc{[123(xyz]}]", False),
        ("[{adaudna}])", False),

        # more edge cases
        ("((((()))))", True),
        ("[[[[[]]]]]", True),
        ("{{{{{}}}}}", True),
        ("()()()()()", True),
        ("[][][][][]", True),
        ("{}{}{}{}{}", True),
        ("([{}])([{}])", True),
        ("(([]){})", True),
        ("{([][])}", True),
        ("([[[{{{}}}]]])", True),
    ]

    for value, expected in cases:
        result = module.brackets(value)
        check(
            f"brackets({value!r})",
            result,
            expected
        )


def test_capitalize_words(module):
    cases = [
        # basic
        ("hello", "Hello"),
        ("world", "World"),
        ("hello world", "Hello World"),
        ("good morning", "Good Morning"),
        ("hello python", "Hello Python"),
        ("this is a test", "This Is A Test"),
        ("one two three", "One Two Three"),
        ("python programming language", "Python Programming Language"),
        ("capitalize every word", "Capitalize Every Word"),
        ("hello world today", "Hello World Today"),

        # mixed case
        ("HELLO", "Hello"),
        ("WORLD", "World"),
        ("hELLO", "Hello"),
        ("HeLLo", "Hello"),
        ("HELLo WoRLD", "Hello World"),
        ("mIXED case", "Mixed Case"),
        ("PyThOn PrOgRaMmInG", "Python Programming"),
        ("tEST case", "Test Case"),
        ("aBcDeF", "Abcdef"),
        ("ABC DEF GHI", "Abc Def Ghi"),

        # multiple spaces
        ("  hello", "  Hello"),
        ("hello  world", "Hello  World"),
        ("hello   world", "Hello   World"),
        ("hello    world", "Hello    World"),
        ("  hello world", "  Hello World"),
        ("hello world  ", "Hello World  "),
        ("  hello world  ", "  Hello World  "),
        ("  multiple   spaces ", "  Multiple   Spaces "),
        ("hello    beautiful    world", "Hello    Beautiful    World"),
        ("   hello   world   test   ", "   Hello   World   Test   "),

        # empty and spaces
        ("", ""),
        (" ", " "),
        ("  ", "  "),
        ("   ", "   "),
        ("    hello    ", "    Hello    "),
        ("\t", "\t"),
        ("\n", "\n"),

        # single-letter words
        ("a", "A"),
        ("i", "I"),
        ("a b", "A B"),
        ("a b c", "A B C"),
        ("x y z", "X Y Z"),
        ("A B C", "A B C"),
        ("i am here", "I Am Here"),
        ("a simple test", "A Simple Test"),
        ("x marks spot", "X Marks Spot"),
        ("i love python", "I Love Python"),

        # numbers
        ("42", "42"),
        ("123", "123"),
        ("42 madrid", "42 Madrid"),
        ("123 hello", "123 Hello"),
        ("hello 123", "Hello 123"),
        ("42 madrid exam", "42 Madrid Exam"),
        ("123 abc def", "123 Abc Def"),
        ("hello 42 world", "Hello 42 World"),
        ("1 2 3 hello", "1 2 3 Hello"),
        ("42 PYTHON 99 TEST", "42 Python 99 Test"),

        # numbers attached to letters
        ("abc123", "Abc123"),
        ("123abc", "123abc"),
        ("hello123", "Hello123"),
        ("123hello", "123hello"),
        ("abc123def", "Abc123def"),
        ("123abc456", "123abc456"),
        ("42madrid", "42madrid"),
        ("madrid42", "Madrid42"),
        ("test123case", "Test123case"),
        ("123test123", "123test123"),

        # punctuation
        ("hello!", "Hello!"),
        ("hello?", "Hello?"),
        ("hello.", "Hello."),
        ("hello,", "Hello,"),
        ("hello;", "Hello;"),
        ("hello:", "Hello:"),
        ("hello-world", "Hello-world"),
        ("hello_world", "Hello_world"),
        ("hello/world", "Hello/world"),
        ("hello@world", "Hello@world"),

        # punctuation between words
        ("hello, world", "Hello, World"),
        ("hello! world", "Hello! World"),
        ("hello? world", "Hello? World"),
        ("hello. world", "Hello. World"),
        ("hello; world", "Hello; World"),
        ("hello: world", "Hello: World"),
        ("hello - world", "Hello - World"),
        ("hello / world", "Hello / World"),
        ("hello @ world", "Hello @ World"),
        ("hello # world", "Hello # World"),

        # punctuation + multiple words
        ("hello,world", "Hello,world"),
        ("hello,world test", "Hello,world Test"),
        ("hello.world test", "Hello.world Test"),
        ("hello-world test", "Hello-world Test"),
        ("hello/world test", "Hello/world Test"),
        ("hello!world test", "Hello!world Test"),
        ("hello?world test", "Hello?world Test"),
        ("hello_world test", "Hello_world Test"),
        ("hello@world test", "Hello@world Test"),
        ("hello#world test", "Hello#world Test"),

        # longer sentences
        (
            "the quick brown fox",
            "The Quick Brown Fox",
        ),
        (
            "the QUICK BROWN fox jumps",
            "The Quick Brown Fox Jumps",
        ),
        (
            "this is a very long sentence",
            "This Is A Very Long Sentence",
        ),
        (
            "python is a great programming language",
            "Python Is A Great Programming Language",
        ),
        (
            "hello world this is python",
            "Hello World This Is Python",
        ),
        (
            "welcome to the world of programming",
            "Welcome To The World Of Programming",
        ),
        (
            "THE quick BROWN fox JUMPS over THE lazy DOG",
            "The Quick Brown Fox Jumps Over The Lazy Dog",
        ),
        (
            "  this   has    many spaces  ",
            "  This   Has    Many Spaces  ",
        ),
        (
            "42 madrid exam is tomorrow",
            "42 Madrid Exam Is Tomorrow",
        ),
        (
            "hello, world! this is a test.",
            "Hello, World! This Is A Test.",
        ),
    ]

    for value, expected in cases:
        result = module.capitalize_words(value)

        check(
            f"capitalize_words({value!r})",
            result,
            expected
        )


def test_convert_base(module):
    cases = [
        # basic conversions
        (("0", 10, 2), "0"),
        (("1", 10, 2), "1"),
        (("10", 10, 2), "1010"),
        (("15", 10, 2), "1111"),
        (("16", 10, 2), "10000"),
        (("10", 2, 10), "2"),
        (("101", 2, 10), "5"),
        (("1111", 2, 10), "15"),
        (("10000", 2, 10), "16"),
        (("ff", 16, 10), "255"),

        # hexadecimal
        (("a", 16, 10), "10"),
        (("b", 16, 10), "11"),
        (("c", 16, 10), "12"),
        (("d", 16, 10), "13"),
        (("e", 16, 10), "14"),
        (("f", 16, 10), "15"),
        (("10", 16, 10), "16"),
        (("ff", 16, 10), "255"),
        (("100", 16, 10), "256"),
        (("abc", 16, 10), "2748"),

        # hex to binary
        (("f", 16, 2), "1111"),
        (("ff", 16, 2), "11111111"),
        (("10", 16, 2), "10000"),
        (("1a", 16, 2), "11010"),
        (("2f", 16, 2), "101111"),
        (("a5", 16, 2), "10100101"),
        (("dead", 16, 2), "1101111010101101"),
        (("beef", 16, 2), "1011111011101111"),
        (("1234", 16, 2), "1001000110100"),
        (("ffff", 16, 2), "1111111111111111"),

        # bbinary to hexadecimal
        (("1", 2, 16), "1"),
        (("10", 2, 16), "2"),
        (("1111", 2, 16), "F"),
        (("11111111", 2, 16), "FF"),
        (("1010", 2, 16), "A"),
        (("10101010", 2, 16), "AA"),
        (("11001100", 2, 16), "CC"),
        (("11110000", 2, 16), "F0"),
        (("10111110", 2, 16), "BE"),
        (("11011110", 2, 16), "DE"),

        # decimal to other bases
        (("10", 10, 16), "A"),
        (("15", 10, 16), "F"),
        (("16", 10, 16), "10"),
        (("31", 10, 16), "1F"),
        (("255", 10, 16), "FF"),
        (("256", 10, 16), "100"),
        (("10", 10, 8), "12"),
        (("15", 10, 8), "17"),
        (("64", 10, 8), "100"),
        (("255", 10, 8), "377"),

        # base 8
        (("10", 8, 10), "8"),
        (("17", 8, 10), "15"),
        (("20", 8, 10), "16"),
        (("77", 8, 10), "63"),
        (("100", 8, 10), "64"),
        (("377", 8, 10), "255"),
        (("10", 8, 2), "1000"),
        (("77", 8, 2), "111111"),
        (("100", 8, 16), "40"),
        (("377", 8, 16), "FF"),

        # other bases
        (("10", 3, 10), "3"),
        (("11", 3, 10), "4"),
        (("100", 3, 10), "9"),
        (("10", 4, 10), "4"),
        (("123", 4, 10), "27"),
        (("10", 5, 10), "5"),
        (("24", 5, 10), "14"),
        (("10", 7, 10), "7"),
        (("123", 7, 10), "66"),
        (("10", 36, 10), "36"),

        # base 36
        (("z", 36, 10), "35"),
        (("y", 36, 10), "34"),
        (("10", 36, 10), "36"),
        (("zz", 36, 10), "1295"),
        (("100", 36, 10), "1296"),
        (("abc", 36, 10), "13368"),
        (("Z", 36, 10), "35"),
        (("ABC", 36, 10), "13368"),
        (("10", 36, 16), "24"),
        (("zz", 36, 16), "50F"),

        # upper/lowercase input
        (("FF", 16, 10), "255"),
        (("Ff", 16, 10), "255"),
        (("fF", 16, 10), "255"),
        (("ABC", 16, 10), "2748"),
        (("abc", 16, 10), "2748"),
        (("AbC", 16, 10), "2748"),
        (("dead", 16, 10), "57005"),
        (("DEAD", 16, 10), "57005"),
        (("BeEf", 16, 10), "48879"),
        (("bEeF", 16, 10), "48879"),

        # leading zeros
        (("00", 10, 2), "0"),
        (("0000", 10, 16), "0"),
        (("00010", 10, 2), "1010"),
        (("00042", 10, 16), "2A"),
        (("000ff", 16, 10), "255"),
        (("0001010", 2, 10), "10"),
        (("00077", 8, 10), "63"),
        (("000z", 36, 10), "35"),
        (("0001", 2, 16), "1"),
        (("000f", 16, 2), "1111"),

        # same base
        (("0", 2, 2), "0"),
        (("1010", 2, 2), "1010"),
        (("123", 10, 10), "123"),
        (("255", 10, 10), "255"),
        (("ff", 16, 16), "FF"),
        (("abc", 16, 16), "ABC"),
        (("77", 8, 8), "77"),
        (("zz", 36, 36), "ZZ"),
        (("123", 4, 4), "123"),
        (("10101", 2, 2), "10101"),

        # invalid bases
        (("10", 1, 10), "ERROR"),
        (("10", 10, 1), "ERROR"),
        (("10", 0, 10), "ERROR"),
        (("10", 10, 0), "ERROR"),
        (("10", -2, 10), "ERROR"),
        (("10", 10, -2), "ERROR"),
        (("10", 37, 10), "ERROR"),
        (("10", 10, 37), "ERROR"),
        (("10", 100, 100), "ERROR"),
        (("10", -1, -1), "ERROR"),

        # invalid digits
        (("2", 2, 10), "ERROR"),
        (("102", 2, 10), "ERROR"),
        (("8", 8, 10), "ERROR"),
        (("89", 8, 10), "ERROR"),
        (("g", 16, 10), "ERROR"),
        (("1g", 16, 10), "ERROR"),
        (("z", 35, 10), "ERROR"),
        (("10", 2, 36), "2"),
        (("1a", 10, 16), "ERROR"),
        (("123", 2, 10), "ERROR"),
    ]

    for args, expected in cases:
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            result = module.convert_base(*args)

        actual = output.getvalue().strip()

        check(
            f"convert_base{args}",
            (actual, result),
            (expected, None),
        )


def test_custom_sort(module):
    source = inspect.getsource(module.custom_sort)

    if ".sort(" in source or "sorted(" in source:
        print("FAIL: sort() and sorted() are not allowed")
        raise SystemExit(1)
    cases = [
        # basic cases
        ([], []),
        ([1], [1]),
        ([2, 1], [1, 2]),
        ([1, 2], [1, 2]),
        ([3, 1, 2], [1, 2, 3]),
        ([5, -1, 0], [-1, 0, 5]),
        ([2, 2], [2, 2]),
        ([1, 1, 1], [1, 1, 1]),
        ([3, 2, 1], [1, 2, 3]),
        ([1, 2, 3], [1, 2, 3]),

        # negative numbers
        ([-1, -2, -3], [-3, -2, -1]),
        ([-3, -1, -2], [-3, -2, -1]),
        ([-1, 0, 1], [-1, 0, 1]),
        ([0, -1, 1], [-1, 0, 1]),
        ([-5, -2, -8, -1], [-8, -5, -2, -1]),
        ([-10, -3, -7, -1], [-10, -7, -3, -1]),
        ([-100, -50, -75], [-100, -75, -50]),
        ([-1, -1, -2], [-2, -1, -1]),
        ([-5, -5, -5], [-5, -5, -5]),
        ([-10, 10, 0, -5, 5], [-10, -5, 0, 5, 10]),

        # zeros
        ([0, 0, 0], [0, 0, 0]),
        ([1, 0, 2], [0, 1, 2]),
        ([0, 5, 0, 3], [0, 0, 3, 5]),
        ([-1, 0, -2, 0, 1], [-2, -1, 0, 0, 1]),
        ([0, -5, 0, -3], [-5, -3, 0, 0]),
        ([10, 0, 5, 0, -5], [-5, 0, 0, 5, 10]),
        ([0], [0]),
        ([0, 0], [0, 0]),
        ([0, 1, 0, 1, 0], [0, 0, 0, 1, 1]),
        ([5, 0, -5, 0, 5], [-5, 0, 0, 5, 5]),

        # duplicates
        ([3, 3, 2, 1], [1, 2, 3, 3]),
        ([5, 1, 5, 1], [1, 1, 5, 5]),
        ([4, 2, 4, 2, 4], [2, 2, 4, 4, 4]),
        ([1, 2, 2, 3, 3, 3], [1, 2, 2, 3, 3, 3]),
        ([9, 9, 8, 8, 7, 7], [7, 7, 8, 8, 9, 9]),
        ([6, 1, 6, 1, 6, 1], [1, 1, 1, 6, 6, 6]),
        ([4, 4, 4, 2, 2, 1], [1, 2, 2, 4, 4, 4]),
        ([10, 5, 10, 5, 0], [0, 5, 5, 10, 10]),
        ([-1, -1, -2, -2], [-2, -2, -1, -1]),
        ([-3, 3, -3, 3], [-3, -3, 3, 3]),

        # already sorted
        ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),
        ([0, 1, 2, 3, 4], [0, 1, 2, 3, 4]),
        ([-5, -4, -3, -2, -1], [-5, -4, -3, -2, -1]),
        ([1, 3, 5, 7, 9], [1, 3, 5, 7, 9]),
        ([-10, -5, 0, 5, 10], [-10, -5, 0, 5, 10]),
        ([2, 4, 6, 8, 10], [2, 4, 6, 8, 10]),
        ([1, 1, 2, 2, 3, 3], [1, 1, 2, 2, 3, 3]),
        ([-3, -3, -2, -2, -1, -1], [-3, -3, -2, -2, -1, -1]),
        ([0, 0, 1, 1, 2, 2], [0, 0, 1, 1, 2, 2]),
        ([10, 20, 30, 40], [10, 20, 30, 40]),

        # reverse sorted
        ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5]),
        ([10, 9, 8, 7, 6], [6, 7, 8, 9, 10]),
        ([0, -1, -2, -3, -4], [-4, -3, -2, -1, 0]),
        ([100, 50, 25, 10, 1], [1, 10, 25, 50, 100]),
        ([9, 7, 5, 3, 1], [1, 3, 5, 7, 9]),
        ([5, 5, 4, 4, 3, 3], [3, 3, 4, 4, 5, 5]),
        ([10, 5, 0, -5, -10], [-10, -5, 0, 5, 10]),
        ([3, 2, 2, 1, 1], [1, 1, 2, 2, 3]),
        ([8, 6, 4, 2, 0], [0, 2, 4, 6, 8]),
        ([20, 10, 0, -10, -20], [-20, -10, 0, 10, 20]),

        # mixed positive/negative
        ([3, -1, 2, -5, 4], [-5, -1, 2, 3, 4]),
        ([-3, 7, -1, 5, 0], [-3, -1, 0, 5, 7]),
        ([10, -10, 5, -5, 0], [-10, -5, 0, 5, 10]),
        ([-7, 2, -3, 8, -1], [-7, -3, -1, 2, 8]),
        ([4, -2, 9, -8, 1], [-8, -2, 1, 4, 9]),
        ([-10, 3, -5, 7, -2], [-10, -5, -2, 3, 7]),
        ([6, -6, 4, -4, 2, -2], [-6, -4, -2, 2, 4, 6]),
        ([-9, 1, -4, 6, -2], [-9, -4, -2, 1, 6]),
        ([8, -1, -7, 3, 0], [-7, -1, 0, 3, 8]),
        ([-5, 10, -10, 5, 0], [-10, -5, 0, 5, 10]),

        # larger lists
        ([9, 1, 8, 2, 7, 3, 6, 4, 5], [1, 2, 3, 4, 5, 6, 7, 8, 9]),
        ([10, 3, 8, 1, 6, 2, 9, 4, 7, 5], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
        ([15, 3, 12, 6, 9, 0, 18, 21, 3], [0, 3, 3, 6, 9, 12, 15, 18, 21]),
        ([20, 5, 15, 10, 0, -5, -10], [-10, -5, 0, 5, 10, 15, 20]),
        ([12, -3, 7, -8, 4, 0, -1, 9], [-8, -3, -1, 0, 4, 7, 9, 12]),
        ([11, 22, 3, 14, 5, 16, 7, 18, 9, 20], [3, 5, 7, 9, 11, 14, 16, 18, 20,
                                                22]),
        ([50, 10, 40, 20, 30, 0], [0, 10, 20, 30, 40, 50]),
        ([13, 1, 21, 8, 5, 34, 2, 3], [1, 2, 3, 5, 8, 13, 21, 34]),
        ([100, -100, 50, -50, 25, -25], [-100, -50, -25, 25, 50, 100]),
        ([7, 14, 2, 28, 21, 35, 1], [1, 2, 7, 14, 21, 28, 35]),

        # more edge cases
        ([1000, 1, 500, 250], [1, 250, 500, 1000]),
        ([-1000, -1, -500, -250], [-1000, -500, -250, -1]),
        ([999, -999, 0], [-999, 0, 999]),
        ([2, -2, 2, -2, 0], [-2, -2, 0, 2, 2]),
        ([1, 100, 10, 1000, 5], [1, 5, 10, 100, 1000]),
        ([-1, -100, -10, -1000, -5], [-1000, -100, -10, -5, -1]),
        ([42, 7, 13, 42, 0, 7], [0, 7, 7, 13, 42, 42]),
        ([3, -3, 3, -3, 0, 0], [-3, -3, 0, 0, 3, 3]),
        ([25, 5, 15, 10, 20], [5, 10, 15, 20, 25]),
        ([8, 1, 4, 2, 7, 3, 6, 5], [1, 2, 3, 4, 5, 6, 7, 8]),

        # final 10
        ([31, 12, 45, 7, 23, 18, 4], [4, 7, 12, 18, 23, 31, 45]),
        ([6, -1, 9, -4, 2, -8, 5], [-8, -4, -1, 2, 5, 6, 9]),
        ([17, 3, 17, 2, 8, 3, 1], [1, 2, 3, 3, 8, 17, 17]),
        ([50, 40, 30, 20, 10], [10, 20, 30, 40, 50]),
        ([-50, -40, -30, -20, -10], [-50, -40, -30, -20, -10]),
        ([4, 0, -4, 8, -8, 12, -12], [-12, -8, -4, 0, 4, 8, 12]),
        ([19, 2, 14, 8, 11, 5, 17], [2, 5, 8, 11, 14, 17, 19]),
        ([100, 1, 50, 25, 75, 10], [1, 10, 25, 50, 75, 100]),
        ([-20, 15, -5, 10, -15, 5, 0], [-20, -15, -5, 0, 5, 10, 15]),
        ([33, 11, 22, 44, 55, 0, -11], [-11, 0, 11, 22, 33, 44, 55]),
    ]

    for arr, expected in cases:
        original = arr[:]
        result = module.custom_sort(arr)
        errors = []
        if result != expected:
            errors.append(
                f"\nwrong result\n"
                f"       Expected: {expected!r}\n"
                f"       Got:      {result!r}"
            )

        if arr != original:
            errors.append(
                f"\noriginal list was modified\n"
                f"       Original: {original!r}\n"
                f"       Got:      {arr!r}"
            )

        if result is arr:
            errors.append(
                "\nfunction returned the original list object"
            )

        check(
            f"custom_sort({arr!r})",
            not errors,
            True,
            errors,
        )


def test_merge_and_sort_desc(module):
    cases = [
        # basic
        ([1], [2], [2, 1]),
        ([1, 2], [3, 4], [4, 3, 2, 1]),
        ([1, 3, 5], [2, 4, 6], [6, 5, 4, 3, 2, 1]),
        ([10, 2], [3, 7, 2], [10, 7, 3, 2, 2]),
        ([5, 4, 3], [2, 1], [5, 4, 3, 2, 1]),
        ([1, 2, 3], [4, 5, 6], [6, 5, 4, 3, 2, 1]),
        ([100], [50], [100, 50]),
        ([50], [100], [100, 50]),
        ([3, 1, 2], [6, 5, 4], [6, 5, 4, 3, 2, 1]),
        ([9, 1, 5], [2, 8, 3], [9, 8, 5, 3, 2, 1]),

        # empty lists
        ([], [], []),
        ([], [1], [1]),
        ([1], [], [1]),
        ([], [1, 2, 3], [3, 2, 1]),
        ([1, 2, 3], [], [3, 2, 1]),
        ([], [5, 4, 3, 2, 1], [5, 4, 3, 2, 1]),
        ([5, 4, 3, 2, 1], [], [5, 4, 3, 2, 1]),
        ([], [100, -1, 0], [100, 0, -1]),
        ([100, -1, 0], [], [100, 0, -1]),
        ([], [0], [0]),

        # duplicates
        ([1, 1], [1, 1], [1, 1, 1, 1]),
        ([2, 2, 2], [2, 2], [2, 2, 2, 2, 2]),
        ([1, 2, 2], [2, 3, 3], [3, 3, 2, 2, 2, 1]),
        ([5, 5], [3, 3], [5, 5, 3, 3]),
        ([10, 10, 5], [10, 5, 5], [10, 10, 10, 5, 5, 5]),
        ([0, 0, 0], [0, 0], [0, 0, 0, 0, 0]),
        ([7, 7, 1], [7, 2, 7], [7, 7, 7, 7, 2, 1]),
        ([3, 3, 3], [], [3, 3, 3]),
        ([], [4, 4, 4], [4, 4, 4]),
        ([9, 9], [9], [9, 9, 9]),

        # negative numbers
        ([-1], [-2], [-1, -2]),
        ([-5, -1], [-3, -2], [-1, -2, -3, -5]),
        ([-10, -20], [-5, -15], [-5, -10, -15, -20]),
        ([-1, -2, -3], [-4, -5], [-1, -2, -3, -4, -5]),
        ([-100], [100], [100, -100]),
        ([-5, 0], [-2, 3], [3, 0, -2, -5]),
        ([-10, -1], [0, 10], [10, 0, -1, -10]),
        ([-7, -3], [-9, -1], [-1, -3, -7, -9]),
        ([-100, -50], [-75, -25], [-25, -50, -75, -100]),
        ([-1, -1], [-2, -2], [-1, -1, -2, -2]),

        # zeros
        ([0], [0], [0, 0]),
        ([0, 1], [0, 2], [2, 1, 0, 0]),
        ([0, -1], [0, -2], [0, 0, -1, -2]),
        ([5, 0, 3], [0, 4, 1], [5, 4, 3, 1, 0, 0]),
        ([0, 0, 5], [0, 0, 3], [5, 3, 0, 0, 0, 0]),
        ([-1, 0, 1], [0], [1, 0, 0, -1]),
        ([0], [-1, 0, 1], [1, 0, 0, -1]),
        ([0, 0], [-1, -2], [0, 0, -1, -2]),
        ([-3, 0, -1], [0, -2], [0, 0, -1, -2, -3]),
        ([10, 0], [5, 0], [10, 5, 0, 0]),

        # already ascending
        ([1, 2, 3], [4, 5, 6], [6, 5, 4, 3, 2, 1]),
        ([1, 2], [3], [3, 2, 1]),
        ([1], [2, 3], [3, 2, 1]),
        ([-5, -4, -3], [-2, -1], [-1, -2, -3, -4, -5]),
        ([0, 1, 2], [3, 4, 5], [5, 4, 3, 2, 1, 0]),

        # already descending
        ([5, 4, 3], [2, 1], [5, 4, 3, 2, 1]),
        ([10, 9, 8], [7, 6, 5], [10, 9, 8, 7, 6, 5]),
        ([3, 2, 1], [6, 5, 4], [6, 5, 4, 3, 2, 1]),
        ([-1, -2, -3], [-4, -5], [-1, -2, -3, -4, -5]),
        ([100, 50, 25], [75, 60, 10], [100, 75, 60, 50, 25, 10]),

        # unsorted
        ([3, 1, 4, 2], [8, 6, 7, 5], [8, 7, 6, 5, 4, 3, 2, 1]),
        ([10, 1, 8, 3], [7, 2, 9, 4], [10, 9, 8, 7, 4, 3, 2, 1]),
        ([5, 1, 9, 2], [8, 3, 7, 4], [9, 8, 7, 5, 4, 3, 2, 1]),
        ([100, 1, 50], [75, 25, 90], [100, 90, 75, 50, 25, 1]),
        ([6, 2, 9], [4, 8, 1], [9, 8, 6, 4, 2, 1]),
        ([12, 3, 7], [10, 2, 15], [15, 12, 10, 7, 3, 2]),
        ([20, 5, 30], [25, 10, 15], [30, 25, 20, 15, 10, 5]),
        ([11, 4, 6], [9, 2, 8], [11, 9, 8, 6, 4, 2]),
        ([14, 1, 13], [12, 3, 15], [15, 14, 13, 12, 3, 1]),
        ([7, 2, 10], [5, 9, 1], [10, 9, 7, 5, 2, 1]),

        # large positive values
        ([1000, 500], [750, 250], [1000, 750, 500, 250]),
        ([9999], [10000], [10000, 9999]),
        ([100000, 1], [50000, 2], [100000, 50000, 2, 1]),
        ([1000000, 500000], [750000, 250000], [1000000, 750000, 500000,
                                               250000]),
        ([999, 100], [500, 1000], [1000, 999, 500, 100]),
        ([2147483647], [-2147483648], [2147483647, -2147483648]),
        ([1000000000], [999999999], [1000000000, 999999999]),
        ([123456, 654321], [111111, 999999], [999999, 654321, 123456, 111111]),
        ([5000, 4000], [3000, 2000], [5000, 4000, 3000, 2000]),
        ([99999, 1], [88888, 2], [99999, 88888, 2, 1]),

        # mixed positive and negative
        ([-5, 10, -2], [3, -8, 7], [10, 7, 3, -2, -5, -8]),
        ([100, -100], [50, -50], [100, 50, -50, -100]),
        ([-10, 20, -30], [40, -50, 60], [60, 40, 20, -10, -30, -50]),
        ([1, -1], [-2, 2], [2, 1, -1, -2]),
        ([-100, 0, 100], [50, -50], [100, 50, 0, -50, -100]),
        ([25, -25, 10], [-10, 30, -5], [30, 25, 10, -5, -10, -25]),
        ([-7, 14, -21], [28, -35, 42], [42, 28, 14, -7, -21, -35]),
        ([9, -9], [8, -8], [9, 8, -8, -9]),
        ([-1, 5, -3], [4, -2, 6], [6, 5, 4, -1, -2, -3]),
        ([-50, 75], [25, -100], [75, 25, -50, -100]),

        # single element combinations
        ([5], [5], [5, 5]),
        ([-5], [-5], [-5, -5]),
        ([0], [10], [10, 0]),
        ([-10], [0], [0, -10]),
        ([100], [-100], [100, -100]),
        ([7], [3], [7, 3]),
        ([3], [7], [7, 3]),
        ([1], [-1], [1, -1]),
        ([-1], [1], [1, -1]),
        ([42], [42], [42, 42]),

        # more duplicates and combinations
        ([1, 3, 3, 5], [2, 3, 4, 5], [5, 5, 4, 3, 3, 3, 2, 1]),
        ([10, 20, 10], [20, 10, 20], [20, 20, 20, 10, 10, 10]),
        ([5, 1, 5, 1], [5, 2, 5, 2], [5, 5, 5, 5, 2, 2, 1, 1]),
        ([9, 9, 8], [8, 8, 7], [9, 9, 8, 8, 8, 7]),
        ([4, 4, 4], [3, 3, 3], [4, 4, 4, 3, 3, 3]),
        ([2, 1, 2, 1], [1, 2, 1, 2], [2, 2, 2, 2, 1, 1, 1, 1]),
        ([0, 5, 0], [5, 0, 5], [5, 5, 5, 0, 0, 0]),
        ([-1, -2, -1], [-2, -3, -2], [-1, -1, -2, -2, -2, -3]),
        ([100, 100, 50], [100, 50, 50], [100, 100, 100, 50, 50, 50]),
        ([7, 7, 7], [7, 7, 7], [7, 7, 7, 7, 7, 7]),
    ]

    for first, second, expected in cases:
        first_original = first[:]
        second_original = second[:]

        result = module.merge_and_sort_desc(first, second)

        errors = []

        if result != expected:
            errors.append(
                f"\nwrong result\n"
                f"       Expected: {expected!r}\n"
                f"       Got:      {result!r}"
            )

        if first != first_original:
            errors.append(
                f"\nfirst list was modified\n"
                f"       Original: {first_original!r}\n"
                f"       Got:      {first!r}"
            )

        if second != second_original:
            errors.append(
                f"\nsecond list was modified\n"
                f"       Original: {second_original!r}\n"
                f"       Got:      {second!r}"
            )

        if result is first:
            errors.append(
                "\nfunction returned the first input list"
            )

        if result is second:
            errors.append(
                "\nfunction returned the second input list"
            )

        check(
            f"merge_and_sort_desc({first_original!r}, {second_original!r})",
            not errors,
            True,
            errors,
        )


def test_mirror_matrix(module):
    cases = [
        # empty / minimal
        ([], []),
        ([[]], [[]]),
        ([[1]], [[1]]),
        ([[0]], [[0]]),
        ([[-1]], [[-1]]),

        # single row
        ([[1, 2]], [[2, 1]]),
        ([[1, 2, 3]], [[3, 2, 1]]),
        ([[1, 2, 3, 4]], [[4, 3, 2, 1]]),
        ([[1, 2, 3, 4, 5]], [[5, 4, 3, 2, 1]]),
        ([[5, 4, 3, 2, 1]], [[1, 2, 3, 4, 5]]),

        # single column
        ([[1], [2]], [[1], [2]]),
        ([[1], [2], [3]], [[1], [2], [3]]),
        ([[1], [2], [3], [4]], [[1], [2], [3], [4]]),
        ([[5], [4], [3], [2], [1]], [[5], [4], [3], [2], [1]]),
        ([[-1], [-2], [-3]], [[-1], [-2], [-3]]),

        # basic 2x2
        ([[1, 2], [3, 4]], [[2, 1], [4, 3]]),
        ([[4, 3], [2, 1]], [[3, 4], [1, 2]]),
        ([[1, 0], [0, 1]], [[0, 1], [1, 0]]),
        ([[5, 6], [7, 8]], [[6, 5], [8, 7]]),
        ([[-1, -2], [-3, -4]], [[-2, -1], [-4, -3]]),

        # basic 2x3
        ([[1, 2, 3], [4, 5, 6]], [[3, 2, 1], [6, 5, 4]]),
        ([[6, 5, 4], [3, 2, 1]], [[4, 5, 6], [1, 2, 3]]),
        ([[1, 2, 3], [3, 2, 1]], [[3, 2, 1], [1, 2, 3]]),
        ([[10, 20, 30], [40, 50, 60]], [[30, 20, 10], [60, 50, 40]]),
        ([[-1, -2, -3], [-4, -5, -6]], [[-3, -2, -1], [-6, -5, -4]]),

        # basic 3x2
        ([[1, 2], [3, 4], [5, 6]], [[2, 1], [4, 3], [6, 5]]),
        ([[2, 1], [4, 3], [6, 5]], [[1, 2], [3, 4], [5, 6]]),
        ([[10, 20], [30, 40], [50, 60]], [[20, 10], [40, 30], [60, 50]]),
        ([[-1, -2], [-3, -4], [-5, -6]], [[-2, -1], [-4, -3], [-6, -5]]),
        ([[0, 1], [2, 0], [3, 4]], [[1, 0], [0, 2], [4, 3]]),

        # 3x3
        (
            [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
            [[3, 2, 1], [6, 5, 4], [9, 8, 7]],
        ),
        (
            [[9, 8, 7], [6, 5, 4], [3, 2, 1]],
            [[7, 8, 9], [4, 5, 6], [1, 2, 3]],
        ),
        (
            [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            [[0, 0, 1], [0, 1, 0], [1, 0, 0]],
        ),
        (
            [[1, 1, 1], [2, 2, 2], [3, 3, 3]],
            [[1, 1, 1], [2, 2, 2], [3, 3, 3]],
        ),
        (
            [[3, 2, 1], [6, 5, 4], [9, 8, 7]],
            [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        ),

        # 3x4
        (
            [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]],
            [[4, 3, 2, 1], [8, 7, 6, 5], [12, 11, 10, 9]],
        ),
        (
            [[4, 3, 2, 1], [8, 7, 6, 5], [12, 11, 10, 9]],
            [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]],
        ),
        (
            [[10, 20, 30, 40], [50, 60, 70, 80], [90, 100, 110, 120]],
            [[40, 30, 20, 10], [80, 70, 60, 50], [120, 110, 100, 90]],
        ),
        (
            [[-1, -2, -3, -4], [-5, -6, -7, -8], [-9, -10, -11, -12]],
            [[-4, -3, -2, -1], [-8, -7, -6, -5], [-12, -11, -10, -9]],
        ),
        (
            [[0, 1, 0, 1], [1, 0, 1, 0], [0, 1, 0, 1]],
            [[1, 0, 1, 0], [0, 1, 0, 1], [1, 0, 1, 0]],
        ),

        # 4x3
        (
            [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]],
            [[3, 2, 1], [6, 5, 4], [9, 8, 7], [12, 11, 10]],
        ),
        (
            [[3, 2, 1], [6, 5, 4], [9, 8, 7], [12, 11, 10]],
            [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]],
        ),
        (
            [[10, 20, 30], [40, 50, 60], [70, 80, 90], [100, 110, 120]],
            [[30, 20, 10], [60, 50, 40], [90, 80, 70], [120, 110, 100]],
        ),
        (
            [[-1, -2, -3], [-4, -5, -6], [-7, -8, -9], [-10, -11, -12]],
            [[-3, -2, -1], [-6, -5, -4], [-9, -8, -7], [-12, -11, -10]],
        ),
        (
            [[0, 0, 1], [1, 0, 0], [0, 1, 0], [1, 1, 1]],
            [[1, 0, 0], [0, 0, 1], [0, 1, 0], [1, 1, 1]],
        ),

        # 4x4
        (
            [[1, 2, 3, 4],
             [5, 6, 7, 8],
             [9, 10, 11, 12],
             [13, 14, 15, 16]],
            [[4, 3, 2, 1],
             [8, 7, 6, 5],
             [12, 11, 10, 9],
             [16, 15, 14, 13]],
        ),
        (
            [[16, 15, 14, 13],
             [12, 11, 10, 9],
             [8, 7, 6, 5],
             [4, 3, 2, 1]],
            [[13, 14, 15, 16],
             [9, 10, 11, 12],
             [5, 6, 7, 8],
             [1, 2, 3, 4]],
        ),
        (
            [[1, 1, 1, 1],
             [2, 2, 2, 2],
             [3, 3, 3, 3],
             [4, 4, 4, 4]],
            [[1, 1, 1, 1],
             [2, 2, 2, 2],
             [3, 3, 3, 3],
             [4, 4, 4, 4]],
        ),
        (
            [[0, 1, 2, 3],
             [4, 5, 6, 7],
             [8, 9, 10, 11],
             [12, 13, 14, 15]],
            [[3, 2, 1, 0],
             [7, 6, 5, 4],
             [11, 10, 9, 8],
             [15, 14, 13, 12]],
        ),
        (
            [[-4, -3, -2, -1],
             [-8, -7, -6, -5],
             [-12, -11, -10, -9],
             [-16, -15, -14, -13]],
            [[-1, -2, -3, -4],
             [-5, -6, -7, -8],
             [-9, -10, -11, -12],
             [-13, -14, -15, -16]],
        ),

        # zeros
        ([[0, 0], [0, 0]], [[0, 0], [0, 0]]),
        ([[0, 1], [0, 2]], [[1, 0], [2, 0]]),
        ([[1, 0], [2, 0]], [[0, 1], [0, 2]]),
        ([[0, 0, 1]], [[1, 0, 0]]),
        ([[1, 0, 0]], [[0, 0, 1]]),
        ([[0, 1, 0], [1, 0, 1]], [[0, 1, 0], [1, 0, 1]]),
        ([[0, 0, 5], [0, 10, 0]], [[5, 0, 0], [0, 10, 0]]),
        ([[5, 0, 0], [0, 10, 0]], [[0, 0, 5], [0, 10, 0]]),
        ([[0, -1, 0], [-2, 0, -3]], [[0, -1, 0], [-3, 0, -2]]),
        ([[0, 0, 0], [1, 2, 3]], [[0, 0, 0], [3, 2, 1]]),

        # negative values
        ([[-1, -2], [-3, -4]], [[-2, -1], [-4, -3]]),
        ([[-1, -2, -3]], [[-3, -2, -1]]),
        ([[-1], [-2], [-3]], [[-1], [-2], [-3]]),
        ([[-10, -20, -30], [-40, -50, -60]],
         [[-30, -20, -10], [-60, -50, -40]]),
        ([[-5, 0, 5], [-10, 0, 10]],
         [[5, 0, -5], [10, 0, -10]]),
        ([[-100, -50, 0, 50, 100]],
         [[100, 50, 0, -50, -100]]),
        ([[-3, -1, -2], [-6, -4, -5]],
         [[-2, -1, -3], [-5, -4, -6]]),
        ([[-9, -8, -7], [-6, -5, -4]],
         [[-7, -8, -9], [-4, -5, -6]]),
        ([[-1, 2, -3], [4, -5, 6]],
         [[-3, 2, -1], [6, -5, 4]]),
        ([[-100, 200], [300, -400]],
         [[200, -100], [-400, 300]]),

        # duplicate values
        ([[1, 1, 1], [2, 2, 2]], [[1, 1, 1], [2, 2, 2]]),
        ([[1, 2, 1], [3, 3, 3]], [[1, 2, 1], [3, 3, 3]]),
        ([[5, 5, 4, 4]], [[4, 4, 5, 5]]),
        ([[1, 2, 2, 1]], [[1, 2, 2, 1]]),
        ([[7, 7], [8, 8], [9, 9]], [[7, 7], [8, 8], [9, 9]]),
        ([[3, 1, 3], [2, 2, 1]], [[3, 1, 3], [1, 2, 2]]),
        ([[10, 20, 10, 20]], [[20, 10, 20, 10]]),
        ([[5, 0, 5], [0, 5, 0]], [[5, 0, 5], [0, 5, 0]]),
        ([[9, 9, 1, 1]], [[1, 1, 9, 9]]),
        ([[4, 4, 4, 4]], [[4, 4, 4, 4]]),

        # large values
        ([[100, 200, 300]], [[300, 200, 100]]),
        ([[1000, 500, 2000]], [[2000, 500, 1000]]),
        ([[999999, 1], [500000, 750000]],
         [[1, 999999], [750000, 500000]]),
        ([[2147483647, -2147483648]],
         [[-2147483648, 2147483647]]),
        ([[1000000000, 2000000000]],
         [[2000000000, 1000000000]]),

        # irregular-looking values
        ([[42, 7, 100, 3]], [[3, 100, 7, 42]]),
        ([[8, 6, 7], [5, 3, 0]], [[7, 6, 8], [0, 3, 5]]),
        ([[10, -5, 20], [0, 15, -10]], [[20, -5, 10], [-10, 15, 0]]),
        ([[100, 1, 50, 25]], [[25, 50, 1, 100]]),
        ([[11, 22, 33], [44, 55, 66]], [[33, 22, 11], [66, 55, 44]]),

        # larger rectangular matrices
        (
            [[1, 2, 3, 4, 5],
             [6, 7, 8, 9, 10]],
            [[5, 4, 3, 2, 1],
             [10, 9, 8, 7, 6]],
        ),
        (
            [[1, 2],
             [3, 4],
             [5, 6],
             [7, 8],
             [9, 10]],
            [[2, 1],
             [4, 3],
             [6, 5],
             [8, 7],
             [10, 9]],
        ),
        (
            [[1, 2, 3, 4, 5, 6]],
            [[6, 5, 4, 3, 2, 1]],
        ),
        (
            [[1, 2, 3, 4, 5, 6, 7, 8]],
            [[8, 7, 6, 5, 4, 3, 2, 1]],
        ),
        (
            [[1, 2, 3],
             [4, 5, 6],
             [7, 8, 9],
             [10, 11, 12],
             [13, 14, 15]],
            [[3, 2, 1],
             [6, 5, 4],
             [9, 8, 7],
             [12, 11, 10],
             [15, 14, 13]],
        ),
    ]

    for value, expected in cases:
        original = [row.copy() for row in value]

        result = module.mirror_matrix(value)

        errors = []

        if result != expected:
            errors.append(
                f"\nwrong result\n"
                f"       Expected: {expected!r}\n"
                f"       Got:      {result!r}"
            )

        if value != original:
            errors.append(
                f"\noriginal matrix was modified\n"
                f"       Original: {original!r}\n"
                f"       Got:      {value!r}"
            )

        if result is value:
            errors.append(
                "\nfunction returned the original matrix object"
            )

        check(
            f"mirror_matrix({value!r})",
            not errors,
            True,
            errors,
        )


def test_mirror_matrix_vertical(module):
    cases = [
        ([[1, 2], [3, 4]], [[3, 4], [1, 2]]),
        ([[1, 2, 3], [4, 5, 6], [7, 8, 9]],
         [[7, 8, 9], [4, 5, 6], [1, 2, 3]]),
        ([[1]], [[1]]),
        ([], []),
        ([[1, 2, 3, 4]], [[1, 2, 3, 4]]),
        ([[1], [2]], [[2], [1]]),
        ([[1], [2], [3]], [[3], [2], [1]]),
        ([[10, 20], [30, 40], [50, 60], [70, 80]],
         [[70, 80], [50, 60], [30, 40], [10, 20]]),
        ([[0, 0], [0, 0]], [[0, 0], [0, 0]]),
        ([[-1, -2], [-3, -4]], [[-3, -4], [-1, -2]]),

        ([[1, 2, 3], [4, 5, 6]], [[4, 5, 6], [1, 2, 3]]),
        ([[9, 8, 7], [6, 5, 4], [3, 2, 1]],
         [[3, 2, 1], [6, 5, 4], [9, 8, 7]]),
        ([[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]],
         [[6, 7, 8, 9, 10], [1, 2, 3, 4, 5]]),
        ([[5, 4, 3, 2, 1], [10, 9, 8, 7, 6]],
         [[10, 9, 8, 7, 6], [5, 4, 3, 2, 1]]),
        ([[100], [200], [300], [400]], [[400], [300], [200], [100]]),
        ([[-1], [0], [1]], [[1], [0], [-1]]),
        ([[1, 2], [3, 4], [5, 6]], [[5, 6], [3, 4], [1, 2]]),
        ([[7, 8], [9, 10], [11, 12], [13, 14], [15, 16]],
         [[15, 16], [13, 14], [11, 12], [9, 10], [7, 8]]),
        ([["a"], ["b"], ["c"]], [["c"], ["b"], ["a"]]),
        ([["hello", "world"], ["foo", "bar"]],
         [["foo", "bar"], ["hello", "world"]]),

        ([[True, False], [False, True]], [[False, True], [True, False]]),
        ([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]],
         [[10, 11, 12], [7, 8, 9], [4, 5, 6], [1, 2, 3]]),
        ([[3, 1], [4, 1], [5, 9], [2, 6]],
         [[2, 6], [5, 9], [4, 1], [3, 1]]),
        ([[11, 22, 33, 44], [55, 66, 77, 88]],
         [[55, 66, 77, 88], [11, 22, 33, 44]]),
        ([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10], [11, 12]],
         [[11, 12], [9, 10], [7, 8], [5, 6], [3, 4], [1, 2]]),
        ([[0], [0], [1], [1]], [[1], [1], [0], [0]]),
        ([[-10, -20], [-30, -40], [-50, -60]],
         [[-50, -60], [-30, -40], [-10, -20]]),
        ([[1000, 2000], [3000, 4000]], [[3000, 4000], [1000, 2000]]),
        ([[1, 2, 3, 4, 5]], [[1, 2, 3, 4, 5]]),
        ([[1], [2], [3], [4], [5], [6]], [[6], [5], [4], [3], [2], [1]]),
        ([[2, 4, 6], [8, 10, 12]], [[8, 10, 12], [2, 4, 6]]),

        ([[3, 6, 9], [12, 15, 18], [21, 24, 27]],
         [[21, 24, 27], [12, 15, 18], [3, 6, 9]]),
        ([[1, 0, 1], [0, 1, 0]], [[0, 1, 0], [1, 0, 1]]),
        ([[-5, 0, 5], [-10, 0, 10]], [[-10, 0, 10], [-5, 0, 5]]),
        ([[42, 43], [44, 45], [46, 47]], [[46, 47], [44, 45], [42, 43]]),
        ([[100, 101, 102], [103, 104, 105]],
         [[103, 104, 105], [100, 101, 102]]),
        ([[9], [8], [7], [6]], [[6], [7], [8], [9]]),
        ([[1, 1], [2, 2], [3, 3]], [[3, 3], [2, 2], [1, 1]]),
        ([[5, 5, 5], [6, 6, 6]], [[6, 6, 6], [5, 5, 5]]),
        ([[10, 20, 30], [40, 50, 60], [70, 80, 90]],
         [[70, 80, 90], [40, 50, 60], [10, 20, 30]]),
        ([["A", "B"], ["C", "D"], ["E", "F"]],
         [["E", "F"], ["C", "D"], ["A", "B"]]),

        ([["one"], ["two"], ["three"]], [["three"], ["two"], ["one"]]),
        ([[True], [False], [True]], [[True], [False], [True]]),
        ([[False, False], [True, True]], [[True, True], [False, False]]),
        ([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]],
         [[9, 10, 11, 12], [5, 6, 7, 8], [1, 2, 3, 4]]),
        ([[-1, -2, -3], [-4, -5, -6]],
         [[-4, -5, -6], [-1, -2, -3]]),
        ([[99, 88], [77, 66], [55, 44], [33, 22]],
         [[33, 22], [55, 44], [77, 66], [99, 88]]),
        ([[123]], [[123]]),
        ([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]],
         [[9, 10], [7, 8], [5, 6], [3, 4], [1, 2]]),
        ([[0, 1, 2], [3, 4, 5], [6, 7, 8]],
         [[6, 7, 8], [3, 4, 5], [0, 1, 2]]),
        ([[10, 11], [12, 13]], [[12, 13], [10, 11]]),

        ([[20, 21, 22], [23, 24, 25], [26, 27, 28]],
         [[26, 27, 28], [23, 24, 25], [20, 21, 22]]),
        ([[-100], [-200], [-300]], [[-300], [-200], [-100]]),
        ([[1, -1], [2, -2], [3, -3]], [[3, -3], [2, -2], [1, -1]]),
        ([[100, 0], [0, 100]], [[0, 100], [100, 0]]),
        ([[1, 2, 3, 4, 5], [6, 7, 8, 9, 10], [11, 12, 13, 14, 15]],
         [[11, 12, 13, 14, 15], [6, 7, 8, 9, 10], [1, 2, 3, 4, 5]]),
        ([[7, 7], [8, 8], [9, 9], [10, 10]],
         [[10, 10], [9, 9], [8, 8], [7, 7]]),
        ([[2, 3, 5], [7, 11, 13]], [[7, 11, 13], [2, 3, 5]]),
        ([[17, 19], [23, 29], [31, 37]],
         [[31, 37], [23, 29], [17, 19]]),
        ([[50, 40, 30], [20, 10, 0]],
         [[20, 10, 0], [50, 40, 30]]),
        ([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10],
          [11, 12], [13, 14]],
         [[13, 14], [11, 12], [9, 10], [7, 8],
          [5, 6], [3, 4], [1, 2]]),

        ([[1, 2, 3, 4, 5, 6]], [[1, 2, 3, 4, 5, 6]]),
        ([[1], [2], [3], [4], [5], [6], [7]],
         [[7], [6], [5], [4], [3], [2], [1]]),
        ([[-9, -8, -7], [-6, -5, -4], [-3, -2, -1]],
         [[-3, -2, -1], [-6, -5, -4], [-9, -8, -7]]),
        ([[100, 200, 300], [400, 500, 600]],
         [[400, 500, 600], [100, 200, 300]]),
        ([[13], [26], [39]], [[39], [26], [13]]),
        ([[2, 4, 6, 8], [10, 12, 14, 16]],
         [[10, 12, 14, 16], [2, 4, 6, 8]]),
        ([[1, 3, 5], [7, 9, 11], [13, 15, 17]],
         [[13, 15, 17], [7, 9, 11], [1, 3, 5]]),
        ([[2, 4], [6, 8], [10, 12], [14, 16]],
         [[14, 16], [10, 12], [6, 8], [2, 4]]),
        ([[1, 1, 2, 2], [3, 3, 4, 4]],
         [[3, 3, 4, 4], [1, 1, 2, 2]]),
        ([[10], [20], [30], [40], [50]],
         [[50], [40], [30], [20], [10]]),

        ([[-1, 1], [-2, 2], [-3, 3]], [[-3, 3], [-2, 2], [-1, 1]]),
        ([[4, 8, 12], [16, 20, 24]], [[16, 20, 24], [4, 8, 12]]),
        ([[25, 50], [75, 100]], [[75, 100], [25, 50]]),
        ([[1, 2, 3], [4, 5, 6], [7, 8, 9],
          [10, 11, 12], [13, 14, 15]],
         [[13, 14, 15], [10, 11, 12], [7, 8, 9],
          [4, 5, 6], [1, 2, 3]]),
        ([["x", "y"], ["z", "w"]], [["z", "w"], ["x", "y"]]),
        ([["red"], ["green"], ["blue"]],
         [["blue"], ["green"], ["red"]]),
        ([["a", "b", "c"], ["d", "e", "f"]],
         [["d", "e", "f"], ["a", "b", "c"]]),
        ([[None], [1], [None]], [[None], [1], [None]]),
        ([[None, 1], [2, None]], [[2, None], [None, 1]]),
        ([[1, 2, 3], [], [4, 5, 6]],
         [[4, 5, 6], [], [1, 2, 3]]),

        ([[], [], []], [[], [], []]),
        ([[1, 2], [], [3, 4], []],
         [[], [3, 4], [], [1, 2]]),
        ([[-1000, 1000], [0, 0]], [[0, 0], [-1000, 1000]]),
        ([[999999], [-999999]], [[-999999], [999999]]),
        ([[1, 2, 3, 4], [5, 6, 7, 8],
          [9, 10, 11, 12], [13, 14, 15, 16]],
         [[13, 14, 15, 16], [9, 10, 11, 12],
          [5, 6, 7, 8], [1, 2, 3, 4]]),
        ([[17, 18, 19], [20, 21, 22], [23, 24, 25]],
         [[23, 24, 25], [20, 21, 22], [17, 18, 19]]),
        ([[31, 32], [33, 34], [35, 36], [37, 38]],
         [[37, 38], [35, 36], [33, 34], [31, 32]]),
        ([[100, 200, 300], [400, 500, 600],
          [700, 800, 900]],
         [[700, 800, 900], [400, 500, 600],
          [100, 200, 300]]),
        ([[-1, -2, -3, -4], [4, 3, 2, 1]],
         [[4, 3, 2, 1], [-1, -2, -3, -4]]),
        ([[0, 1], [1, 0], [0, 1], [1, 0]],
         [[1, 0], [0, 1], [1, 0], [0, 1]]),

        ([[2, 2, 2], [3, 3, 3], [4, 4, 4], [5, 5, 5]],
         [[5, 5, 5], [4, 4, 4], [3, 3, 3], [2, 2, 2]]),
        ([[1, 2, 3, 4, 5, 6, 7, 8]],
         [[1, 2, 3, 4, 5, 6, 7, 8]]),
        ([[1], [2], [3], [4], [5], [6], [7], [8]],
         [[8], [7], [6], [5], [4], [3], [2], [1]]),
        ([[1, 2, 3], [3, 2, 1]],
         [[3, 2, 1], [1, 2, 3]]),
        ([[5, 10, 15], [20, 25, 30],
          [35, 40, 45], [50, 55, 60]],
         [[50, 55, 60], [35, 40, 45],
          [20, 25, 30], [5, 10, 15]]),
        ([[101, 102], [103, 104], [105, 106]],
         [[105, 106], [103, 104], [101, 102]]),
        ([[-10, -20, -30], [40, 50, 60]],
         [[40, 50, 60], [-10, -20, -30]]),
        ([[123, 456, 789], [987, 654, 321]],
         [[987, 654, 321], [123, 456, 789]]),
        ([[1, 2, 3, 4, 5],
          [6, 7, 8, 9, 10],
          [11, 12, 13, 14, 15],
          [16, 17, 18, 19, 20],
          [21, 22, 23, 24, 25]],
         [[21, 22, 23, 24, 25],
          [16, 17, 18, 19, 20],
          [11, 12, 13, 14, 15],
          [6, 7, 8, 9, 10],
          [1, 2, 3, 4, 5]]),
    ]

    for value, expected in cases:
        original = [row[:] for row in value]

        result = module.mirror_matrix_vertical(value)

        errors = []

        if result != expected:
            errors.append(
                f"\nwrong result\n"
                f"       Expected: {expected!r}\n"
                f"       Got:      {result!r}"
            )

        if value != original:
            errors.append(
                f"\noriginal matrix was modified\n"
                f"       Original: {original!r}\n"
                f"       Got:      {value!r}"
            )

        if result is value:
            errors.append(
                "\nfunction returned the original matrix object"
            )

        check(
            f"mirror_matrix_vertical({value!r})",
            not errors,
            True,
            errors,
        )


def test_py_echo_validator(module):

    cases = [
        # basic palindromes
        ("", True),
        ("a", True),
        ("aa", True),
        ("aba", True),
        ("abba", True),
        ("abcba", True),
        ("racecar", True),
        ("level", True),
        ("radar", True),
        ("civic", True),

        # basic non-palindromes
        ("ab", False),
        ("abc", False),
        ("abcd", False),
        ("hello", False),
        ("world", False),
        ("python", False),
        ("palindrome", False),
        ("racecars", False),
        ("levelup", False),
        ("abcdef", False),

        # case-insensitive
        ("A", True),
        ("Aa", True),
        ("aA", True),
        ("AbA", True),
        ("ABCBA", True),
        ("RaceCar", True),
        ("RaCeCaR", True),
        ("LEVEL", True),
        ("LeVeL", True),
        ("CiViC", True),

        # case-insensitive non-palindromes
        ("Ab", False),
        ("aB", False),
        ("Abc", False),
        ("ABC", False),
        ("Racecars", False),
        ("Hello", False),
        ("Python", False),
        ("PyThOn", False),
        ("AbCd", False),
        ("WoRlD", False),

        # spaces
        ("a a", True),
        ("a b a", True),
        ("a b", False),
        ("race car", True),
        ("raceecar", True),
        ("never odd or even", True),
        ("never odd or even!", True),
        ("step on no pets", True),
        ("was it a car or a cat i saw", True),
        ("this is not a palindrome", False),

        # punctuation
        ("a!", True),
        ("!a!", True),
        ("a!b!a", True),
        ("a!b", False),
        ("a,b,a", True),
        ("a,b,c", False),
        ("madam!", True),
        ("madam?", True),
        ("madam.", True),
        ("hello!", False),

        # classic examples
        ("Was it a car or a cat I saw?", True),
        ("tab a cat", False),
        ("A man, a plan, a canal: Panama", True),
        ("No lemon, no melon", True),
        ("Never odd or even", True),
        ("Mr. Owl ate my metal worm", True),
        ("Do geese see God?", True),
        ("Was it Eliot's toilet I saw?", True),
        ("Yo, banana boy!", True),
        ("Eva, can I see bees in a cave?", True),

        # numbers
        ("1", True),
        ("11", True),
        ("12", False),
        ("121", True),
        ("12321", True),
        ("12345", False),
        ("1001", True),
        ("1002", False),
        ("1234321", True),
        ("1234567", False),

        # letters + numbers
        ("a1a", True),
        ("a1b", False),
        ("1a1", True),
        ("1ab1", False),
        ("1ab2", False),
        ("abc123cba", False),
        ("abc123", False),
        ("123abc321", False),
        ("123abc123", False),
        ("a1b2b1a", True),

        # special characters / symbols
        ("!!!", True),
        ("@@@", True),
        ("...", True),
        ("!@#$%", True),
        ("a!!!a", True),
        ("a!!!b", False),
        ("1!!!1", True),
        ("1!!!2", False),
        ("(())", True),
        ("(a)", True),

        # more mixed cases
        ("Madam, I'm Adam", True),
        ("Able was I ere I saw Elba", True),
        ("Taco cat", True),
        ("Taco cat!", True),
        ("A Toyota! Race fast, safe car! A Toyota!", True),
        ("Was it a rat I saw?", True),
        ("A Santa at NASA", True),
        ("Some men interpret nine memos", True),
        ("Too hot to hoot", True),
        ("Not a palindrome!", False),

        # whitespace-only / punctuation-only
        (" ", True),
        ("   ", True),
        ("\t", True),
        ("\n", True),
        ("!!!???", True),
        ("! ! !", True),
        ("  a  ", True),
        ("  abc  ", False),
        (" \t a \t ", True),
        (" \t abc \t ", False),
    ]

    for value, expected in cases:
        check(
            f"py_echo_validator({value!r})",
            module.py_echo_validator(value),
            expected
        )


def test_py_pattern_tracker(module):

    cases = [
        # basic cases
        ("12", 1),
        ("23", 1),
        ("34", 1),
        ("89", 1),
        ("01", 1),
        ("99", 0),
        ("98", 0),
        ("21", 0),
        ("10", 0),

        # multiple patterns
        ("123", 2),
        ("1234", 3),
        ("12345", 4),
        ("123456789", 8),
        ("0123456789", 9),
        ("1123", 2),
        ("1223", 2),
        ("1233", 2),
        ("112233", 2),

        # broken sequences
        ("13", 0),
        ("14", 0),
        ("15", 0),
        ("124", 1),
        ("125", 1),
        ("132", 0),
        ("1235", 2),
        ("1245", 2),
        ("1357", 0),

        # letters between digits
        ("1a2", 0),
        ("1b2", 0),
        ("12a3", 1),
        ("1a23", 1),
        ("12a34", 2),
        ("123a4", 2),
        ("1a2b3", 0),
        ("a12", 1),
        ("12a", 1),
        ("a123", 2),
        ("123a", 2),

        # digits mixed with letters
        ("a1b2c3", 0),
        ("a12b34c", 2),
        ("12abc34", 2),
        ("abc123", 2),
        ("123abc", 2),
        ("a123z", 2),
        ("x12y23z", 2),

        # repeated and descending digits
        ("11", 0),
        ("22", 0),
        ("33", 0),
        ("44", 0),
        ("55", 0),
        ("66", 0),
        ("77", 0),
        ("88", 0),
        ("99", 0),
        ("9876543210", 0),
        ("54321", 0),
        ("210", 0),

        # special cases
        ("", 0),
        ("1", 0),
        ("a", 0),
        ("ab", 0),
        ("!", 0),
        ("!@#$", 0),
        ("12!", 1),
        ("!12", 1),
        ("1!2", 0),
        ("123!", 2),
        ("!123!", 2),
        (" 12 ", 1),
        ("1 2", 0),
        ("1\t2", 0),

        # longer mixed cases
        ("1234567890", 8),
        ("0987654321", 0),
        ("001122334455", 5),
        ("102132435465", 0),
        ("121314151617", 1),
        ("123abc456", 4),
        ("abc123xyz456", 4),
        ("12x34x56", 3),
        ("12-34-56", 3),
        ("12.34.56", 3),

        # boundary cases
        ("89a", 1),
        ("a89", 1),
        ("789", 2),
        ("789a", 2),
        ("a789", 2),
        ("6789", 3),
        ("67890", 3),
        ("78901", 3),

        # unicode and non-ascii characters
        ("1é2", 0),
        ("é12", 1),
        ("12é", 1),
        ("é123", 2),
        ("123é", 2),
    ]

    for value, expected in cases:
        check(
            f"pattern_tracker({value!r})",
            module.pattern_tracker(value),
            expected
        )


def test_rotate_90(module):

    cases = [
        # basic cases
        ([[1]], [[1]]),
        ([[1, 2], [3, 4]], [[3, 1], [4, 2]]),
        ([[1, 2, 3], [4, 5, 6], [7, 8, 9]],
         [[7, 4, 1], [8, 5, 2], [9, 6, 3]]),

        # larger matrices
        ([[1, 2, 3, 4],
          [5, 6, 7, 8],
          [9, 10, 11, 12],
          [13, 14, 15, 16]],
         [[13, 9, 5, 1],
          [14, 10, 6, 2],
          [15, 11, 7, 3],
          [16, 12, 8, 4]]),

        ([[1, 2, 3, 4, 5],
          [6, 7, 8, 9, 10],
          [11, 12, 13, 14, 15],
          [16, 17, 18, 19, 20],
          [21, 22, 23, 24, 25]],
         [[21, 16, 11, 6, 1],
          [22, 17, 12, 7, 2],
          [23, 18, 13, 8, 3],
          [24, 19, 14, 9, 4],
          [25, 20, 15, 10, 5]]),

        # negative numbers
        ([[-1, -2], [-3, -4]], [[-3, -1], [-4, -2]]),
        ([[-1, -2, -3],
          [-4, -5, -6],
          [-7, -8, -9]],
         [[-7, -4, -1],
          [-8, -5, -2],
          [-9, -6, -3]]),

        # zeros
        ([[0, 0], [0, 0]], [[0, 0], [0, 0]]),
        ([[0, 1], [2, 3]], [[2, 0], [3, 1]]),
        ([[0, 0, 1],
          [0, 2, 0],
          [3, 0, 0]],
         [[3, 0, 0],
          [0, 2, 0],
          [0, 0, 1]]),

        # duplicate values
        ([[1, 1], [1, 1]], [[1, 1], [1, 1]]),
        ([[1, 2], [2, 1]], [[2, 1], [1, 2]]),
        ([[1, 2, 1],
          [2, 3, 2],
          [1, 2, 1]],
         [[1, 2, 1],
          [2, 3, 2],
          [1, 2, 1]]),

        # negative and positive values
        ([[-1, 0], [0, 1]], [[0, -1], [1, 0]]),
        ([[-3, -2, -1],
          [0, 1, 2],
          [3, 4, 5]],
         [[3, 0, -3],
          [4, 1, -2],
          [5, 2, -1]]),

        # strings
        ([["a", "b"], ["c", "d"]], [["c", "a"], ["d", "b"]]),
        ([["a", "b", "c"],
          ["d", "e", "f"],
          ["g", "h", "i"]],
         [["g", "d", "a"],
          ["h", "e", "b"],
          ["i", "f", "c"]]),

        # single row/column is not valid because input is assumed square
        # empty matrix
        ([], []),

        # special values
        ([[True]], [[True]]),
        ([[None]], [[None]]),
        ([[1, None], [None, 2]],
         [[None, 1], [2, None]]),

        # already rotationally symmetric
        ([[1, 2], [2, 1]], [[2, 1], [1, 2]]),
        ([[1, 2, 1],
          [2, 3, 2],
          [1, 2, 1]],
         [[1, 2, 1],
          [2, 3, 2],
          [1, 2, 1]]),

        # negative and zero mix
        ([[-5, 0, 5],
          [-4, 0, 4],
          [-3, 0, 3]],
         [[-3, -4, -5],
          [0, 0, 0],
          [3, 4, 5]]),

        # sequential values with a different layout
        ([[9, 8, 7],
          [6, 5, 4],
          [3, 2, 1]],
         [[3, 6, 9],
          [2, 5, 8],
          [1, 4, 7]]),

        # repeated rows
        ([[1, 2, 3],
          [1, 2, 3],
          [1, 2, 3]],
         [[1, 1, 1],
          [2, 2, 2],
          [3, 3, 3]]),

        # repeated columns
        ([[1, 1, 1],
          [2, 2, 2],
          [3, 3, 3]],
         [[3, 2, 1],
          [3, 2, 1],
          [3, 2, 1]]),
    ]

    for value, expected in cases:
        original = [row.copy() for row in value]

        result = module.rotate_90(value)

        check(
            f"rotate_90({value!r})",
            (result, value),
            (expected, original),
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
    actual = output.getvalue().splitlines()
    check(
        "sorted",
        actual,
        expected,
    )


def test_top_k_frequent(module):

    cases = [
        # basic cases
        ([1, 2, 2, 3, 3, 3], 2, [3, 2]),
        ([1, 1, 2, 2, 3], 2, [1, 2]),
        ([1, 1, 1, 2, 3], 1, [1]),
        ([1, 2, 3], 2, [1, 2]),
        ([1, 2, 3], 3, [1, 2, 3]),
        ([5, 5, 5, 5], 1, [5]),
        ([5, 5, 5, 5], 0, []),

        # increasing frequencies
        ([1, 2, 2, 3, 3, 3], 1, [3]),
        ([1, 2, 2, 3, 3, 3], 2, [3, 2]),
        ([1, 2, 2, 3, 3, 3], 3, [1, 2, 3]),
        ([1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 2, [4, 3]),
        ([1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 3, [4, 3, 2]),
        ([1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 4, [1, 2, 3, 4]),

        # equal frequencies
        ([1, 2, 3, 4], 2, [1, 2]),
        ([1, 2, 3, 4], 3, [1, 2, 3]),
        ([1, 1, 2, 2, 3, 3], 2, [1, 2]),
        ([1, 1, 2, 2, 3, 3], 3, [1, 2, 3]),
        ([1, 1, 1, 2, 2, 2, 3, 3, 3], 2, [1, 2]),
        ([1, 1, 2, 2, 3, 3, 4, 4], 3, [1, 2, 3]),

        # single unique element
        ([7], 1, [7]),
        ([7, 7], 1, [7]),
        ([7, 7, 7], 1, [7]),
        ([0], 1, [0]),
        ([-1], 1, [-1]),

        # negative numbers
        ([-1, -2, -2, -3, -3, -3], 2, [-3, -2]),
        ([-1, -1, -2, -3, -3], 2, [-1, -3]),
        ([-5, -5, -5, -4, -4, -3], 2, [-5, -4]),
        ([-10, -10, -9, -8, -8, -8], 1, [-8]),
        ([-10, -10, -9, -8, -8, -8], 2, [-8, -10]),

        # zero
        ([0, 0, 1, 1, 1], 1, [1]),
        ([0, 0, 1, 1, 1], 2, [1, 0]),
        ([0, 0, 0, 1, 1, 2], 2, [0, 1]),
        ([0, 1, 1, 2, 2, 2], 3, [2, 1, 0]),

        # negative and positive mix
        ([-2, -2, -1, 0, 0, 0, 1], 2, [0, -2]),
        ([-2, -2, -1, 0, 0, 0, 1, 1], 3, [0, -2, 1]),
        ([-3, -3, -2, -2, -2, 1, 1], 2, [-2, -3]),

        # repeated patterns
        ([1, 1, 1, 2, 2, 3, 4], 2, [1, 2]),
        ([1, 1, 1, 2, 2, 2, 3], 2, [1, 2]),
        ([1, 1, 1, 2, 2, 3, 3], 2, [1, 2]),
        ([1, 1, 2, 2, 3, 3, 3, 4], 2, [3, 1]),
        ([1, 1, 2, 2, 3, 3, 4, 4, 4, 5], 1, [4]),

        # larger cases
        (
            [1, 1, 1, 2, 2, 3, 3, 3, 3, 4, 4, 5],
            3,
            [3, 1, 2],
        ),
        (
            [1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5],
            4,
            [4, 3, 2, 5],
        ),
        (
            [10, 10, 10, 20, 20, 30, 30, 30, 30, 40],
            3,
            [30, 10, 20],
        ),
        (
            [100, 100, 200, 200, 200, 300, 300, 400],
            2,
            [200, 100],
        ),

        # shuffled input order
        ([3, 1, 2, 3, 2, 3], 2, [3, 2]),
        ([2, 3, 1, 3, 2, 3], 2, [3, 2]),
        ([4, 1, 4, 2, 1, 4, 2, 2], 2, [4, 2]),
        ([5, 3, 5, 1, 3, 5, 3], 2, [5, 3]),

        # all unique
        ([10, 20, 30, 40, 50], 1, [10]),
        ([10, 20, 30, 40, 50], 2, [10, 20]),
        ([10, 20, 30, 40, 50], 4, [10, 20, 30, 40]),
        ([10, 20, 30, 40, 50], 5, [10, 20, 30, 40, 50]),

        # special cases
        ([], 0, []),
        ([1], 0, []),
        ([1, 2, 3], 0, []),
        ([0, 0, 0], 0, []),
        ([-1, -1], 0, []),
    ]

    for nums, k, expected in cases:
        result = module.topKFrequent(nums, k)
        frequencies = Counter(nums)

        correct_elements = set(result) == set(expected)
        correct_length = len(result) == k
        correct_order = all(
            frequencies[result[i]] >= frequencies[result[i + 1]]
            for i in range(len(result) - 1)
        )
        no_duplicates = len(result) == len(set(result))

        check(
            f"topKFrequent({nums!r}, {k})",
            correct_elements
            and correct_length
            and correct_order
            and no_duplicates,
        )


def test_two_sum(module):

    cases = [
        # basic cases
        ([2, 7, 11, 15], 9, [0, 1]),
        ([5, 5], 10, [0, 1]),
        ([2, 3], 5, [0, 1]),
        ([1, 4], 5, [0, 1]),
        ([3, 7], 10, [0, 1]),
        ([10, 20], 30, [0, 1]),
        ([0, 1], 1, [0, 1]),
        ([-1, 1], 0, [0, 1]),
        ([-5, 5], 0, [0, 1]),
        ([-3, -2], -5, [0, 1]),

        # solution at different positions
        ([1, 2, 3, 7], 10, [2, 3]),
        ([1, 2, 3, 7], 4, [0, 2]),
        ([1, 2, 3, 7], 3, [0, 1]),
        ([1, 2, 3, 7], 8, [0, 3]),
        ([4, 9, 1, 6], 10, [1, 2]),
        ([4, 9, 1, 6], 5, [0, 2]),
        ([4, 9, 1, 6], 7, [2, 3]),
        ([8, 2, 5, 3], 7, [1, 2]),
        ([8, 2, 5, 3], 5, [1, 3]),
        ([8, 2, 5, 3], 13, [0, 2]),

        # idk
        ([3, 3, 8], 6, [0, 1]),
        ([4, 4, 10], 8, [0, 1]),
        ([1, 1, 2, 8], 10, [2, 3]),
        ([2, 2, 5, 9], 11, [1, 3]),
        ([7, 7, 1, 4], 11, [1, 3]),
        ([5, 4, 1, 3], 9, [0, 1]),
        ([6, 1, 6, 4], 12, [0, 2]),
        ([2, 9, 2, 7], 4, [0, 2]),

        # negative numbers
        ([-1, -2, -3, -4], -5, [1, 2]),
        ([-1, -2, -3, 5], 2, [2, 3]),
        ([-8, -3, 1, 4], -4, [0, 3]),
        ([-9, -2, 3, 8], -1, [0, 3]),
        ([-7, -4, 2, 6], -1, [0, 3]),
        ([-6, 1, 2, 10], 4, [0, 3]),
        ([-4, -1, 3, 8], 7, [1, 3]),
        ([-3, 1, 4, 6], 3, [0, 3]),

        # zero and positives
        ([0, 0, 1, 2], 0, [0, 1]),
        ([0, 1, 2, 3], 4, [1, 3]),
        ([0, 4, 6, 9], 10, [1, 2]),
        ([0, 5, 7, 11], 12, [1, 2]),
        ([0, 6, 8, 13], 14, [1, 2]),
        ([0, 7, 9, 15], 16, [1, 2]),

        # solution near the middle
        ([8, 3, 7, 2, 5], 9, [2, 3]),
        ([4, 11, 6, 1, 9], 7, [2, 3]),
        ([5, 9, 1, 6, 2], 14, [0, 1]),
        ([12, 5, 8, 3, 10], 22, [0, 4]),
        ([7, 2, 14, 6, 1], 16, [1, 2]),
        ([3, 10, 5, 8, 2], 5, [0, 4]),
        ([9, 4, 6, 1, 7], 16, [0, 4]),

        # larger arrays
        ([1, 4, 7, 10, 13, 16], 23, [3, 4]),
        ([2, 5, 8, 11, 14, 17], 25, [3, 4]),
        ([3, 6, 9, 12, 15, 18], 30, [3, 5]),
        ([5, 10, 15, 20, 25, 30], 55, [4, 5]),
        ([1, 3, 5, 7, 9, 11, 13], 4, [0, 1]),
        ([2, 4, 6, 8, 10, 12, 14], 6, [0, 1]),
        ([10, 20, 30, 40, 50, 60], 30, [0, 1]),
        ([11, 22, 33, 44, 55, 66], 33, [0, 1]),

        # larger values
        ([99999, 1, 500, 2500], 100499, [0, 2]),
        ([123456, 654321, 111111], 234567, [0, 2]),
        ([1000000, 2, 3, 999999], 1000002, [0, 1]),
    ]

    for nums, target, expected in cases:
        try:
            result = module.twoSum(nums, target)

            check(
                f"twoSum({nums!r}, {target})",
                (len(result), set(result)),
                (2, set(expected)),
            )

        except Exception as e:
            print(
                f"test {test_number + 1} || "
                f"twoSum({nums!r}, {target}): FAIL"
            )
            print(f"       Expected: {expected!r}")
            print(f"       Got:      {type(e).__name__}: {e}")
            raise SystemExit(1)


def test_valid_anagram(module):

    cases = [
        # basic cases
        ("racecar", "carrace", True),
        ("jar", "jam", False),
        ("", "", True),
        ("listen", "silent", True),
        ("aabbcc", "abcabc", True),
        ("abc", "ab", False),
        ("hello", "hello", True),
        ("hello", "olleh", True),
        ("world", "dlrow", True),
        ("python", "typhon", True),

        # short strings
        ("a", "a", True),
        ("a", "b", False),
        ("ab", "ba", True),
        ("ab", "aa", False),
        ("abc", "cba", True),
        ("abc", "cab", True),
        ("abc", "acb", True),
        ("abc", "abd", False),
        ("abcd", "dcba", True),
        ("abcd", "abce", False),

        # repeated letters
        ("aa", "aa", True),
        ("aa", "ab", False),
        ("aaa", "aaa", True),
        ("aaa", "aa", False),
        ("aab", "aba", True),
        ("aab", "abb", False),
        ("abb", "bba", True),
        ("abb", "baa", False),
        ("aabb", "bbaa", True),
        ("aabb", "abab", True),

        # longer common words
        ("evil", "vile", True),
        ("evil", "live", True),
        ("evil", "veil", True),
        ("dusty", "study", True),
        ("angel", "glean", True),
        ("angle", "glean", True),
        ("below", "elbow", True),
        ("night", "thing", True),
        ("state", "taste", True),
        ("save", "vase", True),

        # common false anagrams
        ("evil", "vilex", False),
        ("dusty", "studyx", False),
        ("angel", "gleanx", False),
        ("below", "elbows", False),
        ("night", "thingy", False),
        ("state", "tastee", False),
        ("save", "vases", False),
        ("listen", "listens", False),
        ("triangle", "integralx", False),
        ("binary", "brainy", True),

        # longer true anagrams
        ("triangle", "integral", True),
        ("integral", "altering", True),
        ("conversation", "conservation", True),
        ("earth", "heart", True),
        ("heart", "earth", True),
        ("cheaters", "teachers", True),
        ("cheaters", "hectares", True),
        ("schoolmaster", "theclassroom", True),
        ("theeyes", "theysee", True),
        ("astronomer", "moonstarer", True),

        # duplicates and counts
        ("aaaab", "aabaa", True),
        ("aaaab", "aaaba", True),
        ("aaaab", "abaaa", True),
        ("aaaab", "abaaa", True),
        ("aabbbaa", "baaabba", True),
        ("aabbbaa", "abababa", True),
        ("aabbccdd", "ddccbbaa", True),
        ("aabbccdd", "abcdabcd", True),
        ("aaaabbbb", "bbaaaabb", True),
        ("aabcc", "ccaba", True),

        # false due to one count differing
        ("aabbcc", "aabbcd", False),
        ("aabbcc", "aabccc", False),
        ("aabbcc", "abbccc", False),
        ("aaabbb", "aabbbb", False),
        ("aaabbb", "aaaabb", False),
        ("abcd", "abcdd", False),
        ("abcd", "abcc", False),
        ("aabb", "aaab", False),
        ("aabbcc", "aabbc", False),
        ("abcabc", "abcabd", False),

        # numbers
        ("123", "321", True),
        ("12345", "54321", True),
        ("112233", "332211", True),
        ("112233", "123123", True),
        ("123123", "321321", True),
        ("1001", "0110", True),
        ("1001", "1010", True),
        ("112358", "835211", True),
        ("1234567890", "0987654321", True),
        ("1234", "1245", False),

        # letters and numbers
        ("a1b2", "2b1a", True),
        ("abc123", "321cba", True),
        ("a1a2", "2aa1", True),
        ("a1b1", "1ab1", True),
        ("a1b2c3", "3c2b1a", True),
        ("a1b2", "a1b3", False),
        ("abc123", "abc124", False),
        ("aabb11", "11bbaa", True),
        ("1122aa", "aa2211", True),
        ("123abc", "abc124", False),
    ]

    for first, second, expected in cases:
        result = module.valid_anagram(first, second)
        check(
            f"valid_anagram({first!r}, {second!r})",
            result,
            expected,
        )


def test_whisper_lipher(module):

    cases = [
        # basic cases
        ("Hello, World!", 3, "Khoor, Zruog!"),
        ("abc", 1, "bcd"),
        ("xyz", 2, "zab"),
        ("A1!", 26, "A1!"),
        ("", 5, ""),
        ("a", 1, "b"),
        ("z", 1, "a"),
        ("A", 1, "B"),
        ("Z", 1, "A"),
        ("abc", 0, "abc"),

        # zero and full rotations
        ("ABC", 0, "ABC"),
        ("abc", 26, "abc"),
        ("ABC", 52, "ABC"),
        ("abc", -1, "zab"),
        ("ABC", -1, "ZAB"),
        ("short", 52, "short"),
        ("LONG", 104, "LONG"),
        ("wrap ZAP", 52, "wrap ZAP"),
        ("Edge Case!", -26, "Edge Case!"),
        ("Edge Case!", -27, "Dcfd Bzrd!"),

        # uppercase and lowercase
        ("Hello", 5, "Mjqqt"),
        ("hello", 5, "mjqqt"),
        ("HELLO", 5, "MJQQT"),
        ("Hello", 25, "Gdkkn"),
        ("Hello", -5, "Czggj"),
        ("az", 1, "ba"),
        ("AZ", 1, "BA"),
        ("za", 1, "ab"),
        ("ZA", 1, "AB"),
        ("aZ", 1, "bA"),

        # wraparound
        ("Zz", 1, "Aa"),
        ("Aa", 25, "Zz"),
        ("Bb", 25, "Aa"),
        ("zebra", 1, "afcsb"),
        ("ZEBRA", 1, "AFCSB"),
        ("zebra", 2, "bgdtc"),
        ("ZEBRA", 2, "BGDTC"),
        ("abcdefghijklmnopqrstuvwxyz", 1,
         "bcdefghijklmnopqrstuvwxyza"),
        ("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 1,
         "BCDEFGHIJKLMNOPQRSTUVWXYZA"),

        # large positive and negative shifts
        ("abcdefghijklmnopqrstuvwxyz", 25,
         "zabcdefghijklmnopqrstuvwxy"),
        ("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 25,
         "ZABCDEFGHIJKLMNOPQRSTUVWXY"),
        ("abcdefghijklmnopqrstuvwxyz", 26,
         "abcdefghijklmnopqrstuvwxyz"),
        ("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 52,
         "ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
        ("Shifting Letters", 100, "Odebpejc Happano"),
        ("Same Shift", 39, "Fnzr Fuvsg"),
        ("Another Test", 14, "Obchvsf Hsgh"),
        ("qwerty", -3, "ntboqv"),
        ("QWERTY", -3, "NTBOQV"),

        # mixed case
        ("abcXYZ", 3, "defABC"),
        ("xyzABC", 3, "abcDEF"),
        ("abcXYZ", 23, "xyzUVW"),
        ("xyzABC", 23, "uvwXYZ"),
        ("AaBbCc", 1, "BbCcDd"),
        ("ZzYyXx", 1, "AaZzYy"),
        ("AaBbCc", -1, "ZzAaBb"),
        ("ZzYyXx", -1, "YyXxWw"),
        ("Hello WORLD", 13, "Uryyb JBEYQ"),
        ("HELLO world", 13, "URYYB jbeyq"),

        # spaces and punctuation
        ("The quick brown fox", 3,
         "Wkh txlfn eurzq ira"),
        ("The Quick Brown Fox", 3,
         "Wkh Txlfn Eurzq Ira"),
        ("the quick brown fox", 3,
         "wkh txlfn eurzq ira"),
        ("Pack my box!", 13, "Cnpx zl obk!"),
        ("Jump over 2 lazy dogs.", 7,
         "Qbtw vcly 2 shgf kvnz."),
        ("1234567890", 10, "1234567890"),
        ("!@#$%^&*()", 7, "!@#$%^&*()"),
        ("Hello, 123!", 1, "Ifmmp, 123!"),
        ("Hello, 123!", -1, "Gdkkn, 123!"),
        ("a-b-c", 1, "b-c-d"),

        # symbols and separators
        ("A-B-C", 1, "B-C-D"),
        ("a_b_c", 2, "c_d_e"),
        ("A_B_C", 2, "C_D_E"),
        ("one\ttwo\nthree", 1,
         "pof\tuxp\nuisff"),
        ("Hello... goodbye!!!", 19,
         "Axeeh... zhhwurx!!!"),
        ("Punctuation, stays!", 6,
         "Vatizagzout, yzgey!"),
        ("Numbers 123", 4, "Ryqfivw 123"),
        ("42 is cool!", 5, "42 nx httq!"),
        ("Rotate 90°", 4, "Vsxexi 90°"),

        # full alphabet
        ("abcdefghijklmnopqrstuvwxyz", 5,
         "fghijklmnopqrstuvwxyzabcde"),
        ("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 5,
         "FGHIJKLMNOPQRSTUVWXYZABCDE"),
        ("abcdefghijklmnopqrstuvwxyz", -5,
         "vwxyzabcdefghijklmnopqrstu"),
        ("ABCDEFGHIJKLMNOPQRSTUVWXYZ", -5,
         "VWXYZABCDEFGHIJKLMNOPQRSTU"),
        ("abcde", 25, "zabcd"),
        ("ABCDE", 25, "ZABCD"),
        ("vwxyz", 5, "abcde"),
        ("VWXYZ", 5, "ABCDE"),
        ("mnopqr", 13, "zabcde"),
        ("A quick test.", 4, "E uymgo xiwx."),
        ("Caesar Cipher", 2, "Ecguct Ekrjgt"),
        ("Caesar Cipher", -2, "Aycqyp Agnfcp"),
        ("Python3", 10, "Zidryx3"),
        ("abc def", 7, "hij klm"),
        ("ABC DEF", 7, "HIJ KLM"),
        ("abc def", -7, "tuv wxy"),
        ("ABC DEF", -7, "TUV WXY"),
        ("lorem ipsum", 1, "mpsfn jqtvn"),
        ("Lorem Ipsum", 1, "Mpsfn Jqtvn"),

        ("TEST123", 1, "UFTU123"),
        ("test123", 1, "uftu123"),
        ("AaZz", 2, "CcBb"),
        ("AaZz", -2, "YyXx"),
        ("No spaces", 8, "Vw axikma"),
        ("No spaces", 18, "Fg khsuwk"),
        ("Mix3d CASE!", 9, "Vrg3m LJBN!"),
        ("Wraparound zzz AAA", 1,
         "Xsbqbspvoe aaa BBB"),
        ("mixedCASE123!", 17,
         "dzovuTRJV123!"),
        ("final_test", 22, "bejwh_paop"),
    ]

    for text, shift, expected in cases:
        check(
            f"whisper_lipher({text!r}, {shift})",
            module.whisper_lipher(text, shift),
            expected
        )


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
