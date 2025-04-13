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
    "Weapon", "Shield", "Helm", "Hauberk", "Brassairts", "Vambraces",
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