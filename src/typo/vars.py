from .pytypes import *

low_letters = "abcdefghijklmnopqrstuvwxyz"
cap_letters = low_letters.upper()
letters = low_letters + cap_letters

digits = "0123456789"
alphanumerics = letters + digits

punctuation = "`~!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?"

all_characters = letters + digits + punctuation + ' '

filler_words = ["um", "uh", "like", "you know", "I mean"]


keyboard_proximity_map: dict[str, KeyboardProximity] = {
    '`': {
        'accidental_shift': '~',
        'bordering': ['1', 'q', '  '],
        'accidental_shift_bordering': ['!', 'Q', '  ']
    },

    '1': {
        'accidental_shift': '!',
        'bordering': ['`', '2', 'q', 'w', '  '],
        'accidental_shift_bordering': ['~', '@', 'Q', 'W', '  ']
    },

    '2': {
        'accidental_shift': '@',
        'bordering': ['1', '3', 'q', 'w', 'e'],
        'accidental_shift_bordering': ['!', '#', 'Q', 'W', 'E']
    },

    '3': {
        'accidental_shift': '#',
        'bordering': ['2', '4', 'w', 'e', 'r'],
        'accidental_shift_bordering': ['@', '$', 'W', 'E', 'R']
    },

    '4': {
        'accidental_shift': '$',
        'bordering': ['3', '5', 'e', 'r', 't'],
        'accidental_shift_bordering': ['#', '%', 'E', 'R', 'T']
    },

    '5': {
        'accidental_shift': '%',
        'bordering': ['4', '6', 'r', 't', 'y'],
        'accidental_shift_bordering': ['$', '^', 'R', 'T', 'Y']
    },

    '6': {
        'accidental_shift': '^',
        'bordering': ['5', '7', 't', 'y', 'u'],
        'accidental_shift_bordering': ['%', '&', 'T', 'Y', 'U']
    },

    '7': {
        'accidental_shift': '&',
        'bordering': ['6', '8', 'y', 'u', 'i'],
        'accidental_shift_bordering': ['^', '*', 'Y', 'U', 'I']
    },

    '8': {
        'accidental_shift': '*',
        'bordering': ['7', '9', 'u', 'i', 'o'],
        'accidental_shift_bordering': ['&', '(', 'U', 'I', 'O']
    },

    '9': {
        'accidental_shift': '(',
        'bordering': ['8', '0', 'i', 'o', 'p'],
        'accidental_shift_bordering': ['*', ')', 'I', 'O', 'P']
    },

    '0': {
        'accidental_shift': ')',
        'bordering': ['9', '-', 'o', 'p', '['],
        'accidental_shift_bordering': ['(', '_', 'O', 'P', '{']
    },

    '-': {
        'accidental_shift': '_',
        'bordering': ['0', '=', 'p', '[', ']'],
        'accidental_shift_bordering': [')', '+', 'P', '{', '}']
    },

    '=': {
        'accidental_shift': '+',
        'bordering': ['-', '[', ']', '\\'],
        'accidental_shift_bordering': ['_', '{', '}', '|']
    },

    'q': {
        'accidental_shift': 'Q',
        'bordering': ['`', '1', '2', 'w', 'a', 's', '  '],
        'accidental_shift_bordering': ['~', '!', '@', 'W', 'A', 'S', '  ']
    },

    'w': {
        'accidental_shift': 'W',
        'bordering': ['1', '2', '3', 'q', 'e', 'a', 's', 'd'],
        'accidental_shift_bordering': ['!', '@', '#', 'Q', 'E', 'A', 'S', 'D']
    },

    'e': {
        'accidental_shift': 'E',
        'bordering': ['2', '3', '4', 'w', 'r', 's', 'd', 'f'],
        'accidental_shift_bordering': ['@', '#', '$', 'W', 'R', 'S', 'D', 'F']
    },

    'r': {
        'accidental_shift': 'R',
        'bordering': ['3', '4', '5', 'e', 't', 'd', 'f', 'g'],
        'accidental_shift_bordering': ['#', '$', '%', 'E', 'T', 'D', 'F', 'G']
    },

    't': {
        'accidental_shift': 'T',
        'bordering': ['4', '5', '6', 'r', 'y', 'f', 'g', 'h'],
        'accidental_shift_bordering': ['$', '%', '^', 'R', 'Y', 'F', 'G', 'H']
    },

    'y': {
        'accidental_shift': 'Y',
        'bordering': ['5', '6', '7', 't', 'u', 'g', 'h', 'j'],
        'accidental_shift_bordering': ['%', '^', '&', 'T', 'U', 'G', 'H', 'J']
    },

    'u': {
        'accidental_shift': 'U',
        'bordering': ['6', '7', '8', 'y', 'i', 'h', 'j', 'k'],
        'accidental_shift_bordering': ['^', '&', '*', 'Y', 'I', 'H', 'J', 'K']
    },

    'i': {
        'accidental_shift': 'I',
        'bordering': ['7', '8', '9', 'u', 'o', 'j', 'k', 'l'],
        'accidental_shift_bordering': ['&', '*', '(', 'U', 'O', 'J', 'K', 'L']
    },

    'o': {
        'accidental_shift': 'O',
        'bordering': ['8', '9', '0', 'i', 'p', 'k', 'l', ';'],
        'accidental_shift_bordering': ['*', '(', ')', 'I', 'P', 'K', 'L', ':']
    },

    'p': {
        'accidental_shift': 'P',
        'bordering': ['9', '0', '-', 'o', '[', 'l', ';', '\''],
        'accidental_shift_bordering': ['(', ')', '_', 'O', '{', 'L', ':', '"']
    },

    '[': {
        'accidental_shift': '{',
        'bordering': ['0', '-', '=', 'p', ']', ';', '\'', '\\'],
        'accidental_shift_bordering': [')', '_', '+', 'P', '}', ':', '"', '|']
    },

    ']': {
        'accidental_shift': '}',
        'bordering': ['-', '=', '\\', '[', '\'', '\n'],
        'accidental_shift_bordering': ['_', '+', '|', '{', '"', '\n']
    },

    '\\': {
        'accidental_shift': '|',
        'bordering': ['=', ']', '\n'],
        'accidental_shift_bordering': ['+', '}', '\n']
    },

    'a': {
        'accidental_shift': 'A',
        'bordering': ['q', 'w', 's', 'z', '  ', 'x'],
        'accidental_shift_bordering': ['Q', 'W', 'S', 'Z', '  ', 'X']
    },

    's': {
        'accidental_shift': 'S',
        'bordering': ['q', 'w', 'e', 'a', 'd', 'z', 'x', 'c'],
        'accidental_shift_bordering': ['Q', 'W', 'E', 'A', 'D', 'Z', 'X', 'C']
    },

    'd': {
        'accidental_shift': 'D',
        'bordering': ['w', 'e', 'r', 's', 'f', 'x', 'c', 'v'],
        'accidental_shift_bordering': ['W', 'E', 'R', 'S', 'F', 'X', 'C', 'V']
    },

    'f': {
        'accidental_shift': 'F',
        'bordering': ['e', 'r', 't', 'd', 'g', 'c', 'v', 'b'],
        'accidental_shift_bordering': ['R', 'T', 'D', 'G', 'C', 'V', 'B']
    },

    'g': {
        'accidental_shift': 'G',
        'bordering': ['r', 't', 'y', 'f', 'h', 'v', 'b', 'n'],
        'accidental_shift_bordering': ['R', 'T', 'Y', 'F', 'H', 'V', 'B', 'N']
    },

    'h': {
        'accidental_shift': 'H',
        'bordering': ['t', 'y', 'u', 'g', 'j', 'b', 'n', 'm'],
        'accidental_shift_bordering': ['T', 'Y', 'U', 'G', 'J', 'B', 'N', 'M']
    },

    'j': {
        'accidental_shift': 'J',
        'bordering': ['y', 'u', 'i', 'h', 'k', 'n', 'm', ','],
        'accidental_shift_bordering': ['Y', 'U', 'I', 'H', 'K', 'N', 'M', '<']
    },

    'k': {
        'accidental_shift': 'K',
        'bordering': ['u', 'i', 'o', 'j', 'l', 'm', ',', '.'],
        'accidental_shift_bordering': ['U', 'I', 'O', 'J', 'L', 'M', '<', '>']
    },

    'l': {
        'accidental_shift': 'L',
        'bordering': ['i', 'o', 'p', 'k', ';', ',', '.'],
        'accidental_shift_bordering': ['I', 'O', 'P', 'K', ':', '<', '>']
    },

    ';': {
        'accidental_shift': ':',
        'bordering': ['o', 'p', '[', 'l', '\'', '.', '/'],
        'accidental_shift_bordering': ['O', 'P', '{', 'L', '"', '>', '?']
    },

    '\'': {
        'accidental_shift': '"',
        'bordering': ['p', '[', ']', ';', '\\'],
        'accidental_shift_bordering': ['P', '{', '}', ':', '|']
    },

    'z': {
        'accidental_shift': 'Z',
        'bordering': ['a', 's', 'x'],
        'accidental_shift_bordering': ['A', 'S', 'X']
    },

    'x': {
        'accidental_shift': 'X',
        'bordering': ['a', 's', 'd', 'z', 'c', ' '],
        'accidental_shift_bordering': ['A', 'S', 'D', 'Z', 'C', ' ']
    },

    'c': {
        'accidental_shift': 'C',
        'bordering': ['s', 'd', 'f', 'x', 'v', ' '],
        'accidental_shift_bordering': ['S', 'D', 'F', 'X', 'V', ' ']
    },

    'v': {
        'accidental_shift': 'V',
        'bordering': ['d', 'f', 'g', 'c', 'b', ' '],
        'accidental_shift_bordering': ['D', 'F', 'G', 'C', 'B', ' ']
    },

    'b': {
        'accidental_shift': 'B',
        'bordering': ['f', 'g', 'h', 'v', 'n', ' '],
        'accidental_shift_bordering': ['F', 'G', 'H', 'V', 'N', ' ']
    },

    'n': {
        'accidental_shift': 'N',
        'bordering': ['g', 'h', 'j', 'b', 'm', ' '],
        'accidental_shift_bordering': ['G', 'H', 'J', 'B', 'M', ' ']
    },

    'm': {
        'accidental_shift': 'M',
        'bordering': ['h', 'j', 'k', 'n', ','],
        'accidental_shift_bordering': ['H', 'J', 'K', 'N', '<']
    },

    ',': {
        'accidental_shift': '<',
        'bordering': ['j', 'k', 'l', 'm', '.', ' '],
        'accidental_shift_bordering': ['J', 'K', 'L', 'M', '>', ' ']
    },

    '.': {
        'accidental_shift': '>',
        'bordering': ['k', 'l', ';', ',', '/'],
        'accidental_shift_bordering': ['K', 'L', ':', '<', '?']
    },

    '/': {
        'accidental_shift': '?',
        'bordering': ['l', ';', '\'', '.'],
        'accidental_shift_bordering': ['L', ':', '"', '>']
    },

    ' ': {
        'accidental_shift': ' ',
        'bordering': ['x', 'c', 'v', 'b', 'n', 'm', ','],
        'accidental_shift_bordering': ['X', 'C', 'V', 'B', 'N', 'M', '<']
    },
}

def typo_vars_main():
    # Clone the map so we don't modify the original while iterating
    kpm = keyboard_proximity_map.copy()

    # Insert the opposites
    for key, value in kpm.items():
        accidental_shift = value['accidental_shift']
        bordering = value['bordering']
        accidental_shift_bordering = value['accidental_shift_bordering']

        if accidental_shift not in keyboard_proximity_map:
            keyboard_proximity_map[accidental_shift] = {
                'accidental_shift': key,
                'bordering': accidental_shift_bordering,
                'accidental_shift_bordering': bordering
            }

typo_vars_main()