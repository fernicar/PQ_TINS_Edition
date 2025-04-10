Okay, here is the Python source code for the offline, single-player Progress Quest desktop application using PySide6, based on the provided Delphi structure and focusing on the core gameplay loop described in the TINS README.

This code excludes multiplayer features (server communication, login, realm selection). It uses `pickle` and `zlib` for saving/loading, mimicking the original's approach but in Python.

```python
# START OF FILE: config_data.py
# File: config_data.py
# Holds the game configuration data, similar to Config.pas/Config.dfm
import random
import math
import re
import time # Keep time import here if needed by helpers

# --- Game Content Data ---

RACES = {
    "Half Orc": {"bonuses": ["HP Max"]},
    "Half Man": {"bonuses": ["CHA"]},
    "Half Halfling": {"bonuses": ["DEX"]},
    "Double Hobbit": {"bonuses": ["STR"]},
    "Hob-Hobbit": {"bonuses": ["DEX", "CON"]}, # Corrected name based on DFM
    "Low Elf": {"bonuses": ["CON"]},
    "Dung Elf": {"bonuses": ["WIS"]},
    "Talking Pony": {"bonuses": ["MP Max", "INT"]},
    "Gyrognome": {"bonuses": ["DEX"]},
    "Lesser Dwarf": {"bonuses": ["CON"]},
    "Crested Dwarf": {"bonuses": ["CHA"]},
    "Eel Man": {"bonuses": ["DEX"]},
    "Panda Man": {"bonuses": ["CON", "STR"]},
    "Trans-Kobold": {"bonuses": ["WIS"]},
    "Enchanted Motorcycle": {"bonuses": ["MP Max"]},
    "Will o' the Wisp": {"bonuses": ["WIS"]},
    "Battle-Finch": {"bonuses": ["DEX", "INT"]},
    "Double Wookiee": {"bonuses": ["STR"]},
    "Skraeling": {"bonuses": ["WIS"]},
    "Demicanadian": {"bonuses": ["CON"]},
    "Land Squid": {"bonuses": ["STR", "HP Max"]},
}

KLASSES = {
    "Ur-Paladin": {"bonuses": ["WIS", "CON"]},
    "Voodoo Princess": {"bonuses": ["INT", "CHA"]},
    "Robot Monk": {"bonuses": ["STR"]},
    "Mu-Fu Monk": {"bonuses": ["DEX"]},
    "Mage Illusioner": {"bonuses": ["INT", "MP Max"]},
    "Shiv-Knight": {"bonuses": ["DEX"]},
    "Inner Mason": {"bonuses": ["CON"]},
    "Fighter/Organist": {"bonuses": ["CHA", "STR"]},
    "Puma Burgular": {"bonuses": ["DEX"]}, # Sic
    "Runeloremaster": {"bonuses": ["WIS"]},
    "Hunter Strangler": {"bonuses": ["DEX", "INT"]},
    "Battle-Felon": {"bonuses": ["STR"]},
    "Tickle-Mimic": {"bonuses": ["WIS", "INT"]},
    "Slow Poisoner": {"bonuses": ["CON"]},
    "Bastard Lunatic": {"bonuses": ["CON"]},
    "Jungle Clown": {"bonuses": ["DEX", "CHA"]},
    "Birdrider": {"bonuses": ["WIS"]},
    "Vermineer": {"bonuses": ["INT"]},
}

WEAPONS = [
    ("Stick", 0), ("Broken Bottle", 1), ("Shiv", 1), ("Sprig", 1), ("Oxgoad", 1),
    ("Eelspear", 2), ("Bowie Knife", 2), ("Claw Hammer", 2), ("Handpeen", 2),
    ("Andiron", 3), ("Hatchet", 3), ("Tomahawk", 3), ("Hackbarm", 3),
    ("Crowbar", 4), ("Mace", 4), ("Battleadze", 4), ("Leafmace", 5),
    ("Shortsword", 5), ("Longiron", 5), ("Poachard", 5), ("Baselard", 5),
    ("Whinyard", 6), ("Blunderbuss", 6), ("Longsword", 6), ("Crankbow", 6),
    ("Blibo", 7), ("Broadsword", 7), ("Kreen", 7), ("Morning Star", 8),
    ("Pole-adze", 8), ("Spontoon", 8), ("Bastard Sword", 9), ("Peen-arm", 9),
    ("Culverin", 10), ("Lance", 10), ("Halberd", 11), ("Poleax", 12),
    ("Bandyclef", 15),
]

ARMORS = [
    ("Lace", 1), ("Macrame", 2), ("Burlap", 3), ("Canvas", 4), ("Flannel", 5),
    ("Chamois", 6), ("Pleathers", 7), ("Leathers", 8), ("Bearskin", 9),
    ("Ringmail", 10), ("Scale Mail", 12), ("Chainmail", 14), ("Splint Mail", 15),
    ("Platemail", 16), ("ABS", 17), ("Kevlar", 18), ("Titanium", 19),
    ("Mithril Mail", 20), ("Diamond Mail", 25), ("Plasma", 30),
]

SHIELDS = [
    ("Parasol", 0), ("Pie Plate", 1), ("Garbage Can Lid", 2), ("Buckler", 3),
    ("Plexiglass", 4), ("Fender", 4), ("Round Shield", 5), ("Carapace", 5),
    ("Scutum", 6), ("Propugner", 6), ("Kite Shield", 7), ("Pavise", 8),
    ("Tower Shield", 9), ("Baroque Shield", 11), ("Aegis", 12),
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
    'Invisible Hands', 'Revolting Cloud', 'Aqueous Humor', 'Spectral Miasma',
    'Clever Fellow', 'Lockjaw', 'History Lesson', 'Hydrophobia', 'Big Sister',
    'Cone of Paste', 'Mulligan', "Nestor's Bright Idea", 'Holy Batpole',
    'Tumor (Benign)', 'Braingate', 'Nonplus', 'Animate Nightstand',
    'Eye of the Troglodyte', 'Curse Name', 'Dropsy', 'Vitreous Humor',
    "Roger's Grand Illusion", 'Covet', 'Astral Miasma', 'Spectral Oyster',
    'Acrid Hands', 'Angioplasty', "Grognor's Big Day Off", 'Tumor (Malignant)',
    'Animate Tunic', 'Ursine Armor', 'Holy Roller', 'Tonsillectomy',
    'Curse Family', 'Infinite Confusion',
]

BORING_ITEMS = [
    'nail', 'lunchpail', 'sock', 'I.O.U.', 'cookie', 'pint', 'toothpick',
    'writ', 'newspaper', 'letter', 'plank', 'hat', 'egg', 'coin', 'needle',
    'bucket', 'ladder', 'chicken', 'twig', 'dirtclod', 'counterpane',
    'vest', 'teratoma', 'bunny', 'rock', 'pole', 'carrot', 'canoe',
    'inkwell', 'hoe', 'bandage', 'trowel', 'towel', 'planter box',
    'anvil', 'axle', 'tuppence', 'casket', 'nosegay', 'trinket',
    'credenza', 'writ', # Writ appears twice in original
]

SPECIALS = [ # Base name for special items
    'Diadem', 'Festoon', 'Gemstone', 'Phial', 'Tiara', 'Scabbard', 'Arrow',
    'Lens', 'Lamp', 'Hymnal', 'Fleece', 'Laurel', 'Brooch', 'Gimlet',
    'Cobble', 'Albatross', 'Brazier', 'Bandolier', 'Tome', 'Garnet',
    'Amethyst', 'Candelabra', 'Corset', 'Sphere', 'Sceptre', 'Ankh',
    'Talisman', 'Orb', 'Gammel', 'Ornament', 'Brocade', 'Galoon', 'Bijou',
    'Spangle', 'Gimcrack', 'Hood', 'Vulpeculum',
]

ITEM_ATTRIB = [ # Prefixes for special items
    'Golden', 'Gilded', 'Spectral', 'Astral', 'Garlanded', 'Precious',
    'Crafted', 'Dual', 'Filigreed', 'Cruciate', 'Arcane', 'Blessed',
    'Reverential', 'Lucky', 'Enchanted', 'Gleaming', 'Grandiose', 'Sacred',
    'Legendary', 'Mythic', 'Crystalline', 'Austere', 'Ostentatious',
    'One True', 'Proverbial', 'Fearsome', 'Deadly', 'Benevolent',
    'Unearthly', 'Magnificent', 'Iron', 'Ormolu', 'Puissant',
]

ITEM_OFS = [ # Suffixes for special items ("of X")
    'Foreboding', 'Foreshadowing', 'Nervousness', 'Happiness', 'Torpor',
    'Danger', 'Craft', 'Silence', 'Invisibility', 'Rapidity', 'Pleasure',
    'Practicality', 'Hurting', 'Joy', 'Petulance', 'Intrusion', 'Chaos',
    'Suffering', 'Extroversion', 'Frenzy', 'Solitude', 'Punctuality',
    'Efficiency', 'Comfort', 'Patience', 'Internment', 'Incarceration',
    'Misapprehension', 'Loyalty', 'Envy', 'Acrimony', 'Worry', 'Fear',
    'Awe', 'Guile', 'Prurience', 'Fortune', 'Perspicacity', 'Domination',
    'Submission', 'Fealty', 'Hunger', 'Despair', 'Cruelty', 'Grob',
    'Dignard', 'Ra', 'the Bone', 'Diamonique', 'Electrum', 'Hydragyrum',
]

MONSTERS = [
    # (Name, Level, LootItem | * for generic)
    ("Anhkheg", 6, "chitin"), ("Ant", 0, "antenna"), ("Ape", 4, "ass"),
    ("Baluchitherium", 14, "ear"), ("Beholder", 10, "eyestalk"),
    ("Black Pudding", 10, "saliva"), ("Blink Dog", 4, "eyelid"),
    ("Cub Scout", 1, "neckerchief"), ("Girl Scout", 2, "cookie"),
    ("Boy Scout", 3, "merit badge"), ("Eagle Scout", 4, "merit badge"),
    ("Bugbear", 3, "skin"), ("Bugboar", 3, "tusk"), ("Boogie", 3, "slime"),
    ("Camel", 2, "hump"), ("Carrion Crawler", 3, "egg"), ("Catoblepas", 6, "neck"),
    ("Centaur", 4, "rib"), ("Centipede", 0, "leg"), ("Cockatrice", 5, "wattle"),
    ("Couatl", 9, "wing"), ("Crayfish", 0, "antenna"), ("Demogorgon", 53, "tentacle"),
    ("Jubilex", 17, "gel"), ("Manes", 1, "tooth"), ("Orcus", 27, "wand"),
    ("Succubus", 6, "bra"), ("Vrock", 8, "neck"), ("Hezrou", 9, "leg"),
    ("Glabrezu", 10, "collar"), ("Nalfeshnee", 11, "tusk"), ("Marilith", 7, "arm"),
    ("Balor", 8, "whip"), ("Yeenoghu", 25, "flail"), ("Asmodeus", 52, "leathers"),
    ("Baalzebul", 43, "pants"), ("Barbed Devil", 8, "flame"), ("Bone Devil", 9, "hook"),
    ("Dispater", 30, "matches"), ("Erinyes", 6, "thong"), ("Geryon", 30, "cornucopia"),
    ("Malebranche", 5, "fork"), ("Ice Devil", 11, "snow"), ("Lemure", 3, "blob"),
    ("Pit Fiend", 13, "seed"), ("Ankylosaurus", 9, "tail"), ("Brontosaurus", 30, "brain"),
    ("Diplodocus", 24, "fin"), ("Elasmosaurus", 15, "neck"), ("Gorgosaurus", 13, "arm"),
    ("Iguanadon", 6, "thumb"), ("Megalosaurus", 12, "jaw"), ("Monoclonius", 8, "horn"),
    ("Pentasaurus", 12, "head"), ("Stegosaurus", 18, "plate"), ("Triceratops", 16, "horn"),
    ("Tyrannosaurus Rex", 18, "forearm"), ("Djinn", 7, "lamp"), ("Doppelganger", 4, "face"),
    ("Black Dragon", 7, "*"), ("Plaid Dragon", 7, "sporrin"), ("Blue Dragon", 9, "*"),
    ("Beige Dragon", 9, "*"), ("Brass Dragon", 7, "pole"), ("Tin Dragon", 8, "*"),
    ("Bronze Dragon", 9, "medal"), ("Chromatic Dragon", 16, "scale"), ("Copper Dragon", 8, "loafer"),
    ("Gold Dragon", 8, "filling"), ("Green Dragon", 8, "*"), ("Platinum Dragon", 21, "*"),
    ("Red Dragon", 10, "cocktail"), ("Silver Dragon", 10, "*"), ("White Dragon", 6, "tooth"),
    ("Dragon Turtle", 13, "shell"), ("Dryad", 2, "acorn"), ("Dwarf", 1, "drawers"),
    ("Eel", 2, "sashimi"), ("Efreet", 10, "cinder"), ("Sand Elemental", 8, "glass"),
    ("Bacon Elemental", 10, "bit"), ("Porn Elemental", 12, "lube"), ("Cheese Elemental", 14, "curd"),
    ("Hair Elemental", 16, "follicle"), ("Swamp Elf", 1, "lilypad"), ("Brown Elf", 1, "tusk"),
    ("Sea Elf", 1, "jerkin"), ("Ettin", 10, "fur"), ("Frog", 0, "leg"),
    ("Violet Fungi", 3, "spore"), ("Gargoyle", 4, "gravel"), ("Gelatinous Cube", 4, "jam"),
    ("Ghast", 4, "vomit"), ("Ghost", 10, "*"), ("Ghoul", 2, "muscle"),
    ("Humidity Giant", 12, "drops"), ("Beef Giant", 11, "steak"), ("Quartz Giant", 10, "crystal"),
    ("Porcelain Giant", 9, "fixture"), ("Rice Giant", 8, "grain"), ("Cloud Giant", 12, "condensation"),
    ("Fire Giant", 11, "cigarettes"), ("Frost Giant", 10, "snowman"), ("Hill Giant", 8, "corpse"),
    ("Stone Giant", 9, "hatchling"), ("Storm Giant", 15, "barometer"), ("Mini Giant", 4, "pompadour"),
    ("Gnoll", 2, "collar"), ("Gnome", 1, "hat"), ("Goblin", 1, "ear"),
    ("Grid Bug", 1, "carapace"), ("Jellyrock", 9, "seedling"), ("Beer Golem", 15, "foam"),
    ("Oxygen Golem", 17, "platelet"), ("Cardboard Golem", 14, "recycling"), ("Rubber Golem", 16, "ball"),
    ("Leather Golem", 15, "fob"), ("Gorgon", 8, "testicle"), ("Gray Ooze", 3, "gravy"),
    ("Green Slime", 2, "sample"), ("Griffon", 7, "nest"), ("Banshee", 7, "larynx"),
    ("Harpy", 3, "mascara"), ("Hell Hound", 5, "tongue"), ("Hippocampus", 4, "mane"),
    ("Hippogriff", 3, "egg"), ("Hobgoblin", 1, "patella"), ("Homunculus", 2, "fluid"),
    ("Hydra", 8, "gyrum"), ("Imp", 2, "tail"), ("Invisible Stalker", 8, "*"),
    ("Iron Peasant", 3, "chaff"), ("Jumpskin", 3, "shin"), ("Kobold", 1, "penis"),
    ("Leprechaun", 1, "wallet"), ("Leucrotta", 6, "hoof"), ("Lich", 11, "crown"),
    ("Lizard Man", 2, "tail"), ("Lurker", 10, "sac"), ("Manticore", 6, "spike"),
    ("Mastodon", 12, "tusk"), ("Medusa", 6, "eye"), ("Multicell", 2, "dendrite"),
    ("Pirate", 1, "booty"), ("Berserker", 1, "shirt"), ("Caveman", 2, "club"),
    ("Dervish", 1, "robe"), ("Merman", 1, "trident"), ("Mermaid", 1, "gills"),
    ("Mimic", 9, "hinge"), ("Mind Flayer", 8, "tentacle"), ("Minotaur", 6, "map"),
    ("Yellow Mold", 1, "spore"), ("Morkoth", 7, "teeth"), ("Mummy", 6, "gauze"),
    ("Naga", 9, "rattle"), ("Nebbish", 1, "belly"), ("Neo-Otyugh", 11, "organ "), # Trailing space in original
    ("Nixie", 1, "webbing"), ("Nymph", 3, "hanky"), ("Ochre Jelly", 6, "nucleus"),
    ("Octopus", 2, "beak"), ("Ogre", 4, "talon"), ("Ogre Mage", 5, "apparel"),
    ("Orc", 1, "snout"), ("Otyugh", 7, "organ"), ("Owlbear", 5, "feather"),
    ("Pegasus", 4, "aileron"), ("Peryton", 4, "antler"), ("Piercer", 3, "tip"),
    ("Pixie", 1, "dust"), ("Man-o-war", 3, "tentacle"), ("Purple Worm", 15, "dung"),
    ("Quasit", 3, "tail"), ("Rakshasa", 7, "pajamas"), ("Rat", 0, "tail"), # Note: Rat appears twice
    ("Remorhaz", 11, "protrusion"), ("Roc", 18, "wing"), ("Roper", 11, "twine"),
    ("Rot Grub", 1, "eggsac"), ("Rust Monster", 5, "shavings"), ("Satyr", 5, "hoof"),
    ("Sea Hag", 3, "wart"), ("Silkie", 3, "fur"), ("Shadow", 3, "silhouette"),
    ("Shambling Mound", 10, "mulch"), ("Shedu", 9, "hoof"), ("Shrieker", 3, "stalk"),
    ("Skeleton", 1, "clavicle"), ("Spectre", 7, "vestige"), ("Sphinx", 10, "paw"),
    ("Spider", 0, "web"), ("Sprite", 1, "can"), ("Stirge", 1, "proboscis"),
    ("Stun Bear", 5, "tooth"), ("Stun Worm", 2, "trode"), ("Su-monster", 5, "tail"),
    ("Sylph", 3, "thigh"), ("Titan", 20, "sandal"), ("Trapper", 12, "shag"),
    ("Treant", 10, "acorn"), ("Triton", 3, "scale"), ("Troglodyte", 2, "tail"),
    ("Troll", 6, "hide"), ("Umber Hulk", 8, "claw"), ("Unicorn", 4, "blood"),
    ("Vampire", 8, "pancreas"), ("Wight", 4, "lung"), ("Will-o-the-Wisp", 9, "wisp"),
    ("Wraith", 5, "finger"), ("Wyvern", 7, "wing"), ("Xorn", 7, "jaw"),
    ("Yeti", 4, "fur"), ("Zombie", 2, "forehead"), ("Wasp", 0, "stinger"),
    ("Rat", 1, "tail"), ("Bunny", 0, "ear"), ("Moth", 0, "dust"),
    ("Beagle", 0, "collar"), ("Midge", 0, "corpse"), ("Ostrich", 1, "beak"),
    ("Billy Goat", 1, "beard"), ("Bat", 1, "wing"), ("Koala", 2, "heart"),
    ("Wolf", 2, "paw"), ("Whippet", 2, "collar"), ("Uruk", 2, "boot"),
    ("Poroid", 4, "node"), ("Moakum", 8, "frenum"), ("Fly", 0, "*"),
    ("Hogbird", 3, "curl"),
]

MONSTER_MODS = [
    # (LevelAdj, Pattern | * is placeholder)
    # Note: Corrected "fœtal" to "foetal" for easier typing/compatibility
    (-4, 'foetal *'), (-4, 'dying *'), (-3, 'crippled *'), (-3, 'baby *'),
    (-2, 'adolescent *'), (-2, 'very sick *'), (-1, 'lesser *'), (-1, 'undernourished *'),
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
    # Consonants/clusters (start/mid) - adjusted '' frequency based on likely original intent
    ['br', 'cr', 'dr', 'fr', 'gr', 'j', 'kr', 'l', 'm', 'n', 'pr', '', '', 'r', 'sh', 'tr', 'v', 'wh', 'x', 'y', 'z'],
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
    font-size: 9pt; /* Slightly smaller default */
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
    padding: 2px;
}
QListView::item:selected { /* Style for selection (though we disable it) */
    background-color: #4a4a4a;
    color: #ffffff;
}
QListView::item { /* Add padding between items */
    padding-top: 1px;
    padding-bottom: 1px;
}
QProgressBar {
    border: 1px solid #4a4a4a;
    border-radius: 3px;
    text-align: center;
    background-color: #313131;
    color: #f0f0f0;
    font-size: 8pt; /* Smaller font for progress bars */
    height: 14px; /* Make bars slightly shorter */
}
QProgressBar::chunk {
    background-color: #5a9bcf; /* A blue progress color */
    /* Removed width and margin for default smooth look */
}
QStatusBar {
    background-color: #252525;
    color: #d0d0d0;
    font-size: 8pt;
}
QLabel {
    color: #e0e0e0;
}
QLabel#HeaderLabel {
    font-weight: bold;
    color: #cccccc;
    padding-bottom: 2px; /* Add space below headers */
    padding-top: 4px; /* Add space above headers */
}
QLabel#StatValueLabel {
     font-weight: bold;
     color: #ffffff;
}
QGroupBox {
    border: 1px solid #3a3a3a;
    margin-top: 1.5ex; /* leave space at the top for the title */
    padding-top: 0.5ex;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center; /* position at the top center */
    padding: 0 3px;
    background-color: #2b2b2b;
    color: #e0e0e0;
}
QPushButton {
    background-color: #4a4a4a;
    border: 1px solid #5a5a5a;
    padding: 4px 8px;
    min-width: 50px;
    color: #f0f0f0;
    border-radius: 3px;
    font-size: 9pt;
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
QLineEdit, QComboBox, QListWidget { /* Added QListWidget */
    background-color: #313131;
    border: 1px solid #3a3a3a;
    padding: 3px;
    color: #f0f0f0;
}
QComboBox::drop-down {
    border: 0px;
    width: 15px;
}
QComboBox::down-arrow {
    /* Using a simple character arrow */
     image: none; /* Reset potential image */
}
QComboBox QAbstractItemView { /* Style the dropdown list */
    background-color: #313131;
    border: 1px solid #5a5a5a;
    selection-background-color: #4a4a4a;
}
QDialog {
     background-color: #2b2b2b;
}
QSplitter::handle {
    background-color: #3a3a3a;
}
QSplitter::handle:horizontal {
    width: 1px;
}
QSplitter::handle:vertical {
    height: 1px;
}
"""

# ----------------------------------------------------------------------------
# Helper Functions (Ported/Adapted from Delphi)
# ----------------------------------------------------------------------------

def pick(items):
    """Pick a random item from a list."""
    if not items:
        return None
    return random.choice(items)

def pick_low(items):
    """Pick a random item, biased towards the lower end of the list."""
    if not items:
        return None
    count = len(items)
    if count == 0: return None
    idx1 = random.randrange(count)
    idx2 = random.randrange(count)
    return items[min(idx1, idx2)]

def odds(chance, outof):
    """Return True with a 'chance' out of 'outof' probability."""
    if outof <= 0: return False # Avoid division by zero or weirdness
    return random.randint(1, outof) <= chance

def rand_sign():
    """Return 1 or -1 randomly."""
    return random.choice([1, -1])

def ends(s, e):
    """Check if string s ends with string e."""
    return s.endswith(e)

def plural(s):
    """Basic English pluralization - improved version."""
    if not s: return ""
    s_lower = s.lower()
    # Handle irregulars explicitly if needed (e.g., man -> men)
    if s_lower == 'man': return s[:-3] + 'men' if s.isupper() else s[:-3] + 'Men' if s[0].isupper() else s[:-3] + 'men'
    if s_lower == 'woman': return s[:-5] + 'women' if s.isupper() else s[:-5] + 'Women' if s[0].isupper() else s[:-5] + 'women'
    if s_lower == 'goose': return s[:-4] + 'geese' if s.isupper() else s[:-4] + 'Geese' if s[0].isupper() else s[:-4] + 'geese'
    if s_lower == 'mouse': return s[:-5] + 'mice' if s.isupper() else s[:-5] + 'Mice' if s[0].isupper() else s[:-5] + 'mice'
    if s_lower == 'tooth': return s[:-5] + 'teeth' if s.isupper() else s[:-5] + 'Teeth' if s[0].isupper() else s[:-5] + 'teeth'
    # Add more irregulars as found/needed

    # General rules
    if re.search('[sxz]$', s_lower) or re.search('[^aeioudgkprt]h$', s_lower):
        return s + 'es'
    elif re.search('[^aeiou]y$', s_lower):
        return s[:-1] + 'ies'
    elif s_lower.endswith('f'):
        return s[:-1] + 'ves'
    elif s_lower.endswith('fe'):
        return s[:-2] + 'ves'
    elif s_lower.endswith('us') and len(s_lower) > 2: # Avoid 'bus' -> 'bi'
         return s[:-2] + 'i'
    else:
        return s + 's'

def indefinite_article(s):
    """Return 'a' or 'an' based on the first letter of s."""
    if not s: return ""
    # Basic check - doesn't handle 'hour', 'unicorn', etc.
    return 'an' if s[0].lower() in 'aeiou' else 'a'

def indefinite(s, qty):
    """Format a quantity and noun with indefinite article or pluralization."""
    if qty == 1:
        return f"{indefinite_article(s)} {s}"
    else:
        # Handle cases like "1 gold piece" vs "2 gold pieces"
        if s == "Gold Piece":
            return f"{qty} {plural(s)}" if qty != 1 else f"{qty} {s}"
        return f"{qty} {plural(s)}"

def definite(s, qty):
     """Format a quantity and noun with definite article and pluralization."""
     # Handle cases like "the gold piece" vs "the gold pieces"
     if s == "Gold Piece":
          return f"the {plural(s) if qty != 1 else s}"
     return f"the {plural(s) if qty > 1 else s}"

def int_to_roman(num):
    """Convert an integer to Roman numeral string. Handles 1 to 39999."""
    if not isinstance(num, int) or not 0 < num < 40000:
        return str(num) # Fallback for out-of-range or non-integers

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
    while num > 0 and i < len(val):
        for _ in range(num // val[i]):
            roman_num += syb[i]
            num -= val[i]
        i += 1
    return roman_num

def roman_to_int(s):
    """Convert a Roman numeral string (potentially with T, A, M) to an integer."""
    if not isinstance(s, str) or not s: return 0
    s = s.upper()
    roman_map = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000, 'A': 5000, 'T': 10000}
    int_val = 0
    i = 0
    while i < len(s):
        # Check for two-character subtractive combinations (MT, MA, CM, CD, XC, XL, IX, IV)
        if i + 1 < len(s):
            two_char = s[i:i+2]
            v1 = roman_map.get(s[i], 0)
            v2 = roman_map.get(s[i+1], 0)

            if v1 < v2: # Subtractive case
                 # Check specifically for the valid subtractive pairs
                 if two_char in ["MT", "MA", "CM", "CD", "XC", "XL", "IX", "IV"]:
                     int_val += (v2 - v1)
                     i += 2
                     continue
                 else: # Invalid subtractive pair (e.g., IM) - treat as error or ignore
                     # For robustness, we'll just process the first character
                     int_val += v1
                     i += 1
            else: # Additive case or same value
                int_val += v1
                i += 1
        else: # Last character
            int_val += roman_map.get(s[i], 0)
            i += 1
    # Fallback if it wasn't Roman
    if int_val == 0 and s != '':
        try: return int(s)
        except ValueError: return 0
    return int_val


def generate_name():
    """Generate a random fantasy-style name."""
    name = ""
    syllables = random.randint(2, 4) # Control name length via syllables
    for i in range(syllables):
        # Simple structure: Consonant(s) + Vowel + Optional End Consonant
        start_cons = pick(NAME_PARTS[0])
        vowel = pick(NAME_PARTS[1])
        end_cons = ""
        # Add ending consonant less frequently, especially for shorter names or last syllable
        if odds(1, 2) and (i < syllables -1 or odds(1,3)):
            end_cons = pick(NAME_PARTS[2])

        name += start_cons + vowel + end_cons

    # Ensure it doesn't start/end awkwardly (e.g., with empty string parts)
    name = re.sub(r'^[^a-zA-Z]+', '', name) # Remove leading non-alpha (if start_cons was '')
    name = re.sub(r'[^a-zA-Z]+$', '', name) # Remove trailing non-alpha

    return name.capitalize() if name else "Adventurer" # Fallback


def calculate_xp_for_level(level):
    """Calculate the total time (in milliseconds) needed to reach the *next* level."""
    # Corresponds to LevelUpTime in Delphi (converted to ms)
    if level <= 0: level = 1 # Ensure level is at least 1 for calculation
    base_time_seconds = 20 * 60 # ~20 minutes base duration for level 1
    try:
        # Using math.pow for potentially large exponents
        level_factor = math.pow(1.15, level -1) # Adjust exponent base relative to level 1
    except OverflowError:
        level_factor = float('inf') # Handle very high levels
    # Original seems exponential *duration*, not cumulative XP.
    return round((20.0 + level_factor) * 60.0 * 1000.0) # Result in milliseconds

def rough_time(seconds_float):
    """Convert seconds (float) into a human-readable duration string."""
    if not isinstance(seconds_float, (int, float)) or seconds_float < 0:
        return "???"
    seconds = int(seconds_float)
    if seconds < 120:
        return f"{seconds} seconds"
    elif seconds < 60 * 120:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes} min {secs} sec" if secs > 0 else f"{minutes} minutes"
    elif seconds < 60 * 60 * 48:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours} hr {minutes} min" if minutes > 0 else f"{hours} hours"
    else:
        days = seconds // (3600 * 24)
        hours = (seconds % (3600 * 24)) // 3600
        return f"{days} days {hours} hr" if hours > 0 else f"{days} days"

# END OF FILE: config_data.py
```

