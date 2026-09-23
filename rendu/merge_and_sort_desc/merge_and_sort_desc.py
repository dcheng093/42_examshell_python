def merge_and_sort_desc(list1: list[int], list2: list[int]) -> list[int]:
    return sorted(list1 + list2, reverse=True)
