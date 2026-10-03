"""Validate optional, observer-declared animal context; no identification claim."""
GROUPS = {'unknown', 'parrot', 'dog', 'cat', 'other_bird', 'other_mammal',
          'amphibian', 'reptile', 'fish', 'invertebrate', 'other_animal', 'multiple'}


def validate_animal(value):
    if not isinstance(value, dict) or set(value) != {'group', 'species', 'basis'}:
        raise ValueError('Invalid animal context fields.')
    species = value['species']
    if (not isinstance(value['group'], str) or value['group'] not in GROUPS
            or value['basis'] != 'observer-declared' or not isinstance(species, str)
            or len(species.encode('utf-16-le')) // 2 > 80 or species != species.strip()
            or any(ord(c) < 32 or ord(c) == 127 for c in species)):
        raise ValueError('Invalid observer-declared animal context.')
    return dict(value)