```python
# START OF FILE: game_logic.py
# File: game_logic.py
import random
import math
import time
from config_data import * # Import all data and helper functions

from PySide6.QtCore import QObject, Signal

class GameLogic(QObject):
    # Signal emitted when UI needs refresh, includes a string describing the major change (optional)
    state_updated = Signal(str)

    def __init__(self):
        super().__init__()
        self.character = {}
        self.plot_acts = []
        self.quests = []
        self.game_loaded = False
        self.last_tick_time = 0
        self.reset_state() # Initialize with default empty state

    def reset_state(self):
        """Resets the game state to initial defaults (before character creation)."""
        self.character = {
            "Name": "Adventurer",
            "Race": "Human",
            "Class": "Fighter",
            "Level": 0,
            "Stats": {"STR": 10, "CON": 10, "DEX": 10, "INT": 10, "WIS": 10, "CHA": 10},
            "HPMax": 10,
            "MPMax": 10,
            "Equipment": {slot: "" for slot in EQUIPMENT_SLOTS},
            "Inventory": {"Gold Piece": 0}, # ItemName: Quantity
            "Spells": {}, # SpellName: RomanLevelString
            "Gold": 0, # Keep separate track for easy access, sync with Inventory
            "Motto": "",
            "Guild": "",
        }
        self.plot_acts = ["Prologue"]
        self.quests = [] # Store tuples (description, is_complete)

        # Progress Tracking (value, max_value)
        self.task_progress = 0
        self.task_max = 1
        self.task_description = "Initializing..."
        self.task_type = "idle" # e.g., idle, executing, travel_market, selling, buying, travel_combat
        self.item_being_sold = None

        self.xp_progress = 0
        self.xp_max = calculate_xp_for_level(1)

        self.quest_progress = 0
        self.quest_max = 10000
        self.quest_description = "Awaiting orders"
        self.quest_target_monster = None # Store data of specific monster for exterminate quests

        self.plot_progress = 0
        # Plot max duration increases significantly per act
        self.plot_max = calculate_xp_for_level(1) * 10 # Prologue duration scaled

        self.encumbrance = 0
        self.encumbrance_max = BASE_ENCUMBRANCE + self.character["Stats"].get("STR", 10)

        self.current_target_monster = None # Info about monster currently being fought
        self.last_tick_time = time.monotonic() * 1000 # Milliseconds

        self.game_loaded = False # Flag to prevent ticks before ready

    def initialize_new_character(self, name, race, klass, stats):
        """Set up the character after creation."""
        self.reset_state() # Start fresh
        self.character["Name"] = name
        self.character["Race"] = race
        self.character["Class"] = klass
        self.character["Stats"] = stats.copy() # Use a copy
        self.character["Level"] = 1 # Start at level 1 now
        self.character["HPMax"] = random.randint(4, 8) + math.floor(stats.get("CON", 10) / 6)
        self.character["MPMax"] = random.randint(4, 8) + math.floor(stats.get("INT", 10) / 6)
        self.character["Equipment"]["Weapon"] = "Sharp Stick"
        self.character["Inventory"] = {"Gold Piece": 0}
        self.character["Gold"] = 0
        self.character["Spells"] = {}
        self.plot_acts = ["Prologue"] # Reset acts
        self.encumbrance_max = BASE_ENCUMBRANCE + self.character["Stats"]["STR"]
        self.xp_max = calculate_xp_for_level(self.character["Level"] + 1) # XP needed for level 2
        self.xp_progress = 0
        self.plot_progress = 0
        self.plot_max = calculate_xp_for_level(len(self.plot_acts) + 1) * 10

        self.assign_new_quest() # Get the first quest
        self.quest_progress = 0

        # Set initial task chain
        self.set_new_task("Experiencing an enigmatic and foreboding night vision", 10 * 1000, "cinematic")
        # Add more initial tasks here if needed, maybe via a queue later

        self.game_loaded = True
        self.last_tick_time = time.monotonic() * 1000 # Reset tick time
        print(f"Character Initialized: {self.character['Name']}")
        self.state_updated.emit("Character Created")

    def tick(self):
        """Main game loop tick, called by the timer."""
        if not self.game_loaded:
            return

        current_time = time.monotonic() * 1000
        # Protect against system clock changes / large jumps
        elapsed_ms = min(max(0, current_time - self.last_tick_time), TIMER_INTERVAL_MS * 5)
        self.last_tick_time = current_time

        if elapsed_ms <= 0: return

        self.task_progress += elapsed_ms
        major_update_reason = None # Track if something significant happened

        if self.task_progress >= self.task_max:
            # --- Task Completion ---
            completed_task_type = self.task_type
            task_duration_ms = self.task_max # Store duration before resetting

            # 1. Resolve Task Effects (Loot, Sales, Purchases etc.)
            if completed_task_type == "executing" and self.current_target_monster:
                self.resolve_monster_defeat()
                self.current_target_monster = None # Clear target after resolution
                major_update_reason = "Combat End"
            elif completed_task_type == "selling" and self.item_being_sold:
                self.resolve_item_sale()
                self.item_being_sold = None # Clear item after selling
                major_update_reason = "Item Sold"
            elif completed_task_type == "buying":
                self.resolve_equipment_purchase()
                major_update_reason = "Equipment Bought"

            # 2. Update Progress Bars if task was productive
            # Gain based on task *duration*, not arbitrary number
            xp_gain_from_task = task_duration_ms / 1000 # XP = seconds spent
            if completed_task_type in ["executing", "cinematic", "travel_combat"]: # Define which tasks grant progress
                self.xp_progress += xp_gain_from_task
                self.quest_progress += xp_gain_from_task
                self.plot_progress += xp_gain_from_task

            # 3. Check for Level/Quest/Plot Completion *after* updating progress
            level_up_occurred = self.check_level_up()
            if level_up_occurred: major_update_reason = "Level Up"

            quest_complete_occurred = self.check_quest_completion()
            if quest_complete_occurred: major_update_reason = "Quest Complete"

            plot_complete_occurred = self.check_plot_completion()
            if plot_complete_occurred: major_update_reason = "Act Complete"

            # 4. Determine and Set Next Task (Important: after resolving current)
            self.determine_next_task()

        # --- Emit signal for UI refresh ---
        # Emit always to show smooth progress, or only on major updates?
        # Let's emit always for smoothness. The reason helps UI decide if full redraw needed.
        self.state_updated.emit(major_update_reason or "Tick")

    def resolve_monster_defeat(self):
        """Grant rewards for defeating the current target monster."""
        if not self.current_target_monster: return
        print(f"Defeated {self.current_target_monster.get('name_mod', 'monster')}")
        loot_item_name = self.current_target_monster.get("loot")
        if loot_item_name and loot_item_name != '*':
            # Use the *modified* monster name for context if available
            item_base = f"{self.current_target_monster.get('name_mod', self.current_target_monster.get('name_orig','Unknown'))} {loot_item_name}"
            self.add_inventory_item(item_base.capitalize())
        elif odds(1, 5): # Chance for generic interesting/boring item
            self.add_inventory_item(self.generate_random_loot())

        if odds(1, 2): # Chance for gold
            level = self.character.get("Level", 1)
            gold_found = random.randint(1, level * 2 + 1)
            self.add_inventory_item("Gold Piece", gold_found)

    def resolve_item_sale(self):
        """Grant gold for the sold item and remove it."""
        if not self.item_being_sold: return
        item_name = self.item_being_sold
        current_qty = self.character["Inventory"].get(item_name, 0)
        if current_qty > 0:
            # Calculate sale price (simple for now)
            base_value = 1 + roman_to_int(re.sub(r'[^IVXLCDMTA]', '', item_name)) # Crude value from roman numerals in name?
            level = self.character.get("Level", 1)
            gold_gained = max(1, int(base_value * level * random.uniform(0.1, 0.5)))
            if " of " in item_name or any(attrib in item_name for attrib in ITEM_ATTRIB): # Special item bonus
                gold_gained *= random.randint(2, 5)

            print(f"Sold {item_name} for {gold_gained} gold.")
            self.add_inventory_item("Gold Piece", gold_gained)
            self.add_inventory_item(item_name, -1) # Remove one quantity
        else:
             print(f"Warning: Tried to sell {item_name}, but none in inventory.")
             if item_name in self.character["Inventory"]: # Clean up if somehow qty is 0
                 del self.character["Inventory"][item_name]

    def resolve_equipment_purchase(self):
        """Spend gold and potentially get better equipment."""
        cost = self.calculate_equip_price()
        if self.character["Gold"] >= cost:
            self.add_inventory_item("Gold Piece", -cost)
            print(f"Spent {cost} gold on equipment.")
            self.generate_and_equip_item(force_upgrade=True)
        else:
             print("Could not afford new equipment.")


    def set_new_task(self, description, duration_ms, task_type="unknown"):
        """Sets the current task, type, and resets progress."""
        self.task_description = description
        self.task_max = max(100, duration_ms) # Ensure minimum duration
        self.task_progress = 0
        self.task_type = task_type
        print(f"New Task [{self.task_type}]: {self.task_description} ({self.task_max/1000:.1f}s)")

    def check_level_up(self):
        """Check if XP threshold is met and perform level up."""
        if self.xp_progress >= self.xp_max:
            current_level = self.character["Level"]
            self.character["Level"] += 1
            print(f"LEVEL UP! Reached Level {self.character['Level']}")
            # Increase HP/MP based on CON/INT
            con_bonus = math.floor(self.character["Stats"].get("CON", 10) / 6)
            int_bonus = math.floor(self.character["Stats"].get("INT", 10) / 6)
            self.character["HPMax"] += max(1, random.randint(1, 4) + con_bonus)
            self.character["MPMax"] += max(1, random.randint(1, 4) + int_bonus)

            # Grant stat points (e.g., 2 points) - apply race/class bonus logic here?
            # Simple random gain for now:
            for _ in range(2):
                stat_to_increase = random.choice(list(self.character["Stats"].keys()))
                self.character["Stats"][stat_to_increase] += 1

            # Learn a new spell
            self.learn_new_spell()

            # Reset XP bar for next level
            # Rollover XP:
            self.xp_progress -= self.xp_max
            self.xp_max = calculate_xp_for_level(self.character["Level"] + 1)
            self.encumbrance_max = BASE_ENCUMBRANCE + self.character["Stats"]["STR"]

            # TODO: Trigger "Brag" for multiplayer if implemented
            return True
        return False

    def learn_new_spell(self):
         """Try to learn a new spell based on level and WIS."""
         # Chance increases with WIS? For now, just pick if possible.
         if len(self.character["Spells"]) < len(SPELLS):
                eligible_spells = [s for s in SPELLS if s not in self.character["Spells"]]
                if eligible_spells:
                    new_spell = pick_low(eligible_spells) # Bias towards earlier spells
                    # Assign a level based on character level progress
                    # Make spell level progression slower
                    spell_level_int = max(1, 1 + math.floor(self.character["Level"] / 7))
                    self.character["Spells"][new_spell] = int_to_roman(spell_level_int)
                    print(f"Learned Spell: {new_spell} {self.character['Spells'][new_spell]}")


    def check_quest_completion(self):
        """Check if quest progress is met, grant reward, assign new quest."""
        if self.quest_progress >= self.quest_max and self.quests:
            last_quest_desc, was_complete = self.quests[-1]
            if not was_complete: # Only complete it once
                print(f"Quest Complete: {last_quest_desc}")
                self.quests[-1] = (last_quest_desc, True) # Mark as complete

                # Grant reward
                self.grant_quest_reward()
                self.assign_new_quest() # Assign the next one
                return True
        return False

    def grant_quest_reward(self):
        """Give a random reward for completing a quest."""
        reward_type = random.choice(["stat", "equip", "item", "spell"])
        print("Quest Reward: ", end="")
        if reward_type == "stat":
            stat_to_increase = random.choice(list(self.character["Stats"].keys()))
            self.character["Stats"][stat_to_increase] += 1
            print(f"Stat point ({stat_to_increase})!")
        elif reward_type == "equip":
            self.generate_and_equip_item()
            print("Equipment!")
        elif reward_type == "item":
                self.add_inventory_item(self.generate_random_loot(force_special=True))
                print("Item!")
        elif reward_type == "spell":
            self.learn_new_spell()
            print("Spell!") # May not print if no new spell available

    def check_plot_completion(self):
        """Check if plot progress is met, grant reward, advance act."""
        if self.plot_progress >= self.plot_max and self.plot_acts:
            print(f"Act Complete: {self.plot_acts[-1]}")
            current_act_num = len(self.plot_acts) # Prologue is 1st
            next_act_name = f"Act {int_to_roman(current_act_num)}"
            self.plot_acts.append(next_act_name)
            self.plot_progress = 0 # Reset progress for the new act

            # Plot max duration increases significantly per act (based on time for *next* level)
            time_for_next_level = calculate_xp_for_level(self.character.get("Level", 1) + 1)
            self.plot_max = time_for_next_level * (5 + current_act_num * 2) * 10 # arbitrary scaling

            # Grant reward for completing act
            print(f"Starting {next_act_name} (Duration: {rough_time(self.plot_max/1000)})")
            if current_act_num > 0: self.generate_and_equip_item(force_upgrade=True)
            if current_act_num > 1: self.add_inventory_item(self.generate_random_loot(force_special=True))

            # TODO: Trigger "Brag" for multiplayer if implemented
            return True
        return False

    def assign_new_quest(self):
        """Generate and assign a new quest, resetting progress."""
        quest_type = random.randint(0, 4)
        new_quest_desc = "ERROR: Quest Gen Failed"
        self.quest_target_monster = None # Reset quest monster target

        level = self.character.get("Level", 1)
        try:
            if quest_type == 0: # Exterminate
                target_monster_data = self.select_monster_near_level(level)
                if target_monster_data:
                    qty = random.randint(2, 5)
                    plural_name = plural(target_monster_data['name_orig'])
                    new_quest_desc = f"Exterminate the {plural_name}"
                    self.quest_target_monster = target_monster_data # Store for potential task use
                else: new_quest_desc = "Find something to exterminate"
            elif quest_type == 1: # Seek Item
                item_name = self.generate_random_loot(force_special=True)
                new_quest_desc = f"Seek the {item_name}"
            elif quest_type == 2: # Deliver Item
                item_name = pick(BORING_ITEMS)
                new_quest_desc = f"Deliver this {item_name}"
            elif quest_type == 3: # Fetch Item
                item_name = pick(BORING_ITEMS)
                new_quest_desc = f"Fetch me {indefinite(item_name, 1)}"
            elif quest_type == 4: # Placate
                target_monster_data = self.select_monster_near_level(level)
                if target_monster_data:
                    qty = random.randint(2, 4)
                    plural_name = plural(target_monster_data['name_orig'])
                    new_quest_desc = f"Placate the {plural_name}"
                else: new_quest_desc = "Find someone to placate"
        except Exception as e:
            print(f"Error generating quest: {e}")
            new_quest_desc = "Do something heroic"


        self.quests.append((new_quest_desc, False)) # Add as tuple (description, is_complete)
        if len(self.quests) > 15: # Limit quest history visually
            self.quests.pop(0)

        self.quest_description = new_quest_desc
        self.quest_progress = 0
        # Quest duration scales with level, make it shorter than leveling/acts
        base_quest_duration_ms = calculate_xp_for_level(level + 1) / random.randint(4, 8) # Fraction of level time
        self.quest_max = max(10000, base_quest_duration_ms * random.uniform(0.8, 1.2))

        print(f"New Quest: {self.quest_description} (Duration: ~{rough_time(self.quest_max/1000)})")

    def determine_next_task(self):
        """Decide what the character should do next based on state."""
        enc = self.calculate_encumbrance()
        # print(f"Determining task: Enc={enc}/{self.encumbrance_max}, Gold={self.character['Gold']}, TaskType={self.task_type}")

        if enc >= self.encumbrance_max and self.task_type != "travel_market" and self.task_type != "selling":
            self.set_new_task("Heading to market to sell loot", 4 * 1000, "travel_market")
        elif self.task_type == "travel_market": # Just arrived at market
             self.try_selling_items() # Will set task to 'selling' or 'idle_market'
        elif self.task_type == "selling": # Finished selling one item
             self.try_selling_items() # Try selling the next, or sets 'idle_market'
        elif self.task_type == "idle_market": # Finished selling
            # Now decide if we buy or leave
            if self.character["Gold"] > self.calculate_equip_price() and odds(3, 5): # High chance to buy if affordable after selling
                 self.set_new_task("Negotiating purchase of better equipment", 5 * 1000, "buying")
            else:
                 self.set_new_task("Leaving market", 2 * 1000, "travel_combat") # Assume leaving market heads towards combat
        elif self.task_type == "buying": # Finished buying attempt
             # After buying, always head towards combat for simplicity
             self.set_new_task("Heading to the killing fields", 4 * 1000, "travel_combat")
        elif self.character["Gold"] > self.calculate_equip_price() * 1.5 and odds(1, 8): # Lower chance to spontaneously buy if rich
             self.set_new_task("Negotiating purchase of better equipment", 5 * 1000, "buying")
        else: # Default: Go fight something
             # If previous task wasn't combat-related, add travel time
             if self.task_type not in ["executing", "travel_combat"]:
                 self.set_new_task("Heading to the killing fields", random.randint(2, 5) * 1000, "travel_combat")
             else: # Already in the fields or just finished fighting
                 self.generate_monster_encounter_task() # This sets task_type to 'executing'


    def try_selling_items(self):
        """Attempt to sell the next sellable item in inventory. Sets next task."""
        # Find the first item that isn't Gold Piece
        item_to_sell = None
        for name, qty in self.character["Inventory"].items():
            if name != "Gold Piece" and qty > 0:
                item_to_sell = name
                break

        if item_to_sell:
            self.set_new_task(f"Selling {indefinite(item_to_sell, 1)}", 1 * 1000, "selling")
            self.item_being_sold = item_to_sell
        else:
            # No more items to sell
            self.set_new_task("Finished selling loot", 100, "idle_market") # Very short task to transition state


    def generate_monster_encounter_task(self):
        """Generate a monster encounter and set it as the current task."""
        char_level = self.character.get("Level", 1)

        # Use quest target if applicable and available
        monster_data_source = self.quest_target_monster if self.quest_target_monster and odds(2, 3) else None
        if not monster_data_source:
             monster_data_source = self.select_monster_near_level(char_level)

        if not monster_data_source:
             print("Error: Could not select a monster!")
             self.set_new_task("Looking for trouble", 3*1000, "exploring") # Fallback task
             return

        # Create a mutable copy for modification
        target_monster = monster_data_source.copy()

        # --- Determine Monster Modifiers and Effective Level ---
        base_monster_level = target_monster.get("level", 0)
        level_diff = char_level - base_monster_level
        effective_monster_level = base_monster_level
        monster_name_mod = target_monster.get("name_orig", "Unknown Monster")

        # Apply mods based on level difference (more nuanced)
        mod_applied_name = ""
        if level_diff > 5 and odds(1, 2): # Character significantly stronger
            weakening_mods = [m for m in MONSTER_MODS if m[0] < 0]
            if weakening_mods:
                mod = pick(weakening_mods)
                effective_monster_level += mod[0]
                mod_applied_name = mod[1].replace("*", monster_name_mod)
        elif level_diff < -5 and odds(1, 2): # Monster significantly stronger
            strengthening_mods = [m for m in MONSTER_MODS if m[0] > 0]
            if strengthening_mods:
                mod = pick(strengthening_mods)
                effective_monster_level += mod[0]
                mod_applied_name = mod[1].replace("*", monster_name_mod)
        elif abs(level_diff) <= 5 and odds(1, 4): # Closer level, smaller chance for any mod
             all_mods = [m for m in MONSTER_MODS]
             if all_mods:
                 mod = pick(all_mods)
                 effective_monster_level += mod[0]
                 mod_applied_name = mod[1].replace("*", monster_name_mod)

        # Use modified name if a mod was applied
        final_monster_name = mod_applied_name if mod_applied_name else monster_name_mod
        target_monster["name_mod"] = final_monster_name # Store modified name
        effective_monster_level = max(0, effective_monster_level) # Monster level can't be negative

        # --- Determine Quantity ---
        qty = 1
        if effective_monster_level > 0 and char_level > effective_monster_level + 5:
            # Spawn multiples if character level is much higher
            qty = min(5, (char_level // effective_monster_level) + random.randint(0, 1))
        elif effective_monster_level > char_level + 10:
             qty = 1 # Don't swarm if monster is already way stronger

        # Total effective level for the encounter
        total_encounter_level = effective_monster_level * qty

        # --- Calculate Task Duration ---
        # Duration based on relative power levels
        if char_level <= 0: char_level = 1 # Avoid division by zero
        relative_power = total_encounter_level / char_level
        base_duration_ms = 5000 # 5 seconds base

        # Scale duration: longer for tougher fights, shorter for easier ones
        duration_factor = math.pow(max(0.5, relative_power), 0.7) # Dampen the scaling
        duration_ms = int(base_duration_ms * duration_factor * random.uniform(0.8, 1.2))
        duration_ms = max(2000, min(duration_ms, 60000)) # Clamp duration (2s to 60s)

        # --- Set Task ---
        task_desc = f"Executing {indefinite(final_monster_name, qty)}"
        self.set_new_task(task_desc, duration_ms, "executing")
        # Store monster info for loot resolution later
        self.current_target_monster = target_monster
        # Include quantity for potential future use (e.g., calculating XP/loot based on # defeated)
        self.current_target_monster["quantity"] = qty


    def select_monster_near_level(self, level):
        """Select a monster definition reasonably close to the target level."""
        if not MONSTERS: return None
        # Filter out extremely high/low level monsters relative to character? Optional.
        # candidates = [m for m in MONSTERS if abs(m[1] - level) <= level + 5] # Example filter
        # if not candidates: candidates = MONSTERS # Fallback if filter is too strict

        # Sort by absolute level difference
        candidates = sorted(MONSTERS, key=lambda m: abs(m[1] - level))

        # Pick from the closest N monsters to add variety, ensuring N is not out of bounds
        num_closest = min(len(candidates), 7) # Consider 7 closest
        if num_closest == 0: return None # Should not happen if MONSTERS is not empty

        selected_monster_tuple = pick(candidates[:num_closest])

        return {
            "name_orig": selected_monster_tuple[0],
            "level": selected_monster_tuple[1],
            "loot": selected_monster_tuple[2]
            # name_mod will be added later
        }

    def generate_and_equip_item(self, slot_index=None, force_upgrade=False):
        """Generate a new piece of equipment and equip it."""
        if slot_index is None:
            # Pick a random slot, maybe biased towards weapon/armor?
            slot_index = random.randrange(len(EQUIPMENT_SLOTS))
        slot_name = EQUIPMENT_SLOTS[slot_index]

        char_level = self.character.get("Level", 1)
        base_items = []
        good_mods, bad_mods = [], []

        # Select appropriate item lists based on slot
        if slot_name == "Weapon":
            base_items, good_mods, bad_mods = WEAPONS, OFFENSE_ATTRIB, OFFENSE_BAD
        elif slot_name == "Shield":
            base_items, good_mods, bad_mods = SHIELDS, DEFENSE_ATTRIB, DEFENSE_BAD
        elif slot_name in EQUIPMENT_SLOTS: # Assume others use Armor stats
             base_items, good_mods, bad_mods = ARMORS, DEFENSE_ATTRIB, DEFENSE_BAD
        else:
            print(f"Warning: Unknown equipment slot '{slot_name}'")
            return # Unknown slot

        if not base_items:
             print(f"Warning: No base items defined for slot '{slot_name}'")
             return

        # --- Select Base Item ---
        # Select base item considering character level
        # Pick from ~10 closest level items for variety
        sorted_bases = sorted(base_items, key=lambda item: abs(item[1] - char_level))
        candidates = sorted_bases[:min(len(sorted_bases), 10)]
        if not candidates: candidates = base_items # Fallback if sorting/slicing fails
        base_item_tuple = pick(candidates)

        item_name = base_item_tuple[0]
        base_value = base_item_tuple[1]

        # --- Apply Modifiers ---
        level_diff = char_level - base_value
        # If forced upgrade, ensure level_diff is positive or slightly increased
        if force_upgrade:
             level_diff = max(1, level_diff + random.randint(0, char_level // 5))

        current_mods_value = 0
        num_mods = 0
        max_mods = 2 # Max number of named modifiers
        applied_mod_names = []

        # Determine which modifier list to use (good or bad)
        mods_to_use = good_mods if level_diff > 0 else bad_mods

        # Apply named modifiers iteratively
        temp_level_diff = level_diff # Work with a temporary difference
        while num_mods < max_mods and abs(temp_level_diff) > 0 and mods_to_use:
            # Find mods that fit within the remaining difference
            # Ensure mod value sign matches temp_level_diff sign
            sign_match = lambda mv: (mv > 0 and temp_level_diff > 0) or (mv < 0 and temp_level_diff < 0) or mv == 0
            possible_mods = [m for m in mods_to_use
                             if abs(m[1]) <= abs(temp_level_diff) and sign_match(m[1]) and m[0] not in applied_mod_names]

            if not possible_mods: break # No suitable mods left

            # Pick a mod, maybe bias towards larger values? Simple pick for now.
            mod_tuple = pick(possible_mods)
            mod_name = mod_tuple[0]
            mod_value = mod_tuple[1]

            # Prepend modifier name
            item_name = f"{mod_name} {item_name}"
            applied_mod_names.append(mod_name)
            current_mods_value += mod_value
            temp_level_diff -= mod_value # Reduce remaining difference
            num_mods += 1

        # Add numeric prefix if difference still remains after named mods
        final_diff = level_diff - current_mods_value
        if final_diff != 0:
             prefix = f"+{final_diff}" if final_diff > 0 else str(final_diff)
             item_name = f"{prefix} {item_name}"

        # --- Equip Item ---
        # Simple equip: always replace current item in slot
        # Future: could add logic to compare with existing item value
        self.character["Equipment"][slot_name] = item_name
        print(f"Equipped: {item_name} in slot {slot_name}")

    def generate_random_loot(self, force_special=False):
        """Generate a random boring or special item name."""
        if force_special or odds(1, 5): # 1 in 5 chance for special item
             # Ensure all parts are selected
             attrib = pick(ITEM_ATTRIB) or "Plain"
             special = pick(SPECIALS) or "Thingy"
             of_part = pick(ITEM_OFS) or "Average"
             return f"{attrib} {special} of {of_part}"
        else:
             return pick(BORING_ITEMS) or "Chunk of Dirt" # Fallback


    def add_inventory_item(self, item_name, quantity=1):
        """Add or remove an item from the inventory, updating gold separately."""
        if not item_name: return

        is_gold = item_name == "Gold Piece"

        # Update Gold tracker
        if is_gold:
            self.character["Gold"] = max(0, self.character.get("Gold", 0) + quantity)

        # Update Inventory dictionary
        current_qty = self.character["Inventory"].get(item_name, 0)
        new_qty = max(0, current_qty + quantity)

        log_action = "Added" if quantity > 0 else "Removed"
        log_qty = abs(quantity)

        if new_qty > 0:
            self.character["Inventory"][item_name] = new_qty
            # Only log if quantity actually changed or item was added
            if new_qty != current_qty:
                 print(f"Inventory: {log_action} {log_qty}x {item_name} (now {new_qty})")
        elif item_name in self.character["Inventory"]: # Remove if quantity drops to 0 or less
             del self.character["Inventory"][item_name]
             print(f"Inventory: Removed {log_qty}x {item_name} (now 0)")

        # Don't emit state update here, let the main tick loop handle it after encumbrance calc

    def calculate_encumbrance(self):
        """Calculate current encumbrance based on inventory item count (excluding gold)."""
        total_items = 0
        for name, qty in self.character.get("Inventory", {}).items():
            if name != "Gold Piece":
                total_items += qty
        return total_items

    def calculate_equip_price(self):
        """Calculate the cost of buying new equipment based on level."""
        level = self.character.get("Level", 1)
        if level <= 0: level = 1
        return 5 * level * level + 10 * level + 20

    # --- Getters for UI ---
    def get_state(self):
        """Return a dictionary representing the current game state for UI updates."""
        # Ensure quests is a list of tuples before accessing
        current_quest_desc = "None"
        if self.quests and isinstance(self.quests[-1], tuple):
            current_quest_desc = self.quests[-1][0]
        elif self.quests and isinstance(self.quests[-1], str): # Compatibility with old string list
             current_quest_desc = self.quests[-1]


        return {
            "character": self.character,
            "plot_acts": self.plot_acts,
            "quests": self.quests, # List of tuples: (desc, is_complete)
            "task_description": self.task_description,
            "task_progress": self.task_progress,
            "task_max": self.task_max,
            "xp_progress": self.xp_progress,
            "xp_max": self.xp_max,
            "quest_description": current_quest_desc,
            "quest_progress": self.quest_progress,
            "quest_max": self.quest_max,
            "plot_progress": self.plot_progress,
            "plot_max": self.plot_max,
            "encumbrance": self.calculate_encumbrance(), # Recalculate fresh
            "encumbrance_max": self.encumbrance_max,
            "current_act": self.plot_acts[-1] if self.plot_acts else "None"
        }

    def get_state_for_saving(self):
        """Return a dictionary representing the current game state for saving."""
        state = self.get_state() # Get the base state
        # Add non-UI critical state variables
        state["task_type"] = self.task_type
        state["item_being_sold"] = self.item_being_sold
        state["current_target_monster"] = self.current_target_monster
        state["quest_target_monster"] = self.quest_target_monster
        # Store last tick time to handle time passing while game was closed (optional, complex)
        # state["last_tick_time_saved"] = time.monotonic() * 1000
        state["game_loaded"] = self.game_loaded # Save this flag too
        return state

    def apply_loaded_state(self, loaded_state):
        """Apply a loaded state to the game logic."""
        try:
            self.character = loaded_state.get("character", {})
            self.plot_acts = loaded_state.get("plot_acts", ["Prologue"])
            # Handle old save format where quests might be strings
            loaded_quests = loaded_state.get("quests", [])
            self.quests = []
            for q in loaded_quests:
                if isinstance(q, tuple):
                    self.quests.append(q)
                elif isinstance(q, str):
                    # Assume old quests are complete except the last one maybe? Risky.
                    # Safer: mark all loaded string quests as complete.
                    self.quests.append((q, True))


            self.task_description = loaded_state.get("task_description", "Loaded Game")
            self.task_progress = loaded_state.get("task_progress", 0)
            self.task_max = loaded_state.get("task_max", 1000)
            self.xp_progress = loaded_state.get("xp_progress", 0)
            self.xp_max = loaded_state.get("xp_max", calculate_xp_for_level(self.character.get("Level", 1) + 1))
            self.quest_description = loaded_state.get("quest_description", "Awaiting orders")
            self.quest_progress = loaded_state.get("quest_progress", 0)
            self.quest_max = loaded_state.get("quest_max", 10000)
            self.plot_progress = loaded_state.get("plot_progress", 0)
            self.plot_max = loaded_state.get("plot_max", calculate_xp_for_level(len(self.plot_acts) + 1) * 10)
            self.encumbrance_max = loaded_state.get("encumbrance_max", BASE_ENCUMBRANCE + self.character.get("Stats", {}).get("STR", 10))
            # Encumbrance itself is calculated dynamically

            self.task_type = loaded_state.get("task_type", "idle")
            self.item_being_sold = loaded_state.get("item_being_sold", None)
            self.current_target_monster = loaded_state.get("current_target_monster", None)
            self.quest_target_monster = loaded_state.get("quest_target_monster", None)

            self.game_loaded = loaded_state.get("game_loaded", True) # Assume loaded is true
            self.last_tick_time = time.monotonic() * 1000 # Reset timer on load

            # Ensure Gold is synced
            self.character["Gold"] = self.character.get("Inventory", {}).get("Gold Piece", 0)

            # Validate / recalculate dependent values
            self.encumbrance_max = BASE_ENCUMBRANCE + self.character.get("Stats", {}).get("STR", 10)
            self.xp_max = calculate_xp_for_level(self.character.get("Level", 1) + 1)
            # Ensure quest/plot max are reasonable if loaded value is odd
            if self.quest_max <= 0: self.quest_max = 10000
            if self.plot_max <= 0: self.plot_max = 60000

            print("Game state loaded successfully.")
            self.state_updated.emit("Game Loaded")

        except Exception as e:
            print(f"Error applying loaded state: {e}")
            # Consider resetting state if loading fails critically
            self.reset_state()
            self.game_loaded = False

# END OF FILE: game_logic.py
```

