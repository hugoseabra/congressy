

def merge_lists_ignore_duplicates(first_list: list, second_list: list) -> list:
    in_first = set(first_list)
    in_second = set(second_list)

    in_second_but_not_in_first = in_second - in_first

    return first_list + list(in_second_but_not_in_first)