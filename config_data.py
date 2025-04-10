# File: config_data.py
# Holds the game configuration data, similar to Config.pas/Config.dfm

# --- Sample Data (Needs full population based on DFM files) ---

RACES = {
    "Half Orc": {"bonuses": ["HP Max"]},
    "Half Man": {"bonuses": ["CHA"]},
    "Half Halfling": {"bonuses": ["DEX"]},
    "Double Hobbit": {"bonuses": ["STR"]},
    "Hob-Hobbit": {"bonuses": ["DEX", "CON"]},
    "Low Elf": {"bonuses": ["CON"]},
    "Dung Elf": {"bonuses": ["WIS"]},
    "Talking Pony": {"bonuses": ["MP Max", "INT"]},
    # ... add all races
    "Land Squid": {"bonuses": ["STR", "HP Max"]},
}

KLASSES = {
    "Ur-Paladin": {"bonuses": ["WIS", "CON"]},
    "Voodoo Princess": {"bonuses": ["INT", "CHA"]},
    "Robot Monk": {"bonuses": ["STR"]},
    "Mu-Fu Monk": {"bonuses": ["DEX"]},
    # ... add all classes
    "Vermineer": {"bonuses": ["INT"]},
}

WEAPONS = [
    ("Stick", 0), ("Broken Bottle", 1), ("Shiv", 1), ("Sprig", 1), ("Oxgoad", 1),
    ("Eelspear", 2), ("Bowie Knife", 2), ("Claw Hammer", 2), ("Handpeen", 2),
    # ... add all weapons
    ("Bandyclef", 15),
]

ARMORS = [
    ("Lace", 1), ("Macrame", 2), ("Burlap", 3), ("Canvas", 4), ("Flannel", 5),
    # ... add all armors
    ("Plasma", 30),
]

SHIELDS = [
    ("Parasol", 0), ("Pie Plate", 1), ("Garbage Can Lid", 2), ("Buckler", 3),
    # ... add all shields
    ("Magnetic Field", 18),
]

OFFENSE_ATTRIB = [
    ("Polished", 1), ("Serrated", 1), ("Heavy", 1), ("Pronged", 2), ("Steely", 2),
    ("Vicious", 3), ("Venomed", 4), ("Stabbity", 4), ("Dancing", 5),
    ("Invisible", 6), ("Vorpal", 7),
]

DEFENSE_ATTRIB = [
    ("Studded", 1), ("Banded", 2), ("Gilded", 2), ("Festooned", 3), ("Holy", 4),
    ("Cambric", 1), ("Fine", 4), ("Impressive", 5), ("Custom", 3),
]

OFFENSE_BAD = [
    ("Dull", -2), ("Tarnished", -1), ("Rusty", -3), ("Padded", -5), ("Bent", -4),
    ("Mini", -4), ("Rubber", -6), ("Nerf", -7), ("Unbalanced", -2),
]

DEFENSE_BAD = [
    ("Holey", -1), ("Patched", -1), ("Threadbare", -2), ("Faded", -1), ("Rusty", -3),
    ("Motheaten", -3), ("Mildewed", -2), ("Torn", -3), ("Dented", -3),
    ("Cursed", -5), ("Plastic", -4), ("Cracked", -4), ("Warped", -3), ("Corroded", -3),
]

SPELLS = [
    'Slime Finger', 'Rabbit Punch', 'Hastiness', 'Good Move', 'Sadness',
    'Seasick', 'Shoelaces', 'Inoculate', 'Cone of Annoyance', 'Magnetic Orb',
    # ... add all spells
    'Infinite Confusion',
]

BORING_ITEMS = [
    'nail', 'lunchpail', 'sock', 'I.O.U.', 'cookie', 'pint', 'toothpick',
    # ... add all boring items
    'writ',
]

SPECIALS = [ # Base name for special items
    'Diadem', 'Festoon', 'Gemstone', 'Phial', 'Tiara', 'Scabbard', 'Arrow',
    # ... add all specials
    'Vulpeculum',
]

ITEM_ATTRIB = [ # Prefixes for special items
    'Golden', 'Gilded', 'Spectral', 'Astral', 'Garlanded', 'Precious',
    # ... add all item attribs
    'Puissant',
]

ITEM_OFS = [ # Suffixes for special items ("of X")
    'Foreboding', 'Foreshadowing', 'Nervousness', 'Happiness', 'Torpor',
    # ... add all item ofs
    'Hydragyrum',
]

MONSTERS = [
    # (Name, Level, LootItem | * for generic)
    ("Anhkheg", 6, "chitin"), ("Ant", 0, "antenna"), ("Ape", 4, "ass"),
    ("Baluchitherium", 14, "ear"), ("Beholder", 10, "eyestalk"),
    ("Black Pudding", 10, "saliva"), ("Blink Dog", 4, "eyelid"),
    ("Cub Scout", 1, "neckerchief"), ("Girl Scout", 2, "cookie"),
    # ... add ALL monsters
    ("Fly", 0, "*"), ("Hogbird", 3, "curl"),
]