```python
# START OF FILE: character_dialog.py
# File: character_dialog.py
import sys
import random
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QGroupBox, QGridLayout, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFontMetrics
from config_data import RACES, KLASSES, DARK_STYLESHEET, generate_name

class NewCharacterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Progress Quest - New Character")
        self.setMinimumWidth(500)
        # self.setModal(True) # Make it modal

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10) # Add spacing between elements

        # --- Name ---
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        self.name_edit = QLineEdit()
        self.name_edit.setMaxLength(30)
        self.gen_name_button = QPushButton("?")
        self.gen_name_button.setFixedSize(self.gen_name_button.sizeHint().height(), self.gen_name_button.sizeHint().height()) # Square button
        self.gen_name_button.setToolTip("Generate random name")
        self.gen_name_button.clicked.connect(self.generate_random_name)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        name_layout.addWidget(self.gen_name_button)
        self.layout.addLayout(name_layout)

        # --- Race and Class ---
        selection_layout = QHBoxLayout()
        selection_layout.setSpacing(10)

        self.race_group = QGroupBox("Race")
        race_layout = QVBoxLayout()
        self.race_combo = QComboBox()
        self.race_combo.addItems(RACES.keys())
        fm = QFontMetrics(self.race_combo.font())
        max_width = max(fm.horizontalAdvance(race) for race in RACES.keys()) + 40 # Add padding
        self.race_combo.setMinimumWidth(max_width)
        race_layout.addWidget(self.race_combo)
        self.race_group.setLayout(race_layout)
        selection_layout.addWidget(self.race_group, 1) # Add stretch factor

        self.class_group = QGroupBox("Class")
        class_layout = QVBoxLayout()
        self.class_combo = QComboBox()
        self.class_combo.addItems(KLASSES.keys())
        max_width = max(fm.horizontalAdvance(klass) for klass in KLASSES.keys()) + 40 # Add padding
        self.class_combo.setMinimumWidth(max_width)
        class_layout.addWidget(self.class_combo)
        self.class_group.setLayout(class_layout)
        selection_layout.addWidget(self.class_group, 1) # Add stretch factor

        self.layout.addLayout(selection_layout)

        # --- Stats ---
        self.stats_group = QGroupBox("Stats")
        stats_layout = QGridLayout()
        stats_layout.setHorizontalSpacing(15)
        stats_layout.setVerticalSpacing(5)
        self.stat_labels = {}
        self.stat_values = {}
        self.current_stats = {} # Store the actual integer values
        self.stat_order = ["STR", "CON", "DEX", "INT", "WIS", "CHA"]

        for i, stat_name in enumerate(self.stat_order):
            self.stat_labels[stat_name] = QLabel(f"{stat_name}:")
            self.stat_values[stat_name] = QLabel("10")
            self.stat_values[stat_name].setObjectName("StatValueLabel") # For specific styling
            self.stat_values[stat_name].setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.stat_values[stat_name].setMinimumWidth(30)
            stats_layout.addWidget(self.stat_labels[stat_name], i, 0)
            stats_layout.addWidget(self.stat_values[stat_name], i, 1)

        self.total_label = QLabel("Total:")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.total_value = QLabel("60")
        self.total_value.setObjectName("StatValueLabel")
        self.total_value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        stats_layout.addWidget(self.total_label, len(self.stat_order), 0)
        stats_layout.addWidget(self.total_value, len(self.stat_order), 1)

        # Add stretchable space before buttons
        stats_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding), len(self.stat_order) + 1, 0, 1, 2)

        self.roll_button = QPushButton("Roll")
        self.roll_button.setToolTip("Roll new stats (3d6 for each)")
        self.roll_button.clicked.connect(self.roll_stats)
        stats_layout.addWidget(self.roll_button, len(self.stat_order) + 2, 0, 1, 2)

        # Note: Unroll button logic requires storing previous rolls, skipped for simplicity
        # self.unroll_button = QPushButton("Unroll")
        # self.unroll_button.setEnabled(False)
        # self.unroll_button.clicked.connect(self.unroll_stats)
        # stats_layout.addWidget(self.unroll_button, len(self.stat_order) + 3, 0, 1, 2)

        self.stats_group.setLayout(stats_layout)
        selection_layout.addWidget(self.stats_group, 0) # No stretch factor for stats

        # --- Dialog Buttons ---
        button_layout = QHBoxLayout()
        button_layout.addStretch() # Push buttons to the right
        self.ok_button = QPushButton("Sold!")
        self.ok_button.setDefault(True)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(button_layout)

        # --- Initial State ---
        self.generate_random_name()
        self.roll_stats() # Perform initial roll

        # Set focus to name edit initially
        self.name_edit.setFocus()
        self.name_edit.selectAll()

    @Slot()
    def generate_random_name(self):
        self.name_edit.setText(generate_name())

    def roll_d6(self):
        return random.randint(1, 6)

    @Slot()
    def roll_stats(self):
        """Rolls 3d6 for each stat and updates the display."""
        total = 0
        # self.previous_stats = self.current_stats.copy() # Store for unroll if needed
        for stat_name in self.stat_order:
            roll_value = self.roll_d6() + self.roll_d6() + self.roll_d6()
            self.stat_values[stat_name].setText(str(roll_value))
            self.current_stats[stat_name] = roll_value
            total += roll_value
        self.total_value.setText(str(total))

        # Reset style, then apply new style based on total
        self.total_value.setStyleSheet("") # Reset first
        if total >= (63 + 18): self.total_value.setStyleSheet("color: #FF6B6B;") # Bright Red
        elif total > (4 * 18): self.total_value.setStyleSheet("color: #FFD966;") # Yellow
        elif total <= (63 - 18): self.total_value.setStyleSheet("color: #A0A0A0;") # Grey
        elif total < (3 * 18): self.total_value.setStyleSheet("color: #C0C0C0;") # Silver
        # else: no specific style for average rolls

        # self.unroll_button.setEnabled(bool(self.previous_stats)) # Enable if there's something to unroll

    # def unroll_stats(self): # Example if unroll was implemented
    #     if self.previous_stats:
    #         total = 0
    #         self.current_stats = self.previous_stats.copy()
    #         for stat_name in self.stat_order:
    #             val = self.current_stats.get(stat_name, 0)
    #             self.stat_values[stat_name].setText(str(val))
    #             total += val
    #         self.total_value.setText(str(total))
    #         # Reset/apply style for total_value
    #         self.previous_stats = {} # Clear previous roll after unrolling
    #         self.unroll_button.setEnabled(False)


    def get_character_data(self):
        """Returns the selected character data if dialog was accepted."""
        if self.result() == QDialog.DialogCode.Accepted:
            name_text = self.name_edit.text().strip()
            if not name_text: # Ensure name is not empty
                name_text = "Adventurer"
            return {
                "name": name_text,
                "race": self.race_combo.currentText(),
                "class": self.class_combo.currentText(),
                "stats": self.current_stats.copy() # Return a copy
            }
        return None

# Example usage (for testing the dialog standalone)
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLESHEET) # Apply dark theme
    dialog = NewCharacterDialog()
    if dialog.exec():
        data = dialog.get_character_data()
        if data:
            print("Character Created:", data)
        else:
            print("Character data invalid.") # Should not happen if accepted
    else:
        print("Character creation cancelled.")
    sys.exit()
# END OF FILE: character_dialog.py
```

