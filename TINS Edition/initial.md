Okay, this is a complex task. Generating a full, functional desktop application from a description and another language's source code is exactly what TINS *imagines* an LLM doing. However, current LLMs generate code based on patterns and examples, and accurately replicating the *entire* logic, UI nuances, and specific data handling of Progress Quest from Delphi to Python/PySide6 requires significant effort and likely iterative refinement.

I will provide a substantial starting point for the Progress Quest application in PySide6, incorporating the core UI structure, game loop concepts, and data structures described in the TINS README and derived from the Delphi code. It will include:

1.  **Basic UI Structure:** Using PySide6 components (`QMainWindow`, `QWidget`, `QListView`, `QProgressBar`, `QStatusBar`, etc.).
2.  **Dark Mode Styling:** Using a common dark theme QSS stylesheet.
3.  **Core Game Logic Stub:** A `GameLogic` class with state variables and a `tick` method.
4.  **Timer Integration:** A `QTimer` to drive the game loop.
5.  **Data Configuration Stub:** A separate module to hold the game data (monsters, items, etc.) similar to `Config.pas`/`Config.dfm`.
6.  **Helper Functions:** Stubs or basic implementations for procedural generation (names, items).
7.  **Character Creation Dialog Stub:** A basic dialog structure.
8.  **Main Application Setup.**

**Limitations:**

*   **Incomplete Logic:** The procedural generation, complex item/monster modification, specific quest logic, plot progression details, saving/loading, and multiplayer features will be placeholders or simplified. Implementing *all* of this accurately is beyond a single generation step.
*   **Data Conversion:** Manually converting *all* the data from the Delphi DFM files into Python structures is tedious and error-prone; I will include samples.
*   **Direct Delphi Replication:** This won't be a line-by-line translation. It's a conceptual reimplementation in Python/PySide6 based on the *description* and observed *structure*.

```python
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

```