MONSTER_MODS = [
    # (LevelAdj, Pattern | * is placeholder)
    (-4, 'fötal *'), (-4, 'dying *'), (-3, 'crippled *'), (-3, 'baby *'),
    (-2, 'adolescent'), (-2, 'very sick *'), (-1, 'lesser *'), (-1, 'undernourished *'),
    (1, 'greater *'), (1, '* Elder'), (2, 'war *'), (2, 'Battle-*'),
    (3, 'Were-*'), (3, 'undead *'), (4, 'giant *'), (4, '* Rex'),
]

EQUIPMENT_SLOTS = [
    "Weapon", "Shield", "Helm", "Hauberk", "Brassairs", "Vambraces",
    "Gauntlets", "Gambeson", "Cuisses", "Greaves", "Sollerets"
]

TITLES = ['Mr.', 'Mrs.', 'Sir', 'Sgt.', 'Ms.', 'Captain', 'Chief', 'Admiral', 'Saint']
IMPRESSIVE_TITLES = ['King', 'Queen', 'Lord', 'Lady', 'Viceroy', 'Mayor', 'Prince', 'Princess', 'Chief', 'Boss', 'Archbishop', 'Baron', 'Comptroller']

NAME_PARTS = [
    # Consonants/clusters (start/mid)
    ['br', 'cr', 'dr', 'fr', 'gr', 'j', 'kr', 'l', 'm', 'n', 'pr', '', '', '', 'r', 'sh', 'tr', 'v', 'wh', 'x', 'y', 'z'],
    # Vowels
    ['a', 'a', 'e', 'e', 'i', 'i', 'o', 'o', 'u', 'u', 'ae', 'ie', 'oo', 'ou'],
    # Consonants (end/mid)
    ['b', 'ck', 'd', 'g', 'k', 'm', 'n', 'p', 't', 'v', 'x', 'z']
]

# --- Constants ---
BASE_ENCUMBRANCE = 10
SAVE_FILE_EXT = ".pq"
BACKUP_FILE_EXT = ".bak"
TIMER_INTERVAL_MS = 100 # How often the game logic timer fires

DARK_STYLESHEET = """
QWidget {
    background-color: #2b2b2b;
    color: #f0f0f0;
    font-size: 10pt;
}
QMainWindow::separator {
    background-color: #3a3a3a;
    width: 1px; /* when vertical */
    height: 1px; /* when horizontal */
}
QListView {
    background-color: #313131;
    border: 1px solid #3a3a3a;
    color: #d0d0d0;
}
QListView::item:selected {
    background-color: #4a4a4a;
    color: #ffffff;
}
QProgressBar {
    border: 1px solid #4a4a4a;
    border-radius: 3px;
    text-align: center;
    background-color: #313131;
    color: #f0f0f0;
}
QProgressBar::chunk {
    background-color: #5a9bcf; /* A blue progress color */
    width: 10px; /* Minimal chunk width */
    margin: 0.5px;
}
QStatusBar {
    background-color: #252525;
    color: #d0d0d0;
}
QLabel {
    color: #e0e0e0;
}
QLabel#HeaderLabel { /* Optional: Style specific labels differently */
    font-weight: bold;
    color: #cccccc;
}
QGroupBox {
    border: 1px solid #3a3a3a;
    margin-top: 1ex; /* leave space at the top for the title */
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left; /* position at the top center */
    padding: 0 3px;
    background-color: #2b2b2b;
    color: #e0e0e0;
}
QPushButton {
    background-color: #4a4a4a;
    border: 1px solid #5a5a5a;
    padding: 5px;
    min-width: 60px;
    color: #f0f0f0;
    border-radius: 3px;
}
QPushButton:hover {
    background-color: #5a5a5a;
}
QPushButton:pressed {
    background-color: #3a3a3a;
}
QPushButton:disabled {
    background-color: #313131;
    color: #707070;
}
QLineEdit, QComboBox, QListWidget {
    background-color: #313131;
    border: 1px solid #3a3a3a;
    padding: 3px;
    color: #f0f0f0;
}
QComboBox::drop-down {
    border: 0px;
}
QComboBox::down-arrow {
    image: url(down_arrow.png); /* You'd need an image or use default */
    width: 14px;
    height: 14px;
}
QDialog {
     background-color: #2b2b2b;
}
"""

# ----------------------------------------------------------------------------
# Helper Functions (Ported/Adapted from Delphi)
# ----------------------------------------------------------------------------
import random
import math
import re

def pick(items):
    """Pick a random item from a list."""
    if not items:
        return None
    return random.choice(items)