```python
# START OF FILE: main_window.py
# File: main_window.py
import sys
import os
import zlib
import pickle
import time

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QListView, QProgressBar, QStatusBar, QSizePolicy, QSplitter,
    QFileDialog, QMessageBox
)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon, QAction, QFont
from PySide6.QtCore import Qt, QTimer, Slot, QPoint, QSettings # Added QSettings

from config_data import (
    DARK_STYLESHEET, EQUIPMENT_SLOTS, rough_time, int_to_roman,
    plural, definite, indefinite, SAVE_FILE_EXT, BACKUP_FILE_EXT,
    TIMER_INTERVAL_MS
)
from game_logic import GameLogic
from character_dialog import NewCharacterDialog

# Define application and organization names for QSettings
APP_NAME = "ProgressQuestPy"
ORG_NAME = "ZeroSource"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Progress Quest (Zero Source Edition)")
        self.setGeometry(100, 100, 900, 700) # Slightly larger default size

        # Load settings (e.g., window position, last save file)
        self.settings = QSettings(ORG_NAME, APP_NAME)

        self.game_logic = GameLogic()
        self.game_logic.state_updated.connect(self.update_ui)

        self.save_file_path = None # Store path for saving current game

        self.setup_ui()
        self.create_actions()
        self.create_menus()

        # --- Game Timer ---
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.game_logic.tick)

        # --- Restore Geometry and State ---
        self.restore_geometry_and_state()

        # --- Initial Game Load or Creation ---
        # Try loading last opened file first
        last_file = self.settings.value("Files/lastOpened", None)
        loaded = False
        if last_file and os.path.exists(last_file):
             print(f"Attempting to load last opened file: {last_file}")
             loaded = self.load_game_from_path(last_file)

        # If last file load failed or no last file, try finding most recent
        if not loaded:
            most_recent_save = self.find_most_recent_save()
            if most_recent_save:
                print(f"Attempting to load most recent save: {most_recent_save}")
                loaded = self.load_game_from_path(most_recent_save)

        # If still not loaded, prompt for new character
        if not loaded:
            print("No valid save files found or loaded. Starting new character creation.")
            # Delay character creation until after window is shown
            QTimer.singleShot(100, self.create_new_character)
            # self.create_new_character() # This might block showing the window initially

    def setup_ui(self):
        """Create the main UI elements."""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 5, 5, 5) # Add small margin
        main_layout.setSpacing(5) # Reduce spacing

        # --- Top Panels (Splitter for resizing) ---
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Panel 1: Character Sheet
        panel1 = QWidget()
        layout1 = QVBoxLayout(panel1)
        layout1.setContentsMargins(0,0,0,0); layout1.setSpacing(3)
        layout1.addWidget(self._create_label("Character Sheet", header=True))
        self.traits_list = self._create_list_view(["Trait", "Value"])
        layout1.addWidget(self.traits_list, 1) # Add stretch factor
        self.stats_list = self._create_list_view(["Stat", "Value"])
        layout1.addWidget(self.stats_list, 2) # More stretch for stats
        layout1.addWidget(self._create_label("Experience"))
        self.exp_bar = self._create_progress_bar()
        layout1.addWidget(self.exp_bar)
        layout1.addWidget(self._create_label("Spell Book", header=True))
        self.spells_list = self._create_list_view(["Spell", "Level"])
        layout1.addWidget(self.spells_list, 3) # Most stretch for spells
        self.splitter.addWidget(panel1)

        # Panel 2: Equipment & Inventory
        panel2 = QWidget()
        layout2 = QVBoxLayout(panel2)
        layout2.setContentsMargins(0,0,0,0); layout2.setSpacing(3)
        layout2.addWidget(self._create_label("Equipment", header=True))
        self.equips_list = self._create_list_view(["Position", "Equipped"])
        layout2.addWidget(self.equips_list, 1) # Stretch factor
        layout2.addWidget(self._create_label("Inventory", header=True))
        self.inventory_list = self._create_list_view(["Item", "Qty"])
        layout2.addWidget(self.inventory_list, 2) # More stretch for inventory
        layout2.addWidget(self._create_label("Encumbrance"))
        self.encum_bar = self._create_progress_bar()
        layout2.addWidget(self.encum_bar)
        self.splitter.addWidget(panel2)

        # Panel 3: Plot & Quests
        panel3 = QWidget()
        layout3 = QVBoxLayout(panel3)
        layout3.setContentsMargins(0,0,0,0); layout3.setSpacing(3)
        layout3.addWidget(self._create_label("Plot Development", header=True))
        self.plots_list = self._create_list_view(["Act"])
        layout3.addWidget(self.plots_list, 1) # Stretch factor
        self.plot_bar = self._create_progress_bar()
        layout3.addWidget(self.plot_bar)
        layout3.addWidget(self._create_label("Quests", header=True))
        self.quests_list = self._create_list_view(["Quest"])
        layout3.addWidget(self.quests_list, 2) # More stretch for quests
        self.quest_bar = self._create_progress_bar()
        layout3.addWidget(self.quest_bar)
        self.splitter.addWidget(panel3)

        main_layout.addWidget(self.splitter, 1) # Give splitter vertical stretch

        # --- Bottom Bars ---
        bottom_layout = QVBoxLayout()
        bottom_layout.setSpacing(2)
        self.status_bar_label = QLabel("Welcome to Progress Quest!") # Use a label instead of QStatusBar for layout flexibility
        self.status_bar_label.setObjectName("StatusBarLabel") # For styling if needed
        self.status_bar_label.setStyleSheet("font-size: 8pt; color: #c0c0c0; padding: 2px;")
        bottom_layout.addWidget(self.status_bar_label)

        self.task_bar = self._create_progress_bar()
        bottom_layout.addWidget(self.task_bar)
        main_layout.addLayout(bottom_layout) # Add bottom layout below splitter


        # --- Models for ListViews ---
        # Create models with 2 columns for potential future use with QTableView/QTreeView
        # QListView will only display the first column's text by default
        self.traits_model = QStandardItemModel()
        self.traits_model.setHorizontalHeaderLabels(["Trait", "Value"])
        self.stats_model = QStandardItemModel()
        self.stats_model.setHorizontalHeaderLabels(["Stat", "Value"])
        self.equips_model = QStandardItemModel()
        self.equips_model.setHorizontalHeaderLabels(["Position", "Equipped"])
        self.inventory_model = QStandardItemModel()
        self.inventory_model.setHorizontalHeaderLabels(["Item", "Qty"])
        self.spells_model = QStandardItemModel()
        self.spells_model.setHorizontalHeaderLabels(["Spell", "Level"])
        self.plots_model = QStandardItemModel()
        self.plots_model.setHorizontalHeaderLabels(["Act"])
        self.quests_model = QStandardItemModel()
        self.quests_model.setHorizontalHeaderLabels(["Quest"])

        # Assign models to views
        self.traits_list.setModel(self.traits_model)
        self.stats_list.setModel(self.stats_model)
        self.equips_list.setModel(self.equips_model)
        self.inventory_list.setModel(self.inventory_model)
        self.spells_list.setModel(self.spells_model)
        self.plots_list.setModel(self.plots_model)
        self.quests_list.setModel(self.quests_model)

    def create_actions(self):
        """Create actions for menus."""
        self.new_action = QAction("&New Character...", self)
        self.new_action.triggered.connect(self.create_new_character)
        self.load_action = QAction("&Load Game...", self)
        self.load_action.triggered.connect(self.load_game)
        self.save_action = QAction("&Save Game", self)
        self.save_action.triggered.connect(self.save_game)
        self.save_action.setEnabled(False) # Enabled only when game is loaded/created
        self.exit_action = QAction("E&xit", self)
        self.exit_action.triggered.connect(self.close)
        # Add About action later if needed

    def create_menus(self):
        """Create the main menu bar."""
        self.menuBar().setStyleSheet(DARK_STYLESHEET) # Style menubar too
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.load_action)
        file_menu.addAction(self.save_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

    # --- UI Helper Methods ---
    def _create_label(self, text, header=False):
        label = QLabel(text)
        if header:
            label.setObjectName("HeaderLabel") # For specific styling
            # label.setStyleSheet("font-weight: bold; padding-top: 3px; padding-bottom: 1px;") # Inline style
        return label

    def _create_list_view(self, headers):
        view = QListView()
        view.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        view.setSelectionMode(QListView.SelectionMode.NoSelection)
        view.setFocusPolicy(Qt.FocusPolicy.NoFocus) # Prevent list views from stealing focus
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setVerticalScrollMode(QListView.ScrollMode.ScrollPerPixel) # Smoother scrolling
        view.setUniformItemSizes(True) # Performance optimization
        return view

    def _create_progress_bar(self):
        bar = QProgressBar()
        bar.setRange(0, 1000) # Use a high range for smoother updates (e.g., milliseconds)
        bar.setValue(0)
        bar.setTextVisible(True)
        bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bar.setFormat("%p%")
        return bar

    # --- Game Interaction ---
    @Slot()
    def create_new_character(self):
        """Opens the dialog to create a new character."""
        if self.game_logic.game_loaded:
             reply = QMessageBox.warning(self, "New Game",
                                         "Creating a new character will end the current game.\n"
                                         "Do you want to save the current game first?",
                                         QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                                         QMessageBox.StandardButton.Cancel)
             if reply == QMessageBox.StandardButton.Save:
                 if not self.save_game(): # If save fails, cancel new game
                     return
             elif reply == QMessageBox.StandardButton.Cancel:
                 return

        self.timer.stop() # Stop game loop while creating
        self.save_action.setEnabled(False) # Disable save during creation
        dialog = NewCharacterDialog(self)
        if dialog.exec():
            char_data = dialog.get_character_data()
            if char_data:
                self.game_logic.initialize_new_character(
                    char_data["name"], char_data["race"], char_data["class"], char_data["stats"]
                )
                # Determine initial save file path in user's documents or app data dir
                char_name_safe = "".join(c for c in char_data["name"] if c.isalnum() or c in (' ', '_')).rstrip()
                # Use QSettings directory or a standard location
                save_dir = self.settings.fileName().rsplit('/', 1)[0] # Get settings dir
                # Ensure directory exists? QSettings might handle this.
                # A simpler approach for now: save in current working directory
                self.save_file_path = os.path.join(os.getcwd(), f"{char_name_safe}{SAVE_FILE_EXT}")

                self.setWindowTitle(f"Progress Quest - {char_data['name']}")
                self.save_action.setEnabled(True) # Enable saving now
                print(f"Starting new game. Save file will be: {self.save_file_path}")
                # Save immediately after creation
                self.save_game()
                self.settings.setValue("Files/lastOpened", self.save_file_path) # Update last opened
                self.timer.start(TIMER_INTERVAL_MS)
        else:
            print("Character creation cancelled.")
            # If no game was previously loaded, close the app. Otherwise, maybe resume?
            if not self.game_logic.game_loaded:
                self.close() # Close main window if creation is cancelled and no game loaded

    # --- UI Update Slot ---
    @Slot(str)
    def update_ui(self, reason="Tick"):
        """Update all UI elements based on the current game state."""
        if not self.game_logic.game_loaded:
            # print("UI Update skipped: Game not loaded.")
            return # Don't update if no game is active

        state = self.game_logic.get_state()
        char = state["character"]

        # Update lists only if major change occurred? Check reason string.
        is_major_update = reason not in ["Tick"]
        if is_major_update:
             # print(f"Major Update Reason: {reason}")
             pass # Can add specific logic based on reason if needed

        # --- Panel 1: Character Sheet ---
        # Update these less frequently? Maybe only on Level Up or Load?
        if is_major_update or reason == "Tick": # Update Traits/Stats always for now
            self._update_model(self.traits_model, [
                ("Name", char.get("Name", "N/A")),
                ("Race", char.get("Race", "N/A")),
                ("Class", char.get("Class", "N/A")),
                ("Level", str(char.get("Level", 0))),
            ])

            stats_data = []
            stats_dict = char.get("Stats", {})
            for stat_name in ["STR", "CON", "DEX", "INT", "WIS", "CHA"]: # Ensure consistent order
                stats_data.append((stat_name, str(stats_dict.get(stat_name, 0))))
            stats_data.append(("HP Max", str(char.get("HPMax", 0))))
            stats_data.append(("MP Max", str(char.get("MPMax", 0))))
            self._update_model(self.stats_model, stats_data)

        # Update spells only if reason indicates a change?
        if reason in ["Level Up", "Quest Complete", "Game Loaded", "Character Created"] or is_major_update:
            spells_data = sorted(char.get("Spells", {}).items())
            self._update_model(self.spells_model, spells_data)

        self._update_progress_bar(self.exp_bar, state["xp_progress"], state["xp_max"],
                                  f"{int(state['xp_progress']):,}/{int(state['xp_max']):,} XP")

        # --- Panel 2: Equipment & Inventory ---
        if reason in ["Equipment Bought", "Quest Complete", "Act Complete", "Game Loaded", "Character Created"] or is_major_update:
            equip_data = []
            equip_dict = char.get("Equipment", {})
            for slot in EQUIPMENT_SLOTS:
                equip_data.append((slot, equip_dict.get(slot, "")))
            self._update_model(self.equips_model, equip_data)

        if reason in ["Combat End", "Item Sold", "Quest Complete", "Act Complete", "Game Loaded", "Character Created"] or is_major_update:
            inv_data = []
            # Sort inventory: Gold first, then alphabetically
            inv_items = sorted(char.get("Inventory", {}).items(), key=lambda item: (item[0] != "Gold Piece", item[0]))
            for item, qty in inv_items:
                 # Format gold differently in the list view item
                 display_name = f"{qty:,} {plural(item)}" if item == "Gold Piece" else item
                 inv_data.append((display_name, str(f"{qty:,}"))) # Pass qty separately? No, ListView needs 1 col.
            # For ListView, combine into one string per row
            inv_list_data = [(f"{name}: {qty}", "") for name, qty in inv_data] # Kludge for _update_model
            # Adjust gold display specifically
            for i in range(len(inv_list_data)):
                if inv_data[i][0].endswith("Gold Piece"):
                     inv_list_data[i] = (inv_data[i][0], "") # Already formatted qty in name
            self._update_model(self.inventory_model, inv_list_data, use_formatting=False) # Use custom formatting


        self._update_progress_bar(self.encum_bar, state["encumbrance"], state["encumbrance_max"],
                                  f"{state['encumbrance']}/{state['encumbrance_max']} cubits")

        # --- Panel 3: Plot & Quests ---
        if reason in ["Act Complete", "Game Loaded", "Character Created"] or is_major_update:
            plot_data = []
            plot_list = state.get("plot_acts", [])
            for i, act in enumerate(plot_list):
                prefix = "✓ " if i < len(plot_list) - 1 else "► " # Checkmark or Arrow
                plot_data.append((f"{prefix}{act}", "")) # Kludge for _update_model
            self._update_model(self.plots_model, plot_data, use_formatting=False)
            self.plots_list.scrollToBottom()

        time_left_plot = rough_time(max(0, state["plot_max"] - state["plot_progress"]) / 1000)
        self._update_progress_bar(self.plot_bar, state["plot_progress"], state["plot_max"],
                                  f"{state.get('current_act', 'N/A')} ({time_left_plot} left)")

        if reason in ["Quest Complete", "Game Loaded", "Character Created"] or is_major_update:
            quest_data = []
            quest_list = state.get("quests", [])
            for i, (desc, is_complete) in enumerate(quest_list):
                prefix = "✓ " if is_complete else "► "
                quest_data.append((f"{prefix}{desc}", "")) # Kludge for _update_model
            self._update_model(self.quests_model, quest_data, use_formatting=False)
            self.quests_list.scrollToBottom()

        percent_quest = (state["quest_progress"] * 100 / state["quest_max"]) if state["quest_max"] > 0 else 0
        quest_desc_short = state['quest_description'][:60] + '...' if len(state['quest_description']) > 60 else state['quest_description'] # Truncate long quests
        self._update_progress_bar(self.quest_bar, state["quest_progress"], state["quest_max"],
                                  f"{percent_quest:.0f}% - {quest_desc_short}")

        # --- Bottom Bars ---
        self.status_bar_label.setText(state["task_description"] + "...")
        percent_task = (state["task_progress"] * 100 / state["task_max"]) if state["task_max"] > 0 else 0
        self._update_progress_bar(self.task_bar, state["task_progress"], state["task_max"], f"{percent_task:.1f}%") # Show decimal for task


    def _update_model(self, model, data, use_formatting=True):
        """ Efficiently updates a QStandardItemModel. Data is list of (col1_text, col2_text) tuples."""
        model.setRowCount(len(data)) # Adjust row count first
        bold_font = QFont()
        bold_font.setBold(True)
        for row, row_data in enumerate(data):
            # --- Create or get items ---
            item1 = model.item(row, 0)
            if item1 is None:
                item1 = QStandardItem()
                model.setItem(row, 0, item1)
            # item2 = model.item(row, 1) # Only needed for multi-column views
            # if item2 is None:
            #     item2 = QStandardItem()
            #     model.setItem(row, 1, item2)

            # --- Format and set text for ListView (uses only item1) ---
            text1 = str(row_data[0])
            text2 = str(row_data[1]) if len(row_data) > 1 else ""

            if use_formatting:
                # Basic formatting: "Key: Value"
                display_text = f"{text1}: {text2}" if text2 else text1
                item1.setText(display_text)
                # Example: Make stat names bold (requires identifying them)
                # if text1 in ["STR", "CON", "DEX", "INT", "WIS", "CHA", "HP Max", "MP Max", "Level", "Name", "Race", "Class"] + EQUIPMENT_SLOTS:
                #      item1.setFont(bold_font) # This sets font for the *whole item* in QListView

            else: # Use raw text1 if formatting is disabled
                 item1.setText(text1)

            # --- Set text for second column (for QTableView/QTreeView) ---
            # item2.setText(text2)
            # item2.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)


    def _update_progress_bar(self, bar, value, maximum, text_format=None):
        """Safely update a progress bar's value, maximum, and format string."""
        # Ensure maximum is at least 1 to avoid division by zero in format string %p
        safe_maximum = max(1, int(maximum))
        bar.setMaximum(safe_maximum)
        # Clamp value to be within [0, maximum]
        safe_value = max(0, min(int(value), safe_maximum))
        bar.setValue(safe_value)

        if text_format:
            try:
                # Test the format string to catch potential errors if value/max are weird
                _ = text_format.format(value=safe_value, maximum=safe_maximum) # Basic check
                bar.setFormat(text_format)
            except (ValueError, TypeError, KeyError):
                print(f"Warning: Invalid progress bar format string: {text_format}")
                bar.setFormat("%p%") # Fallback to percentage
        else:
            # Default percentage format
            bar.setFormat("%p%")


    # --- Saving and Loading ---
    @Slot()
    def save_game(self):
        """Saves the current game state."""
        if not self.save_file_path:
             # If no path exists (e.g., new game not saved yet), prompt for one
             # This typically shouldn't happen if save is called after creation/load
             print("Warning: No save path set. Cannot save.")
             # Optionally prompt user to select save location here using QFileDialog.getSaveFileName
             return False

        if not self.game_logic.game_loaded:
            print("Cannot save: Game not loaded.")
            return False

        print(f"Attempting to save game to: {self.save_file_path}")
        self.status_bar_label.setText("Saving game...") # Provide feedback
        QApplication.processEvents() # Update UI

        # Create backup
        backup_path = self.save_file_path.replace(SAVE_FILE_EXT, BACKUP_FILE_EXT)
        if os.path.exists(self.save_file_path):
            try:
                if os.path.exists(backup_path):
                    os.remove(backup_path) # Remove old backup
                os.rename(self.save_file_path, backup_path)
                # print(f"Created backup: {backup_path}") # Less verbose
            except OSError as e:
                QMessageBox.warning(self, "Save Warning", f"Could not create backup file:\n{e}")
                # Decide whether to continue saving without backup? Yes.

        # Save current state
        try:
            game_state_data = self.game_logic.get_state_for_saving()
            pickled_data = pickle.dumps(game_state_data)
            compressed_data = zlib.compress(pickled_data, level=zlib.Z_BEST_COMPRESSION) # Use constant

            with open(self.save_file_path, 'wb') as f:
                f.write(compressed_data)

            self.status_bar_label.setText("Game saved.")
            QTimer.singleShot(2000, lambda: self.status_bar_label.setText(self.game_logic.task_description + "...")) # Restore status after 2s
            self.setWindowModified(False) # Indicate saved state if using title bar asterisk
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            QMessageBox.critical(self, "Save Error", f"Could not save game to:\n{self.save_file_path}\n\nError: {e}")
            # Attempt to restore backup if save failed
            if os.path.exists(backup_path):
                try:
                    if os.path.exists(self.save_file_path): # Remove partially written file?
                        os.remove(self.save_file_path)
                    os.rename(backup_path, self.save_file_path)
                    print("Restored backup file after save error.")
                except OSError as be:
                     print(f"Critical Error: Could not restore backup file: {be}")
            return False

    def find_most_recent_save(self):
        """Find the most recent .pq save file in the settings directory or CWD."""
        # Prefer settings directory
        save_dir = os.path.dirname(self.settings.fileName())
        try:
            files_in_dir = [os.path.join(save_dir, f) for f in os.listdir(save_dir) if f.endswith(SAVE_FILE_EXT)]
        except FileNotFoundError:
            files_in_dir = []
            print(f"Settings directory not found: {save_dir}. Checking CWD.")
            save_dir = os.getcwd() # Fallback to current working directory
            try:
                 files_in_dir = [os.path.join(save_dir, f) for f in os.listdir(save_dir) if f.endswith(SAVE_FILE_EXT)]
            except FileNotFoundError:
                print("CWD not found.")
                return None


        if not files_in_dir:
            print(f"No save files found in {save_dir}")
            return None

        # Sort by modification time, newest first
        try:
             files_in_dir.sort(key=lambda f: os.path.getmtime(f), reverse=True)
             return files_in_dir[0]
        except FileNotFoundError: # File might disappear between listing and getmtime
             print("Error accessing file modification times.")
             return None


    def load_game_from_path(self, file_path):
        """Load a game from a specific file path."""
        if not file_path or not os.path.exists(file_path):
            print(f"Error: Save file not found at {file_path}")
            # QMessageBox.warning(self, "Load Error", f"Save file not found:\n{file_path}")
            return False

        print(f"Attempting to load game from: {file_path}")
        self.status_bar_label.setText("Loading game...")
        QApplication.processEvents()

        try:
            with open(file_path, 'rb') as f:
                compressed_data = f.read()

            # Decompress and unpickle
            decompressed_data = zlib.decompress(compressed_data)
            loaded_state = pickle.loads(decompressed_data)

            # Apply the loaded state to the game logic
            self.game_logic.apply_loaded_state(loaded_state) # apply_loaded_state should set game_loaded=True

            if self.game_logic.game_loaded:
                self.save_file_path = file_path # Update save path
                self.setWindowTitle(f"Progress Quest - {self.game_logic.character.get('Name', 'Unknown')}")
                self.update_ui("Game Loaded") # Force immediate UI update with reason
                self.timer.start(TIMER_INTERVAL_MS)
                self.save_action.setEnabled(True) # Enable save menu item
                self.settings.setValue("Files/lastOpened", file_path) # Store as last opened
                self.status_bar_label.setText("Game loaded successfully.")
                QTimer.singleShot(2000, lambda: self.status_bar_label.setText(self.game_logic.task_description + "...")) # Restore status after 2s
                return True
            else:
                 # apply_loaded_state might have failed internally
                 raise ValueError("Game logic failed to apply loaded state.")

        except FileNotFoundError:
            QMessageBox.critical(self, "Load Error", f"Save file not found:\n{file_path}")
        except (zlib.error, pickle.UnpicklingError, EOFError, AttributeError, KeyError, TypeError, ValueError) as e:
            print(f"Error loading game data: Invalid or corrupt file, or data mismatch. {e}")
            QMessageBox.critical(self, "Load Error", f"Could not load game:\nInvalid or corrupt file, or incompatible save format.\n\nError: {e}")
            # Reset to a safe state? Maybe prompt for new character?
            self.game_logic.reset_state()
            self.save_file_path = None
            self.setWindowTitle("Progress Quest (Zero Source Edition)")
            self.update_ui("Load Failed")
            self.save_action.setEnabled(False)
            self.timer.stop()
        except Exception as e:
            print(f"An unexpected error occurred during loading: {e}")
            QMessageBox.critical(self, "Load Error", f"An unexpected error occurred while loading:\n{e}")
            self.game_logic.reset_state() # Reset to be safe
            self.save_action.setEnabled(False)
            self.timer.stop()

        # If we reach here, loading failed
        self.status_bar_label.setText("Failed to load game.")
        return False

    @Slot()
    def load_game(self):
        """Show a file dialog to select and load a game."""
        if self.game_logic.game_loaded:
             reply = QMessageBox.warning(self, "Load Game",
                                         "Loading a game will end the current game.\n"
                                         "Do you want to save the current game first?",
                                         QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                                         QMessageBox.StandardButton.Cancel)
             if reply == QMessageBox.StandardButton.Save:
                 if not self.save_game(): # If save fails, cancel load
                     return False
             elif reply == QMessageBox.StandardButton.Cancel:
                 return False
             # If Discard, continue to load dialog

        # Determine starting directory for dialog
        start_dir = os.path.dirname(self.settings.fileName()) # Settings dir
        if not os.path.isdir(start_dir):
            start_dir = os.getcwd() # Fallback to CWD

        file_path, _ = QFileDialog.getOpenFileName(self, "Load Progress Quest Game", start_dir, f"Progress Quest Files (*{SAVE_FILE_EXT})")
        if file_path:
            self.timer.stop() # Stop current game before loading
            return self.load_game_from_path(file_path)
        else:
            print("Load cancelled.")
            return False

    # --- Settings and Window State ---
    def save_geometry_and_state(self):
        """Save window size, position, and splitter state."""
        self.settings.setValue("Geometry/mainWindowState", self.saveState())
        self.settings.setValue("Geometry/mainWindowSize", self.size())
        self.settings.setValue("Geometry/mainWindowPos", self.pos())
        self.settings.setValue("UI/splitterSizes", self.splitter.saveState())

    def restore_geometry_and_state(self):
        """Restore window size, position, and splitter state."""
        size = self.settings.value("Geometry/mainWindowSize", None)
        pos = self.settings.value("Geometry/mainWindowPos", None)
        state = self.settings.value("Geometry/mainWindowState", None)
        splitter_state = self.settings.value("UI/splitterSizes", None)

        if size: self.resize(size)
        if pos: self.move(pos)
        if state: self.restoreState(state)
        if splitter_state:
             self.splitter.restoreState(splitter_state)
        else: # Set default splitter sizes if no saved state
             self.splitter.setSizes([240, 320, 240]) # Adjust defaults maybe


    # --- Event Overrides ---
    def closeEvent(self, event):
        """Handle window close event: save settings and game."""
        print("Closing application...")
        self.timer.stop()

        # Save game state if a game is loaded
        if self.game_logic.game_loaded and self.save_file_path:
            self.save_game()
            # Don't block closing if save fails, but maybe warn?

        # Save window geometry and settings
        self.save_geometry_and_state()

        print("Exiting.")
        event.accept() # Accept the close event


# --- Main Execution ---
if __name__ == "__main__":
    # Set AppUserModelID for Windows Taskbar grouping/icon
    try:
        from ctypes import windll # Only OS specific functionality
        myappid = f'{ORG_NAME}.{APP_NAME}.1.0' # Arbitrary string
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass # Ignore if not on Windows or ctypes not available

    app = QApplication(sys.argv)
    app.setOrganizationName(ORG_NAME)
    app.setApplicationName(APP_NAME)
    app.setStyleSheet(DARK_STYLESHEET)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
# END OF FILE: main_window.py
```