```python
# File: game_logic.py
import random
import math
import time
from config_data import * # Import all data and helper functions

from PySide6.QtCore import QObject, Signal

class GameLogic(QObject):
    state_updated = Signal() # Signal emitted when UI needs refresh

    def __init__(self):
        super().__init__()
        self.character = {
            "Name": "Adventurer",
            "Race": "Human", # Default, overwritten on creation
            "Class": "Fighter", # Default
            "Level": 0, # Start at 0, first task levels to 1
            "Stats": {"STR": 10, "CON": 10, "DEX": 10, "INT": 10, "WIS": 10, "CHA": 10},
            "HPMax": 10,
            "MPMax": 10,
            "Equipment": {slot: "" for slot in EQUIPMENT_SLOTS},
            "Inventory": {"Gold Piece": 0}, # ItemName: Quantity
            "Spells": {}, # SpellName: RomanLevelString
            "Gold": 0,
            "Motto": "",
            "Guild": "",
        }
        self.plot_acts = ["Prologue"]
        self.quests = []

        # Progress Tracking (value, max_value)
        self.task_progress = 0
        self.task_max = 1 # Avoid division by zero initially
        self.task_description = "Initializing..."

        self.xp_progress = 0
        self.xp_max = calculate_xp_for_level(1) # XP needed for level 1

        self.quest_progress = 0
        self.quest_max = 10000 # Placeholder duration
        self.quest_description = "Awaiting orders"

        self.plot_progress = 0
        self.plot_max = 60 * 60 * 1000 # 1 hour in ms for prologue

        self.encumbrance = 0
        self.encumbrance_max = BASE_ENCUMBRANCE + self.character["Stats"]["STR"]

        self.current_target_monster = None # Store info about monster being fought
        self.last_tick_time = time.monotonic() * 1000 # Milliseconds

        self.game_loaded = False

    def initialize_new_character(self, name, race, klass, stats):
        """Set up the character after creation."""
        self.character["Name"] = name
        self.character["Race"] = race
        self.character["Class"] = klass
        self.character["Stats"] = stats
        self.character["Level"] = 0 # Start at level 0
        self.character["HPMax"] = random.randint(4, 8) + math.floor(stats.get("CON", 10) / 6)
        self.character["MPMax"] = random.randint(4, 8) + math.floor(stats.get("INT", 10) / 6)
        self.character["Equipment"]["Weapon"] = "Sharp Stick"
        self.character["Inventory"] = {"Gold Piece": 0}
        self.character["Spells"] = {}
        self.plot_acts = ["Prologue"]
        self.quests = []
        self.encumbrance_max = BASE_ENCUMBRANCE + self.character["Stats"]["STR"]
        self.xp_max = calculate_xp_for_level(1) # XP for level 1
        self.xp_progress = 0
        self.plot_progress = 0
        self.plot_max = calculate_xp_for_level(len(self.plot_acts)) * 500 # Plot duration related to level time, scaled

        self.assign_new_quest() # Get the first quest
        self.quest_progress = 0
        # Set initial task
        self.set_new_task("Beginning the adventure", 5 * 1000) # 5 seconds
        self.game_loaded = True
        print(f"Character Initialized: {self.character['Name']}")
        self.state_updated.emit()


    def tick(self):
        """Main game loop tick, called by the timer."""
        if not self.game_loaded:
            return

        current_time = time.monotonic() * 1000
        elapsed_ms = current_time - self.last_tick_time
        self.last_tick_time = current_time

        if elapsed_ms <= 0: return # Avoid issues if timer fires too fast

        self.task_progress += elapsed_ms

        needs_ui_update = False

        if self.task_progress >= self.task_max:
            # --- Task Completion ---
            completed_task_type = self.task_description.split(" ")[0].lower() # e.g., "executing", "selling"
            is_productive_task = completed_task_type in ["executing", "exploring", "training"] # Tasks that grant XP etc.

            # 1. Resolve Task Effects (Loot, etc.)
            if completed_task_type == "executing" and self.current_target_monster:
                # Grant loot from monster
                loot_item_name = self.current_target_monster.get("loot")
                if loot_item_name and loot_item_name != '*':
                    item_base = f"{self.current_target_monster['name']} {loot_item_name}"
                    self.add_inventory_item(item_base.capitalize())
                elif odds(1, 5): # Chance for generic interesting/boring item
                     self.add_inventory_item(self.generate_random_loot())
                if odds(1, 2): # Chance for gold
                    gold_found = random.randint(1, self.character["Level"] * 2 + 1)
                    self.add_inventory_item("Gold Piece", gold_found)
                self.current_target_monster = None


            # 2. Update Progress Bars if Productive
            if is_productive_task:
                xp_gain = int(self.task_max / 1000) # Simple XP gain based on task time
                self.xp_progress += xp_gain
                self.quest_progress += xp_gain # Quest/Plot progress also tied to task time
                self.plot_progress += xp_gain

            # 3. Check for Level/Quest/Plot Completion
            level_up_occurred = self.check_level_up()
            quest_complete_occurred = self.check_quest_completion() if not level_up_occurred else False # Avoid double reward
            plot_complete_occurred = self.check_plot_completion() if not quest_complete_occurred else False

            # 4. Determine and Set Next Task
            self.determine_next_task()

            needs_ui_update = True


        # --- Update Encumbrance ---
        new_encumbrance = self.calculate_encumbrance()
        if new_encumbrance != self.encumbrance:
            self.encumbrance = new_encumbrance
            needs_ui_update = True

        # --- Emit signal if anything changed ---
        if needs_ui_update:
            self.state_updated.emit()

    def set_new_task(self, description, duration_ms):
        """Sets the current task and resets progress."""
        self.task_description = description
        self.task_max = max(100, duration_ms) # Ensure minimum duration
        self.task_progress = 0
        print(f"New Task: {self.task_description} ({self.task_max/1000:.1f}s)")


    def check_level_up(self):
        """Check if XP threshold is met and perform level up."""
        if self.xp_progress >= self.xp_max:
            self.character["Level"] += 1
            print(f"LEVEL UP! Reached Level {self.character['Level']}")
            # Increase HP/MP
            self.character["HPMax"] += random.randint(1, 4) + math.floor(self.character["Stats"]["CON"] / 3)
            self.character["MPMax"] += random.randint(1, 4) + math.floor(self.character["Stats"]["INT"] / 3)
            # Grant stat points (e.g., 2 points)
            for _ in range(2):
                stat_to_increase = random.choice(list(self.character["Stats"].keys()))
                self.character["Stats"][stat_to_increase] += 1
            # Learn a new spell (simplified)
            if len(self.character["Spells"]) < len(SPELLS):
                eligible_spells = [s for s in SPELLS if s not in self.character["Spells"]]
                if eligible_spells:
                    new_spell = pick(eligible_spells)
                    # Assign a level based on character level progress (crude)
                    spell_level_int = max(1, math.ceil(self.character["Level"] / 5))
                    self.character["Spells"][new_spell] = int_to_roman(spell_level_int)

            # Reset XP bar for next level
            self.xp_progress = 0 # Or self.xp_progress - self.xp_max for rollover
            self.xp_max = calculate_xp_for_level(self.character["Level"] + 1)
            self.encumbrance_max = BASE_ENCUMBRANCE + self.character["Stats"]["STR"] # Update max enc
            # TODO: Trigger "Brag" for multiplayer if implemented
            return True
        return False

    def check_quest_completion(self):
        """Check if quest progress is met and assign new quest."""
        if self.quest_progress >= self.quest_max and self.quests:
            print(f"Quest Complete: {self.quests[-1]}")
            # Grant reward
            reward_type = random.choice(["stat", "equip", "item", "spell"])
            if reward_type == "stat":
                stat_to_increase = random.choice(list(self.character["Stats"].keys()))
                self.character["Stats"][stat_to_increase] += 1
                print("Reward: Stat point!")
            elif reward_type == "equip":
                self.generate_and_equip_item()
                print("Reward: Equipment!")
            elif reward_type == "item":
                 self.add_inventory_item(self.generate_random_loot(force_special=True))
                 print("Reward: Item!")
            elif reward_type == "spell":
                if len(self.character["Spells"]) < len(SPELLS):
                    eligible_spells = [s for s in SPELLS if s not in self.character["Spells"]]
                    if eligible_spells:
                        new_spell = pick(eligible_spells)
                        spell_level_int = max(1, math.ceil(self.character["Level"] / 4))
                        self.character["Spells"][new_spell] = int_to_roman(spell_level_int)
                        print("Reward: Spell!")

            self.assign_new_quest()
            return True
        return False

    def check_plot_completion(self):
        """Check if plot progress is met and advance act."""
        if self.plot_progress >= self.plot_max:
            print(f"Act Complete: {self.plot_acts[-1]}")
            current_act_num = len(self.plot_acts) # Already includes prologue
            next_act_name = f"Act {int_to_roman(current_act_num)}"
            self.plot_acts.append(next_act_name)
            self.plot_progress = 0
            # Plot max duration increases significantly per act
            self.plot_max = calculate_xp_for_level(self.character["Level"] + 1) * (5 + current_act_num * 2) * 10 # arbitrary scaling

            # Give reward for completing act
            if current_act_num > 1: self.generate_and_equip_item(force_upgrade=True)
            if current_act_num > 2: self.add_inventory_item(self.generate_random_loot(force_special=True))

            print(f"Starting {next_act_name}")
            # TODO: Trigger "Brag" for multiplayer if implemented
            return True
        return False


    def assign_new_quest(self):
        """Generate and assign a new quest."""
        quest_type = random.randint(0, 4)
        new_quest_desc = "ERROR: Quest Gen Failed"
        self.quest_target_monster = None # Reset quest monster target

        level = self.character["Level"]
        if quest_type == 0: # Exterminate
            target_monster_data = self.select_monster_near_level(level)
            qty = random.randint(2, 5)
            new_quest_desc = f"Exterminate {definite(target_monster_data['name_mod'], qty)}"
            self.quest_target_monster = target_monster_data # Store for potential task use
        elif quest_type == 1: # Seek Item
             item_name = self.generate_random_loot(force_special=True)
             new_quest_desc = f"Seek {definite(item_name, 1)}"
        elif quest_type == 2: # Deliver Item
             item_name = pick(BORING_ITEMS)
             new_quest_desc = f"Deliver this {item_name}"
        elif quest_type == 3: # Fetch Item
             item_name = pick(BORING_ITEMS)
             new_quest_desc = f"Fetch me {indefinite(item_name, 1)}"
        elif quest_type == 4: # Placate
            target_monster_data = self.select_monster_near_level(level)
            qty = random.randint(2, 4)
            new_quest_desc = f"Placate {definite(target_monster_data['name_mod'], qty)}"
            # No specific target stored for placate, just flavor

        self.quests.append(new_quest_desc)
        if len(self.quests) > 100: # Limit quest history
            self.quests.pop(0)
        self.quest_description = self.quests[-1]
        self.quest_progress = 0
        # Quest duration scales with level
        self.quest_max = (50 + random.randint(0, 50) + self.character["Level"] * 5) * 1000

        print(f"New Quest: {self.quest_description}")

    def determine_next_task(self):
        """Decide what the character should do next."""
        if self.calculate_encumbrance() >= self.encumbrance_max:
            self.set_new_task("Heading to market to sell loot", 4 * 1000)
            self.task_type = "travel_market"
        elif self.character["Gold"] > self.calculate_equip_price() and odds(1, 5): # Chance to buy if affordable
             self.set_new_task("Negotiating purchase of better equipment", 5 * 1000)
             self.task_type = "buying"
        elif self.task_type == "travel_market": # Just arrived at market
             self.try_selling_items() # This might set the next task to 'selling'
        elif self.task_type == "selling": # Finished selling one item
             self.try_selling_items() # Try selling the next
        elif self.task_type == "buying": # Finished buying
             self.perform_buy_equipment()
             self.determine_next_task() # Decide what to do after buying
        else: # Default to combat/exploration
             if odds (1, 3):
                 self.set_new_task("Heading to the killing fields", 4 * 1000)
                 self.task_type = "travel_combat"
             else:
                 self.generate_monster_encounter_task()
                 self.task_type = "executing"


    def try_selling_items(self):
        """Attempt to sell the next sellable item in inventory."""
        sellable_items = [(name, qty) for name, qty in self.character["Inventory"].items() if name != "Gold Piece" and qty > 0]
        if sellable_items:
            item_to_sell, current_qty = sellable_items[0] # Sell oldest first (based on dict order, roughly)
            self.set_new_task(f"Selling {indefinite(item_to_sell, 1)}", 1 * 1000)
            self.task_type = "selling"
            # Actual removal and gold addition happens when the 'selling' task completes
            self.item_being_sold = item_to_sell
        else:
            # No more items to sell, decide next action
            self.task_type = "idle_market" # Mark as finished selling
            self.determine_next_task()


    def perform_buy_equipment(self):
        """Complete the 'buying' task."""
        cost = self.calculate_equip_price()
        if self.character["Gold"] >= cost:
            self.character["Gold"] -= cost
            self.add_inventory_item("Gold Piece", -cost) # Update inventory too
            self.generate_and_equip_item(force_upgrade=True) # Try to get something good


    def generate_monster_encounter_task(self):
        """Generate a monster encounter and set it as the current task."""
        char_level = self.character["Level"]
        target_monster_data = self.select_monster_near_level(char_level)

        # Adjust monster level based on difference from character level (simplified)
        level_diff = char_level - target_monster_data["level"]
        effective_monster_level = target_monster_data["level"]
        monster_name_mod = target_monster_data["name_orig"]

        # Apply mods (very simplified version)
        mod_applied = False
        if level_diff > 5 and odds(1,2): # Character much higher level
             mod = pick( [m for m in MONSTER_MODS if m[0] < -1] ) # Pick a weakening mod
             if mod:
                 effective_monster_level += mod[0]
                 monster_name_mod = mod[1].replace("*", monster_name_mod)
                 mod_applied = True
        elif level_diff < -5 and odds(1,2): # Monster much higher level
             mod = pick( [m for m in MONSTER_MODS if m[0] > 1] ) # Pick a strengthening mod
             if mod:
                 effective_monster_level += mod[0]
                 monster_name_mod = mod[1].replace("*", monster_name_mod)
                 mod_applied = True

        target_monster_data["name_mod"] = monster_name_mod

        # Determine quantity (simplified)
        qty = 1
        if char_level > effective_monster_level + 5 and effective_monster_level > 0:
            qty = min(5, (char_level // effective_monster_level) + random.randint(0,1))
        effective_monster_level *= qty # Total effective level of encounter

        # Task duration based on relative levels (needs tuning)
        duration_factor = max(0.5, effective_monster_level / max(1, char_level))
        base_duration = 5000 # 5 seconds base
        duration_ms = int(base_duration * duration_factor * qty * (random.uniform(0.8, 1.2)))
        duration_ms = max(2000, duration_ms) # Min 2 seconds

        task_desc = f"Executing {indefinite(target_monster_data['name_mod'], qty)}"
        self.set_new_task(task_desc, duration_ms)
        self.current_target_monster = target_monster_data


    def select_monster_near_level(self, level):
        """Select a monster definition reasonably close to the target level."""
        candidates = sorted(MONSTERS, key=lambda m: abs(m[1] - level))
        # Pick from the closest N monsters to add variety
        num_closest = min(len(candidates), 5)
        selected_monster = pick(candidates[:num_closest])
        return {
            "name_orig": selected_monster[0],
            "name_mod": selected_monster[0], # Modified name gets updated later
            "level": selected_monster[1],
            "loot": selected_monster[2]
        }


    def generate_and_equip_item(self, slot_index=None, force_upgrade=False):
        """Generate a new piece of equipment and equip if better (simplified)."""
        if slot_index is None:
            slot_index = random.randrange(len(EQUIPMENT_SLOTS))
        slot_name = EQUIPMENT_SLOTS[slot_index]

        char_level = self.character["Level"]
        base_items = []
        good_mods = []
        bad_mods = []

        if slot_name == "Weapon":
            base_items = WEAPONS
            good_mods = OFFENSE_ATTRIB
            bad_mods = OFFENSE_BAD
        elif slot_name == "Shield":
            base_items = SHIELDS
            good_mods = DEFENSE_ATTRIB
            bad_mods = DEFENSE_BAD
        elif slot_name in ["Helm", "Hauberk", "Brassairs", "Vambraces", "Gauntlets", "Gambeson", "Cuisses", "Greaves", "Sollerets"]:
             base_items = ARMORS # Use armor list for all armor slots
             good_mods = DEFENSE_ATTRIB
             bad_mods = DEFENSE_BAD
        else: return # Unknown slot

        if not base_items: return

        # Select base item near character level
        base_item_tuple = pick(sorted(base_items, key=lambda item: abs(item[1] - char_level))[:10]) # Pick from 10 closest
        item_name = base_item_tuple[0]
        base_value = base_item_tuple[1]

        level_diff = char_level - base_value
        if force_upgrade: level_diff = max(1, level_diff + random.randint(1,3)) # Bias towards positive if upgrading

        current_mods_value = 0
        num_mods = 0
        max_mods = 2

        mods_to_use = good_mods if level_diff > 0 else bad_mods
        applied_mod_names = []

        while num_mods < max_mods and abs(level_diff) > 0 and mods_to_use:
            possible_mods = [m for m in mods_to_use if abs(m[1]) <= abs(level_diff) and m[0] not in applied_mod_names]
            if not possible_mods: break

            mod_tuple = pick(possible_mods)
            mod_name = mod_tuple[0]
            mod_value = mod_tuple[1]

            item_name = f"{mod_name} {item_name}"
            applied_mod_names.append(mod_name)
            current_mods_value += mod_value
            level_diff -= mod_value
            num_mods += 1

        # Add numeric prefix if difference remains
        if level_diff != 0:
             prefix = f"+{level_diff}" if level_diff > 0 else str(level_diff)
             item_name = f"{prefix} {item_name}"

        # Simple: Always equip the newly generated item (no comparison logic yet)
        self.character["Equipment"][slot_name] = item_name
        print(f"Equipped: {item_name} in slot {slot_name}")

    def generate_random_loot(self, force_special=False):
        """Generate a random boring or special item."""
        if force_special or odds(1, 5): # 1 in 5 chance for special item
             attrib = pick(ITEM_ATTRIB)
             special = pick(SPECIALS)
             of_part = pick(ITEM_OFS)
             return f"{attrib} {special} of {of_part}"
        else:
             return pick(BORING_ITEMS)


    def add_inventory_item(self, item_name, quantity=1):
        """Add an item to the inventory."""
        if item_name == "Gold Piece":
            self.character["Gold"] = max(0, self.character["Gold"] + quantity)
        current_qty = self.character["Inventory"].get(item_name, 0)
        new_qty = max(0, current_qty + quantity)
        if new_qty > 0:
            self.character["Inventory"][item_name] = new_qty
        elif item_name in self.character["Inventory"]: # Remove if quantity drops to 0 or less
             del self.character["Inventory"][item_name]
        print(f"Inventory: {'Added' if quantity > 0 else 'Removed'} {abs(quantity)}x {item_name}")
        self.state_updated.emit() # Update UI after inventory change


    def calculate_encumbrance(self):
        """Calculate current encumbrance based on inventory (excluding gold)."""
        total_items = 0
        for name, qty in self.character["Inventory"].items():
            if name != "Gold Piece":
                total_items += qty
        return total_items

    def calculate_equip_price(self):
        """Calculate the cost of buying new equipment."""
        level = self.character["Level"]
        return 5 * level * level + 10 * level + 20


    # --- Getters for UI ---
    def get_state(self):
        """Return a dictionary representing the current game state for UI updates."""
        return {
            "character": self.character,
            "plot_acts": self.plot_acts,
            "quests": self.quests,
            "task_description": self.task_description,
            "task_progress": self.task_progress,
            "task_max": self.task_max,
            "xp_progress": self.xp_progress,
            "xp_max": self.xp_max,
            "quest_description": self.quest_description,
            "quest_progress": self.quest_progress,
            "quest_max": self.quest_max,
            "plot_progress": self.plot_progress,
            "plot_max": self.plot_max,
            "encumbrance": self.encumbrance,
            "encumbrance_max": self.encumbrance_max,
            "current_act": self.plot_acts[-1] if self.plot_acts else "None"
        }

```