def pick_low(items):
    """Pick a random item, biased towards the lower end of the list."""
    if not items:
        return None
    idx1 = random.randint(0, len(items) - 1)
    idx2 = random.randint(0, len(items) - 1)
    return items[min(idx1, idx2)]

def odds(chance, outof):
    """Return True with a 'chance' out of 'outof' probability."""
    return random.randint(1, outof) <= chance

def rand_sign():
    """Return 1 or -1 randomly."""
    return random.choice([1, -1])

def ends(s, e):
    """Check if string s ends with string e."""
    return s.endswith(e)

def plural(s):
    """Basic English pluralization."""
    s_lower = s.lower()
    if not s: return ""
    if s_lower.endswith(('s', 'x', 'z', 'ch', 'sh')):
        return s + 'es'
    elif s_lower.endswith('y') and len(s) > 1 and s[-2].lower() not in 'aeiou':
        return s[:-1] + 'ies'
    elif s_lower.endswith('us'):
         return s[:-2] + 'i'
    elif s_lower.endswith('f'):
        return s[:-1] + 'ves'
    elif s_lower.endswith('fe'):
        return s[:-2] + 'ves'
    elif s_lower.endswith('man'):
        return s[:-3] + 'men'
    else:
        return s + 's'

def indefinite_article(s):
    """Return 'a' or 'an' based on the first letter of s."""
    if not s: return ""
    return 'an' if s[0].lower() in 'aeiou' else 'a'

def indefinite(s, qty):
    """Format a quantity and noun with indefinite article or pluralization."""
    if qty == 1:
        return f"{indefinite_article(s)} {s}"
    else:
        return f"{qty} {plural(s)}"

def definite(s, qty):
     """Format a quantity and noun with definite article and pluralization."""
     return f"the {plural(s) if qty > 1 else s}"

def int_to_roman(num):
    """Convert an integer to Roman numeral string."""
    if not isinstance(num, int) or not 0 < num < 40000: # Basic range check
        return str(num) # Or raise error

    val = [
        10000, 9000, 5000, 4000, 1000, 900, 500, 400,
        100, 90, 50, 40, 10, 9, 5, 4, 1
        ]
    syb = [
        "T", "MT", "A", "MA", "M", "CM", "D", "CD",
        "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"
        ]
    roman_num = ''
    i = 0
    while num > 0:
        for _ in range(num // val[i]):
            roman_num += syb[i]
            num -= val[i]
        i += 1
    return roman_num

def roman_to_int(s):
    """Convert a Roman numeral string to an integer."""
    s = s.upper()
    roman_map = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000, 'A': 5000, 'T': 10000}
    result = 0
    prev_value = 0
    # Handle subtractive cases like MT, MA, CM, CD, XC, XL, IX, IV
    s = s.replace("MT", "P") # Placeholder P=9000
    s = s.replace("MA", "Q") # Placeholder Q=4000
    s = s.replace("CM", "R") # Placeholder R=900
    s = s.replace("CD", "S") # Placeholder S=400
    s = s.replace("XC", "U") # Placeholder U=90
    s = s.replace("XL", "W") # Placeholder W=40
    s = s.replace("IX", "Y") # Placeholder Y=9
    s = s.replace("IV", "Z") # Placeholder Z=4

    roman_map.update({'P': 9000, 'Q': 4000, 'R': 900, 'S': 400, 'U': 90, 'W': 40, 'Y': 9, 'Z': 4})

    for numeral in s:
        value = roman_map.get(numeral)
        if value is None:
            try: return int(s) # Not a valid roman numeral string
            except ValueError: return 0
        result += value
    return result

def generate_name():
    """Generate a random fantasy-style name."""
    name = ""
    length = random.randint(4, 7) # Control name length
    for i in range(length):
        part_list = NAME_PARTS[i % len(NAME_PARTS)]
        name += pick(part_list)
    return name.capitalize()

def calculate_xp_for_level(level):
    """Calculate the total time (in seconds) needed to reach the *next* level."""
    # Corresponds to LevelUpTime in Delphi
    # This seems to be the *duration* of the level, not the cumulative XP
    base_time_seconds = 20 * 60 # ~20 minutes for level 1
    try:
        # Using math.pow for potentially large exponents
        level_factor = math.pow(1.15, level)
    except OverflowError:
        level_factor = float('inf') # Handle very high levels
    return round((20.0 + level_factor) * 60.0)

def rough_time(seconds):
    """Convert seconds into a human-readable duration string."""
    if seconds < 120:
        return f"{int(seconds)} seconds"
    elif seconds < 60 * 120:
        return f"{int(seconds / 60)} minutes"
    elif seconds < 60 * 60 * 48:
        return f"{int(seconds / 3600)} hours"
    else:
        return f"{int(seconds / (3600 * 24))} days"