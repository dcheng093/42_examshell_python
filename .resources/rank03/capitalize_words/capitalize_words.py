def capitalize_words(s: str) -> str:
    words = s.split(" ")
    capitalized_words = [word.capitalize() for word in words]
    return " ".join(capitalized_words)


print(capitalize_words("hello world"))           # "Hello World"
print(capitalize_words("42 madrid exam"))        # "42 Madrid Exam"
print(capitalize_words("  multiple   spaces "))  # "  Multiple   Spaces "
print(capitalize_words("mixed CASE letters"))    # "Mixed Case Letters"