```python
# File: character_dialog.py
import sys
import random
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QGroupBox, QGridLayout, QSizePolicy
)
from PySide6.QtCore import Qt, Slot
from config_data import RACES, KLASSES, generate_name

class NewCharacterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Progress Quest - New Character")
        self.setMinimumWidth(500)

        self.layout = QVBoxLayout(self)

        # Name and Generation
        name_layout = QHBoxLayout()
        self.name_label = QLabel("Name:")
        self.name_edit = QLineEdit()
        self.name_edit.setMaxLength(30)
        self.gen_name_button = QPushButton("?")
        self.gen_name_button.setFixedSize(25, 25)
        self.gen_name_button.clicked.connect(self.generate_random_name)
        name_layout.addWidget(self.name_label)
        name_layout.addWidget(self.name_edit)
        name_layout.addWidget(self.gen_name_button)
        self.layout.addLayout(name_layout)

        # Race and Class Selection
        selection_layout = QHBoxLayout()
        self.race_group = QGroupBox("Race")
        self.race_layout = QVBoxLayout()
        self.race_combo = QComboBox()
        self.race_combo.addItems(RACES.keys())
        self.race_layout.addWidget(self.race_combo)
        self.race_group.setLayout(self.race_layout)
        selection_layout.addWidget(self.race_group)

        self.class_group = QGroupBox("Class")
        self.class_layout = QVBoxLayout()
        self.class_combo = QComboBox()
        self.class_combo.addItems(KLASSES.keys())
        self.class_layout.addWidget(self.class_combo)
        self.class_group.setLayout(self.class_layout)
        selection_layout.addWidget(self.class_group)
        self.layout.addLayout(selection_layout)

        # Stats Rolling
        self.stats_group = QGroupBox("Stats")
        self.stats_layout = QGridLayout()
        self.stat_labels = {}
        self.stat_values = {}
        self.stat_order = ["STR", "CON", "DEX", "INT", "WIS", "CHA"]
        for i, stat_name in enumerate(self.stat_order):
            self.stat_labels[stat_name] = QLabel(f"{stat_name}:")
            self.stat_values[stat_name] = QLabel("10") # Initial value
            self.stat_values[stat_name].setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.stat_values[stat_name].setMinimumWidth(30)
            self.stats_layout.addWidget(self.stat_labels[stat_name], i, 0)
            self.stats_layout.addWidget(self.stat_values[stat_name], i, 1)

        self.total_label = QLabel("Total:")
        self.total_value = QLabel("60")
        self.total_value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.stats_layout.addWidget(self.total_label, len(self.stat_order), 0)
        self.stats_layout.addWidget(self.total_value, len(self.stat_order), 1)

        self.roll_button = QPushButton("Roll")
        self.roll_button.clicked.connect(self.roll_stats)
        # self.unroll_button = QPushButton("Unroll") # Unroll is more complex, requires state saving
        # self.unroll_button.setEnabled(False)
        self.stats_layout.addWidget(self.roll_button, len(self.stat_order) + 1, 0, 1, 2)
        # self.stats_layout.addWidget(self.unroll_button, len(self.stat_order) + 2, 0, 1, 2)
        self.stats_group.setLayout(self.stats_layout)
        self.layout.addWidget(self.stats_group)

        # Dialog Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Sold!")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(button_layout)

        # Initial state
        self.generate_random_name()
        self.roll_stats()

    @Slot()
    def generate_random_name(self):
        self.name_edit.setText(generate_name())

    def roll_d6(self):
        return random.randint(1, 6)

    @Slot()
    def roll_stats(self):
        total = 0
        self.current_stats = {}
        for stat_name in self.stat_order:
            roll_value = self.roll_d6() + self.roll_d6() + self.roll_d6()
            self.stat_values[stat_name].setText(str(roll_value))
            self.current_stats[stat_name] = roll_value
            total += roll_value
        self.total_value.setText(str(total))
        # Add visual feedback for total score (optional)
        if total >= (63 + 18): self.total_value.setStyleSheet("color: red;")
        elif total > (4 * 18): self.total_value.setStyleSheet("color: yellow;")
        elif total <= (63 - 18): self.total_value.setStyleSheet("color: grey;")
        elif total < (3 * 18): self.total_value.setStyleSheet("color: silver;")
        else: self.total_value.setStyleSheet("") # Reset style


    def get_character_data(self):
        if self.result() == QDialog.DialogCode.Accepted:
            return {
                "name": self.name_edit.text(),
                "race": self.race_combo.currentText(),
                "class": self.class_combo.currentText(),
                "stats": self.current_stats
            }
        return None

# Example usage (for testing the dialog)
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLESHEET) # Apply dark theme
    dialog = NewCharacterDialog()
    if dialog.exec():
        data = dialog.get_character_data()
        print("Character Created:", data)
    else:
        print("Character creation cancelled.")
    sys.exit()
```