**To Run This Code:**

1.  **Save the code:** Save each block into its corresponding `.py` file (`config_data.py`, `game_logic.py`, `character_dialog.py`, `main_window.py`) in the same directory.
2.  **Install PySide6:** If you don't have it, open a terminal or command prompt and run:
    ```bash
    pip install PySide6
    ```
3.  **Run the main window:** Execute the main script from your terminal:
    ```bash
    python main_window.py
    ```

**Key Changes and Considerations:**

1.  **Offline Focus:** All code related to `HTTPGet.pas`, `Web.pas`, `Login.pas`, `SelServ.pas`, and the multiplayer aspects within `Main.pas` and `NewGuy.pas` have been removed or commented out in the conceptual porting stage. The `GameLogic` and UI do not attempt any network connections.
2.  **Configuration Data:** `config_data.py` now holds all the static lists (Weapons, Monsters, etc.) translated from the Delphi DFM resources. It also includes the helper functions (like `plural`, `int_to_roman`) and the dark stylesheet.
3.  **Core Logic:** `game_logic.py` contains the `GameLogic` class, encapsulating the character state and the main `tick()` loop logic adapted from `Main.pas`. It uses signals to notify the UI of updates.
4.  **UI Structure:** `main_window.py` builds the UI using PySide6 widgets (`QListView`, `QProgressBar`, `QSplitter`, etc.) mirroring the layout described and seen in `Main.dfm`. `QListView` is used for simplicity, although `QTableView` or `QTreeView` would be technically better for multi-column data; the data is formatted into single strings for `QListView`.
5.  **Character Creation:** `character_dialog.py` implements the character creation screen using `QDialog`. `QComboBox` is used for Race/Class selection instead of `TRadioGroup` for a more compact UI. The multiplayer account fields are omitted.
6.  **Saving/Loading:** Implemented using Python's `pickle` for object serialization and `zlib` for compression, saving to `.pq` files. Basic backup functionality (`.bak`) is included. `QSettings` is added to remember window position and potentially the last loaded file.
7.  **Startup Flow:** The application now attempts to load the last opened save file (stored in settings) or the most recently modified `.pq` file in the settings/app directory or CWD. If none are found or loading fails, it prompts for new character creation.
8.  **Styling:** The `DARK_STYLESHEET` from `config_data.py` is applied to the application for the dark mode theme. Some minor adjustments were made to the stylesheet for better spacing and element sizing.
9.  **Dependencies:** Requires only `PySide6`.