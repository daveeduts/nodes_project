

def validate_unique_names(names):
    return len(names) == len(set(names))

def is_empty_or_duplicate(names):
    if not all(names):
        return "Some names are empty."
    if len(names) != len(set(names)):
        return "There are duplicates."
    return None