```python
# File: main_window.py
# (Continuing from the previous response)

import sys
import os # For potential file path operations (saving/loading)
import zlib # For saving/loading
import pickle # For saving/loading complex Python objects

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QListView, QProgressBar, QStatusBar, QSizePolicy, QSplitter,
    QFileDialog # For loading games
)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon
from PySide6.QtCore import Qt, QTimer, Slot, QPoint

from config_data import (
    DARK_STYLESHEET, EQUIPMENT_SLOTS, rough_time, int_to_roman,
    plural, definite, indefinite, SAVE_FILE_EXT, BACKUP_FILE_EXT,
    TIMER_INTERVAL_MS
)
from game_logic import GameLogic
from character_dialog import NewCharacterDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Progress Quest (Zero Source Edition)")
        self.setGeometry(100, 100, 850, 650) # x, y, width, height

        self.game_logic = GameLogic()
        self.game_logic.state_updated.connect(self.update_ui)

        self.save_file_path = None # Store path for saving

        self.setup_ui()

        # --- Game Timer ---
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.game_logic.tick)
        # Timer starts after character creation or loading

        # --- Start Character Creation ---
        # In a real app, you'd have a start screen first
        # For now, directly call character creation.
        # TODO: Implement a start screen later offering New/Load/Multiplayer etc.
        self.create_new_character()


    def setup_ui(self):
        """Create the main UI elements."""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # --- Top Panels (Splitter for resizing) ---
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Panel 1: Character Sheet
        panel1 = QWidget()
        layout1 = QVBoxLayout(panel1)
        layout1.addWidget(self._create_label("Character Sheet", header=True))
        self.traits_list = self._create_list_view(["Trait", "Value"])
        layout1.addWidget(self.traits_list)
        self.stats_list = self._create_list_view(["Stat", "Value"])
        layout1.addWidget(self.stats_list)
        layout1.addWidget(self._create_label("Experience"))
        self.exp_bar = self._create_progress_bar()
        layout1.addWidget(self.exp_bar)
        layout1.addWidget(self._create_label("Spell Book", header=True))
        self.spells_list = self._create_list_view(["Spell", "Level"])
        layout1.addWidget(self.spells_list)
        self.splitter.addWidget(panel1)

        # Panel 2: Equipment & Inventory
        panel2 = QWidget()
        layout2 = QVBoxLayout(panel2)
        layout2.addWidget(self._create_label("Equipment", header=True))
        self.equips_list = self._create_list_view(["Position", "Equipped"])
        layout2.addWidget(self.equips_list)
        layout2.addWidget(self._create_label("Inventory", header=True))
        self.inventory_list = self._create_list_view(["Item", "Qty"])
        layout2.addWidget(self.inventory_list)
        layout2.addWidget(self._create_label("Encumbrance"))
        self.encum_bar = self._create_progress_bar()
        layout2.addWidget(self.encum_bar)
        self.splitter.addWidget(panel2)

        # Panel 3: Plot & Quests
        panel3 = QWidget()
        layout3 = QVBoxLayout(panel3)
        layout3.addWidget(self._create_label("Plot Development", header=True))
        self.plots_list = self._create_list_view(["Act"])
        self.plots_list.setHeaderHidden(True) # No need for header if only one column
        layout3.addWidget(self.plots_list)
        self.plot_bar = self._create_progress_bar()
        layout3.addWidget(self.plot_bar)
        layout3.addWidget(self._create_label("Quests", header=True))
        self.quests_list = self._create_list_view(["Quest"])
        self.quests_list.setHeaderHidden(True) # No need for header if only one column
        layout3.addWidget(self.quests_list)
        self.quest_bar = self._create_progress_bar()
        layout3.addWidget(self.quest_bar)
        self.splitter.addWidget(panel3)

        main_layout.addWidget(self.splitter)
        self.splitter.setSizes([220, 300, 220]) # Initial relative sizes

        # --- Bottom Bars ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.task_bar = self._create_progress_bar()
        main_layout.addWidget(self.task_bar)

        # --- Models for ListViews ---
        self.traits_model = QStandardItemModel()
        self.stats_model = QStandardItemModel()
        self.equips_model = QStandardItemModel()
        self.inventory_model = QStandardItemModel()
        self.spells_model = QStandardItemModel()
        self.plots_model = QStandardItemModel()
        self.quests_model = QStandardItemModel() # Completing the line

        # Assign models to views
        self.traits_list.setModel(self.traits_model)
        self.stats_list.setModel(self.stats_model)
        self.equips_list.setModel(self.equips_model)
        self.inventory_list.setModel(self.inventory_model)
        self.spells_list.setModel(self.spells_model)
        self.plots_list.setModel(self.plots_model)
        self.quests_list.setModel(self.quests_model)


    # --- UI Helper Methods ---
    def _create_label(self, text, header=False):
        label = QLabel(text)
        if header:
            label.setObjectName("HeaderLabel") # For potential specific styling
            label.setStyleSheet("font-weight: bold;") # Simple bolding
        return label

    def _create_list_view(self, headers):
        view = QListView()
        view.setEditTriggers(QListView.EditTrigger.NoEditTriggers) # Read-only
        view.setSelectionMode(QListView.SelectionMode.NoSelection) # No selection highlight
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # Note: QListView itself doesn't show headers. For headers, you'd use QTreeView
        # We'll use QStandardItemModel which QListView can display. Headers are just conceptual here.
        # If actual columns are needed, switch to QTableView or QTreeView.
        # For simplicity now, stick to QListView and format items appropriately.
        return view

    def _create_progress_bar(self):
        bar = QProgressBar()
        bar.setRange(0, 1000) # Use a high range for smoother updates (e.g., milliseconds)
        bar.setValue(0)
        bar.setTextVisible(True)
        bar.setFormat("%p%") # Show percentage by default
        return bar

    # --- Game Interaction ---
    def create_new_character(self):
        """Opens the dialog to create a new character."""
        self.timer.stop() # Stop game loop while creating
        dialog = NewCharacterDialog(self)
        if dialog.exec():
            char_data = dialog.get_character_data()
            if char_data:
                self.game_logic.initialize_new_character(
                    char_data["name"], char_data["race"], char_data["class"], char_data["stats"]
                )
                # Determine initial save file path
                char_name_safe = "".join(c for c in char_data["name"] if c.isalnum() or c in (' ', '_')).rstrip()
                self.save_file_path = f"{char_name_safe}{SAVE_FILE_EXT}"
                self.setWindowTitle(f"Progress Quest - {char_data['name']}")
                print(f"Starting game. Save file will be: {self.save_file_path}")
                self.timer.start(TIMER_INTERVAL_MS)
        else:
            print("Character creation cancelled. Closing application.")
            self.close() # Close main window if creation is cancelled

    # --- UI Update Slot ---
    @Slot()
    def update_ui(self):
        """Update all UI elements based on the current game state."""
        state = self.game_logic.get_state()
        char = state["character"]

        # --- Panel 1: Character Sheet ---
        self.traits_model.clear()
        self.traits_model.setHorizontalHeaderLabels(["Trait", "Value"]) # Set conceptually
        self._add_item_to_model(self.traits_model, ["Name", char["Name"]])
        self._add_item_to_model(self.traits_model, ["Race", char["Race"]])
        self._add_item_to_model(self.traits_model, ["Class", char["Class"]])
        self._add_item_to_model(self.traits_model, ["Level", str(char["Level"])])

        self.stats_model.clear()
        self.stats_model.setHorizontalHeaderLabels(["Stat", "Value"])
        for stat, value in char["Stats"].items():
            self._add_item_to_model(self.stats_model, [stat, str(value)])
        self._add_item_to_model(self.stats_model, ["HP Max", str(char["HPMax"])])
        self._add_item_to_model(self.stats_model, ["MP Max", str(char["MPMax"])])

        self.spells_model.clear()
        self.spells_model.setHorizontalHeaderLabels(["Spell", "Level"])
        # Sort spells alphabetically for consistency
        sorted_spells = sorted(char["Spells"].items())
        for spell, level_roman in sorted_spells:
            self._add_item_to_model(self.spells_model, [spell, level_roman])

        self._update_progress_bar(self.exp_bar, state["xp_progress"], state["xp_max"],
                                  f"{int(state['xp_progress'])}/{int(state['xp_max'])} XP")

        # --- Panel 2: Equipment & Inventory ---
        self.equips_model.clear()
        self.equips_model.setHorizontalHeaderLabels(["Position", "Equipped"])
        for slot in EQUIPMENT_SLOTS:
            item = char["Equipment"].get(slot, "")
            self._add_item_to_model(self.equips_model, [slot, item])

        self.inventory_model.clear()
        self.inventory_model.setHorizontalHeaderLabels(["Item", "Qty"])
        # Sort inventory: Gold first, then alphabetically
        inv_items = sorted(char["Inventory"].items(), key=lambda item: (item[0] != "Gold Piece", item[0]))
        for item, qty in inv_items:
            display_name = f"{qty}x {plural(item)}" if item == "Gold Piece" else item
            self._add_item_to_model(self.inventory_model, [display_name, str(qty)])


        self._update_progress_bar(self.encum_bar, state["encumbrance"], state["encumbrance_max"],
                                  f"{state['encumbrance']}/{state['encumbrance_max']} cubits")

        # --- Panel 3: Plot & Quests ---
        self.plots_model.clear()
        self.plots_model.setHorizontalHeaderLabels(["Act"])
        for i, act in enumerate(state["plot_acts"]):
             # Checkmark for completed acts (all except the last one)
             icon = QIcon(":/qt-project.org/styles/commonstyle/images/standardbutton-apply-16.png") if i < len(state["plot_acts"]) - 1 else QIcon() # Needs proper icon path
             item = QStandardItem(act)
             # item.setIcon(icon) # Requires valid icon setup
             if i < len(state["plot_acts"]) - 1:
                 item.setData(Qt.CheckState.Checked, Qt.ItemDataRole.CheckStateRole) # Alternate visualization
                 item.setText(f"✓ {act}") # Simple text checkmark
             self.plots_model.appendRow(item)
        # Scroll to bottom (newest act)
        self.plots_list.scrollToBottom()

        time_left_plot = rough_time(max(0, state["plot_max"] - state["plot_progress"]) / 1000)
        self._update_progress_bar(self.plot_bar, state["plot_progress"], state["plot_max"],
                                  f"{state['current_act']} ({time_left_plot} left)")

        self.quests_model.clear()
        self.quests_model.setHorizontalHeaderLabels(["Quest"])
        for i, quest in enumerate(state["quests"]):
            # Checkmark for completed quests (all except the last one)
            icon = QIcon(":/qt-project.org/styles/commonstyle/images/standardbutton-apply-16.png") if i < len(state["quests"]) - 1 else QIcon()
            item = QStandardItem(quest)
            # item.setIcon(icon)
            if i < len(state["quests"]) - 1:
                 item.setText(f"✓ {quest}")
            self.quests_model.appendRow(item)
        # Scroll to bottom (current quest)
        self.quests_list.scrollToBottom()

        percent_quest = (state["quest_progress"] * 100 / state["quest_max"]) if state["quest_max"] > 0 else 0
        self._update_progress_bar(self.quest_bar, state["quest_progress"], state["quest_max"],
                                  f"{percent_quest:.0f}% - {state['quest_description']}")

        # --- Bottom Bars ---
        self.status_bar.showMessage(state["task_description"] + "...")
        percent_task = (state["task_progress"] * 100 / state["task_max"]) if state["task_max"] > 0 else 0
        self._update_progress_bar(self.task_bar, state["task_progress"], state["task_max"], f"{percent_task:.0f}%")


    def _add_item_to_model(self, model, texts):
        """Adds a row with multiple columns to a QStandardItemModel."""
        # Since QListView shows only the first column, we format the string here
        # If using QTreeView/QTableView, you'd append QStandardItem(text) for each column
        display_text = f"{texts[0]}: {texts[1]}" if len(texts) > 1 else texts[0]
        item = QStandardItem(display_text)
        model.appendRow(item)


    def _update_progress_bar(self, bar, value, maximum, text_format=None):
        """Safely update a progress bar."""
        bar.setMaximum(max(1, int(maximum))) # Ensure max is at least 1
        bar.setValue(min(int(value), bar.maximum())) # Clamp value
        if text_format:
            bar.setFormat(text_format)
        else:
            # Default format if none provided
            percent = (value * 100 / maximum) if maximum > 0 else 0
            bar.setFormat(f"{percent:.0f}%")

    # --- Saving and Loading (Basic Implementation) ---
    def save_game(self):
        if not self.save_file_path or not self.game_logic.game_loaded:
            print("Cannot save: Game not started or no save path defined.")
            return False

        # Create backup
        if os.path.exists(self.save_file_path):
            backup_path = self.save_file_path.replace(SAVE_FILE_EXT, BACKUP_FILE_EXT)
            try:
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                os.rename(self.save_file_path, backup_path)
                print(f"Created backup: {backup_path}")
            except OSError as e:
                print(f"Warning: Could not create backup file: {e}")

        # Save current state
        try:
            game_state_data = self.game_logic.get_state_for_saving() # Need this method in GameLogic
            # Serialize and compress
            pickled_data = pickle.dumps(game_state_data)
            compressed_data = zlib.compress(pickled_data, level=9) # Max compression

            with open(self.save_file_path, 'wb') as f:
                f.write(compressed_data)
            print(f"Game saved successfully to {self.save_file_path}")
            # TODO: Show message in status bar? Original showed a dialog.
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            # Attempt to restore backup if save failed
            if os.path.exists(backup_path):
                try:
                    os.rename(backup_path, self.save_file_path)
                    print("Restored backup file after save error.")
                except OSError as be:
                     print(f"Critical Error: Could not restore backup file: {be}")
            return False


    def load_game(self):
        """Placeholder for loading game state."""
        # TODO: Implement loading logic
        # 1. Show File Dialog to select .pq file
        # 2. Read file, decompress ZLib, unpickle data
        # 3. Restore game_logic state from loaded data
        # 4. Update UI
        # 5. Start timer
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Progress Quest Game", "", f"Progress Quest Files (*{SAVE_FILE_EXT})")
        if file_path:
             print(f"Loading game from: {file_path}")
             try:
                 with open(file_path, 'rb') as f:
                     compressed_data = f.read()
                 decompressed_data = zlib.decompress(compressed_data)
                 loaded_state = pickle.loads(decompressed_data)

                 # Need a method in GameLogic to apply the loaded state
                 self.game_logic.apply_loaded_state(loaded_state)

                 self.save_file_path = file_path # Update save path
                 self.setWindowTitle(f"Progress Quest - {self.game_logic.character['Name']}")
                 self.update_ui() # Force immediate UI update
                 self.timer.start(TIMER_INTERVAL_MS)
                 print("Game loaded successfully.")
             except FileNotFoundError:
                 print(f"Error: Save file not found at {file_path}")
             except (zlib.error, pickle.UnpicklingError, EOFError) as e:
                 print(f"Error loading game data: Invalid or corrupt file. {e}")
             except Exception as e:
                 print(f"An unexpected error occurred during loading: {e}")
        else:
             print("Load cancelled.")


    # --- Event Overrides ---
    def closeEvent(self, event):
        """Handle window close event."""
        print("Closing application...")
        self.timer.stop()
        # Attempt to save game before closing
        if self.game_logic.game_loaded:
             self.save_game()
             # Consider asking user if save fails?
        event.accept() # Accept the close event


# --- Main Execution ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLESHEET) # Apply dark theme

    # Check if game file path provided as argument
    game_file_to_load = None
    if len(sys.argv) > 1:
        potential_path = sys.argv[1]
        if potential_path.endswith(SAVE_FILE_EXT) and os.path.exists(potential_path):
             game_file_to_load = potential_path
        # Add handling for other command-line args like -help, -export etc. here

    window = MainWindow()

    if game_file_to_load:
        print(f"Command line argument detected: Attempting to load {game_file_to_load}")
        # Stop the automatic character creation if loading from command line
        # This requires restructuring __init__ slightly or adding a flag
        window.timer.stop() # Ensure timer isn't running from a cancelled char creation
        window.load_game_from_path(game_file_to_load) # Need this specific method
    #else:
    #    # If not loading from command line, the character creation
    #    # called from __init__ takes precedence.
    #    pass # Normal startup flow handled in __init__

    window.show()
    sys.exit(app.exec())
```

**To make this runnable, you would also need to:**

1.  **Complete `config_data.py`:** Populate *all* the lists (Weapons, Armors, Spells, Monsters, etc.) from the DFM files provided earlier. This is the most tedious part.
2.  **Implement Saving/Loading in `GameLogic`:**
    *   Add `get_state_for_saving()` to `GameLogic` which bundles all necessary state variables into a serializable dictionary.
    *   Add `apply_loaded_state(loaded_state)` to `GameLogic` which takes the dictionary loaded from a file and restores the game's internal state.
3.  **Refine `MainWindow.__init__` and Loading:** Modify `MainWindow.__init__` to handle the case where a game is loaded via command-line argument *instead* of immediately calling `create_new_character`. You might add a `load_game_from_path` method.
4.  **Refine Game Logic:** Implement the missing details in `game_logic.py` – accurate XP/Quest/Plot progression calculations, item comparison for equipping, selling logic, buying logic, proper monster mod application, etc.
5.  **Install PySide6:** `pip install PySide6`
6.  **Run:** `python main_window.py` (or `python main_window.py your_save_file.pq` to test loading).

This provides a solid foundation based on the TINS description and Delphi structure, but completing it into a fully functional replica of Progress Quest requires significant further development.