import random
import time
import math
import json
import base64
import os
from pathlib import Path
import copy

# --- Constants (Ported from config.js K object) ---

# Using lists of tuples or simple lists based on usage
TRAITS = ["Name", "Race", "Class", "Level"]
PRIME_STATS = ["STR", "CON", "DEX", "INT", "WIS", "CHA"]
STATS = PRIME_STATS + ["HP Max", "MP Max"]
EQUIPS = [
    "Weapon", "Shield", "Helm", "Hauberk", "Brassairts", "Vambraces",
    "Gauntlets", "Gambeson", "Cuisses", "Greaves", "Sollerets"
]

SPELLS = [
  "Slime Finger", "Rabbit Punch", "Hastiness", "Good Move", "Sadness",
  "Seasick", "Shoelaces", "Inoculate", "Cone of Annoyance", "Magnetic Orb",
  "Invisible Hands", "Revolting Cloud", "Aqueous Humor", "Spectral Miasma",
  "Clever Fellow", "Lockjaw", "History Lesson", "Hydrophobia", "Big Sister",
  "Cone of Paste", "Mulligan", "Nestor's Bright Idea", "Holy Batpole",
  "Tumor (Benign)", "Braingate", "Summon a Bitch", "Nonplus",
  "Animate Nightstand", "Eye of the Troglodyte", "Curse Name", "Dropsy",
  "Vitreous Humor", "Roger's Grand Illusion", "Covet", "Black Idaho",
  "Astral Miasma", "Spectral Oyster", "Acrid Hands", "Angioplasty",
  "Grognor's Big Day Off", "Tumor (Malignant)", "Animate Tunic",
  "Ursine Armor", "Holy Roller", "Tonsillectomy", "Curse Family",
  "Infinite Confusion"
]

# Format: (Name, Bonus_String) -> (Name, Bonus_Value)
OFFENSE_ATTRIB = [("Polished", 1), ("Serrated", 1), ("Heavy", 1),
                  ("Pronged", 2), ("Steely", 2), ("Vicious", 3),
                  ("Venomed", 4), ("Stabbity", 4), ("Dancing", 5),
                  ("Invisible", 6), ("Vorpal", 7)]
DEFENSE_ATTRIB = [("Studded", 1), ("Banded", 2), ("Gilded", 2),
                  ("Festooned", 3), ("Holy", 4), ("Cambric", 1),
                  ("Fine", 4), ("Impressive", 5), ("Custom", 3)]

# Format: (Name, Base_Value_String) -> (Name, Base_Value)
SHIELDS = [("Parasol", 0), ("Pie Plate", 1), ("Garbage Can Lid", 2),
           ("Buckler", 3), ("Plexiglass", 4), ("Fender", 4),
           ("Round Shield", 5), ("Carapace", 5), ("Scutum", 6),
           ("Propugner", 6), ("Kite Shield", 7), ("Pavise", 8),
           ("Tower Shield", 9), ("Baroque Shield", 11), ("Aegis", 12),
           ("Magnetic Field", 18)]
ARMORS = [("Lace", 1), ("Macrame", 2), ("Burlap", 3), ("Canvas", 4),
          ("Flannel", 5), ("Chamois", 6), ("Pleathers", 7),
          ("Leathers", 8), ("Bearskin", 9), ("Ringmail", 10),
          ("Scale Mail", 12), ("Chainmail", 14), ("Splint Mail", 15),
          ("Platemail", 16), ("ABS", 17), ("Kevlar", 18),
          ("Titanium", 19), ("Mithril Mail", 20), ("Diamond Mail", 25),
          ("Plasma", 30)]
WEAPONS = [("Stick", 0), ("Broken Bottle", 1), ("Shiv", 1), ("Sprig", 1),
           ("Oxgoad", 1), ("Eelspear", 2), ("Bowie Knife", 2),
           ("Claw Hammer", 2), ("Handpeen", 2), ("Andiron", 3),
           ("Hatchet", 3), ("Tomahawk", 3), ("Hackbarm", 3),
           ("Crowbar", 4), ("Mace", 4), ("Battleadze", 4),
           ("Leafmace", 5), ("Shortsword", 5), ("Longiron", 5),
           ("Poachard", 5), ("Baselard", 5), ("Whinyard", 6),
           ("Blunderbuss", 6), ("Longsword", 6), ("Crankbow", 6),
           ("Blibo", 7), ("Broadsword", 7), ("Kreen", 7),
           ("Warhammer", 7), ("Morning Star", 8), ("Pole-adze", 8),
           ("Spontoon", 8), ("Bastard Sword", 9), ("Peen-arm", 9),
           ("Culverin", 10), ("Lance", 10), ("Halberd", 11),
           ("Poleax", 12), ("Bandyclef", 15)]

SPECIALS = ["Diadem", "Festoon", "Gemstone", "Phial", "Tiara", "Scabbard",
            "Arrow", "Lens", "Lamp", "Hymnal", "Fleece", "Laurel", "Brooch",
            "Gimlet", "Cobble", "Albatross", "Brazier", "Bandolier", "Tome",
            "Garnet", "Amethyst", "Candelabra", "Corset", "Sphere", "Sceptre",
            "Ankh", "Talisman", "Orb", "Gammel", "Ornament", "Brocade",
            "Galoon", "Bijou", "Spangle", "Gimcrack", "Hood", "Vulpeculum"]
ITEM_ATTRIB = ["Golden", "Gilded", "Spectral", "Astral", "Garlanded",
               "Precious", "Crafted", "Dual", "Filigreed", "Cruciate",
               "Arcane", "Blessed", "Reverential", "Lucky", "Enchanted",
               "Gleaming", "Grandiose", "Sacred", "Legendary", "Mythic",
               "Crystalline", "Austere", "Ostentatious", "One True",
               "Proverbial", "Fearsome", "Deadly", "Benevolent", "Unearthly",
               "Magnificent", "Iron", "Ormolu", "Puissant"]
ITEM_OFS = ["Foreboding", "Foreshadowing", "Nervousness", "Happiness",
            "Torpor", "Danger", "Craft", "Silence", "Invisibility",
            "Rapidity", "Pleasure", "Practicality", "Hurting", "Joy",
            "Petulance", "Intrusion", "Chaos", "Suffering", "Extroversion",
            "Frenzy", "Sisu", "Solitude", "Punctuality", "Efficiency",
            "Comfort", "Patience", "Internment", "Incarceration",
            "Misapprehension", "Loyalty", "Envy", "Acrimony", "Worry",
            "Fear", "Awe", "Guile", "Prurience", "Fortune", "Perspicacity",
            "Domination", "Submission", "Fealty", "Hunger", "Despair",
            "Cruelty", "Grob", "Dignard", "Ra", "the Bone", "Diamonique",
            "Electrum", "Hydragyrum"]
BORING_ITEMS = ["nail", "lunchpail", "sock", "I.O.U.", "cookie", "pint",
                "toothpick", "writ", "newspaper", "letter", "plank", "hat",
                "egg", "coin", "needle", "bucket", "ladder", "chicken",
                "twig", "dirtclod", "counterpane", "vest", "teratoma",
                "bunny", "rock", "pole", "carrot", "canoe", "inkwell", "hoe",
                "bandage", "trowel", "towel", "planter box", "anvil",
                "axle", "tuppence", "casket", "nosegay", "trinket",
                "credenza", "writ"]

# Format: (Name, Level_String, Loot) -> (Name, Level, Loot)
MONSTERS = [
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
    ("Bronze Dragon", 9, "medal"), ("Chromatic Dragon", 16, "scale"),
    ("Copper Dragon", 8, "loafer"), ("Gold Dragon", 8, "filling"), ("Green Dragon", 8, "*"),
    ("Platinum Dragon", 21, "*"), ("Red Dragon", 10, "cocktail"), ("Silver Dragon", 10, "*"),
    ("White Dragon", 6, "tooth"), ("Dragon Turtle", 13, "shell"), ("Dryad", 2, "acorn"),
    ("Dwarf", 1, "drawers"), ("Eel", 2, "sashimi"), ("Efreet", 10, "cinder"),
    ("Sand Elemental", 8, "glass"), ("Bacon Elemental", 10, "bit"),
    ("Porn Elemental", 12, "lube"), ("Cheese Elemental", 14, "curd"),
    ("Hair Elemental", 16, "follicle"), ("Swamp Elf", 1, "lilypad"),
    ("Brown Elf", 1, "tusk"), ("Sea Elf", 1, "jerkin"), ("Ettin", 10, "fur"),
    ("Frog", 0, "leg"), ("Violet Fungi", 3, "spore"), ("Gargoyle", 4, "gravel"),
    ("Gelatinous Cube", 4, "jam"), ("Ghast", 4, "vomit"), ("Ghost", 10, "*"),
    ("Ghoul", 2, "muscle"), ("Humidity Giant", 12, "drops"), ("Beef Giant", 11, "steak"),
    ("Quartz Giant", 10, "crystal"), ("Porcelain Giant", 9, "fixture"),
    ("Rice Giant", 8, "grain"), ("Cloud Giant", 12, "condensation"),
    ("Fire Giant", 11, "cigarettes"), ("Frost Giant", 10, "snowman"),
    ("Hill Giant", 8, "corpse"), ("Stone Giant", 9, "hatchling"),
    ("Storm Giant", 15, "barometer"), ("Mini Giant", 4, "pompadour"),
    ("Gnoll", 2, "collar"), ("Gnome", 1, "hat"), ("Goblin", 1, "ear"),
    ("Grid Bug", 1, "carapace"), ("Jellyrock", 9, "seedling"), ("Beer Golem", 15, "foam"),
    ("Oxygen Golem", 17, "platelet"), ("Cardboard Golem", 14, "recycling"),
    ("Rubber Golem", 16, "ball"), ("Leather Golem", 15, "fob"), ("Gorgon", 8, "testicle"),
    ("Gray Ooze", 3, "gravy"), ("Green Slime", 2, "sample"), ("Griffon", 7, "nest"),
    ("Banshee", 7, "larynx"), ("Harpy", 3, "mascara"), ("Hell Hound", 5, "tongue"),
    ("Hippocampus", 4, "mane"), ("Hippogriff", 3, "egg"), ("Hobgoblin", 1, "patella"),
    ("Homunculus", 2, "fluid"), ("Hydra", 8, "gyrum"), ("Imp", 2, "tail"),
    ("Invisible Stalker", 8, "*"), ("Iron Peasant", 3, "chaff"), ("Jumpskin", 3, "shin"),
    ("Kobold", 1, "penis"), ("Leprechaun", 1, "wallet"), ("Leucrotta", 6, "hoof"),
    ("Lich", 11, "crown"), ("Lizard Man", 2, "tail"), ("Lurker", 10, "sac"),
    ("Manticore", 6, "spike"), ("Mastodon", 12, "tusk"), ("Medusa", 6, "eye"),
    ("Multicell", 2, "dendrite"), ("Pirate", 1, "booty"), ("Berserker", 1, "shirt"),
    ("Caveman", 2, "club"), ("Dervish", 1, "robe"), ("Merman", 1, "trident"),
    ("Mermaid", 1, "gills"), ("Mimic", 9, "hinge"), ("Mind Flayer", 8, "tentacle"),
    ("Minotaur", 6, "map"), ("Yellow Mold", 1, "spore"), ("Morkoth", 7, "teeth"),
    ("Mummy", 6, "gauze"), ("Naga", 9, "rattle"), ("Nebbish", 1, "belly"),
    ("Neo-Otyugh", 11, "organ "), ("Nixie", 1, "webbing"), ("Nymph", 3, "hanky"),
    ("Ochre Jelly", 6, "nucleus"), ("Octopus", 2, "beak"), ("Ogre", 4, "talon"),
    ("Ogre Mage", 5, "apparel"), ("Orc", 1, "snout"), ("Otyugh", 7, "organ"),
    ("Owlbear", 5, "feather"), ("Pegasus", 4, "aileron"), ("Peryton", 4, "antler"),
    ("Piercer", 3, "tip"), ("Pixie", 1, "dust"), ("Man-o-war", 3, "tentacle"),
    ("Purple Worm", 15, "dung"), ("Quasit", 3, "tail"), ("Rakshasa", 7, "pajamas"),
    ("Rat", 0, "tail"), ("Remorhaz", 11, "protrusion"), ("Roc", 18, "wing"),
    ("Roper", 11, "twine"), ("Rot Grub", 1, "eggsac"), ("Rust Monster", 5, "shavings"),
    ("Satyr", 5, "hoof"), ("Sea Hag", 3, "wart"), ("Silkie", 3, "fur"),
    ("Shadow", 3, "silhouette"), ("Shambling Mound", 10, "mulch"), ("Shedu", 9, "hoof"),
    ("Shrieker", 3, "stalk"), ("Skeleton", 1, "clavicle"), ("Spectre", 7, "vestige"),
    ("Sphinx", 10, "paw"), ("Spider", 0, "web"), ("Sprite", 1, "can"),
    ("Stirge", 1, "proboscis"), ("Stun Bear", 5, "tooth"), ("Stun Worm", 2, "trode"),
    ("Su-monster", 5, "tail"), ("Sylph", 3, "thigh"), ("Titan", 20, "sandal"),
    ("Trapper", 12, "shag"), ("Treant", 10, "acorn"), ("Triton", 3, "scale"),
    ("Troglodyte", 2, "tail"), ("Troll", 6, "hide"), ("Umber Hulk", 8, "claw"),
    ("Unicorn", 4, "blood"), ("Vampire", 8, "pancreas"), ("Wight", 4, "lung"),
    ("Will-o'-the-Wisp", 9, "wisp"), ("Wraith", 5, "finger"), ("Wyvern", 7, "wing"),
    ("Xorn", 7, "jaw"), ("Yeti", 4, "fur"), ("Zombie", 2, "forehead"),
    ("Wasp", 0, "stinger"), ("Rat", 1, "tail"), ("Bunny", 0, "ear"),
    ("Moth", 0, "dust"), ("Beagle", 0, "collar"), ("Midge", 0, "corpse"),
    ("Ostrich", 1, "beak"), ("Billy Goat", 1, "beard"), ("Bat", 1, "wing"),
    ("Koala", 2, "heart"), ("Wolf", 2, "paw"), ("Whippet", 2, "collar"),
    ("Uruk", 2, "boot"), ("Poroid", 4, "node"), ("Moakum", 8, "frenum"),
    ("Fly", 0, "*"), ("Hogbird", 3, "curl"), ("Wolog", 4, "lemma")
]

# Format: (Modifier_String, Level_Diff) -> (Modifier_Prefix, Modifier_Suffix, Level_Diff)
MON_MODS = [
    ("fœtal *", -4), ("dying *", -4), ("crippled *", -3), ("baby *", -3),
    ("adolescent *", -2), ("very sick *", -2), ("lesser *", -1),
    ("undernourished *", -1), ("greater *", 1), ("* Elder", 1),
    ("war *", 2), ("Battle-*", 2), ("Were-*", 3), ("undead *", 3),
    ("giant *", 4), ("* Rex", 4)
]

OFFENSE_BAD = [("Dull", -2), ("Tarnished", -1), ("Rusty", -3), ("Padded", -5),
               ("Bent", -4), ("Mini", -4), ("Rubber", -6), ("Nerf", -7),
               ("Unbalanced", -2)]
DEFENSE_BAD = [("Holey", -1), ("Patched", -1), ("Threadbare", -2), ("Faded", -1),
               ("Rusty", -3), ("Motheaten", -3), ("Mildewed", -2), ("Torn", -3),
               ("Dented", -3), ("Cursed", -5), ("Plastic", -4), ("Cracked", -4),
               ("Warped", -3), ("Corroded", -3)]

# Format: (Name, Bonus_Stats_String) -> (Name, list[Bonus_Stats])
RACES = [
    ("Half Orc", ["HP Max"]), ("Half Man", ["CHA"]), ("Half Halfling", ["DEX"]),
    ("Double Hobbit", ["STR"]), ("Hob-Hobbit", ["DEX", "CON"]), ("Low Elf", ["CON"]),
    ("Dung Elf", ["WIS"]), ("Talking Pony", ["MP Max", "INT"]), ("Gyrognome", ["DEX"]),
    ("Lesser Dwarf", ["CON"]), ("Crested Dwarf", ["CHA"]), ("Eel Man", ["DEX"]),
    ("Panda Man", ["CON", "STR"]), ("Trans-Kobold", ["WIS"]),
    ("Enchanted Motorcycle", ["MP Max"]), ("Will o' the Wisp", ["WIS"]),
    ("Battle-Finch", ["DEX", "INT"]), ("Double Wookiee", ["STR"]),
    ("Skraeling", ["WIS"]), ("Demicanadian", ["CON"]),
    ("Land Squid", ["STR", "HP Max"])
]
KLASSES = [
    ("Ur-Paladin", ["WIS", "CON"]), ("Voodoo Princess", ["INT", "CHA"]),
    ("Robot Monk", ["STR"]), ("Mu-Fu Monk", ["DEX"]),
    ("Mage Illusioner", ["INT", "MP Max"]), ("Shiv-Knight", ["DEX"]),
    ("Inner Mason", ["CON"]), ("Fighter/Organist", ["CHA", "STR"]),
    ("Puma Burgular", ["DEX"]), ("Runeloremaster", ["WIS"]),
    ("Hunter Strangler", ["DEX", "INT"]), ("Battle-Felon", ["STR"]),
    ("Tickle-Mimic", ["WIS", "INT"]), ("Slow Poisoner", ["CON"]),
    ("Bastard Lunatic", ["CON"]), ("Lowling", ["WIS"]), ("Birdrider", ["WIS"]),
    ("Vermineer", ["INT"])
]
TITLES = ["Mr.", "Mrs.", "Sir", "Sgt.", "Ms.", "Captain", "Chief", "Admiral", "Saint"]
IMPRESSIVE_TITLES = ["King", "Queen", "Lord", "Lady", "Viceroy", "Mayor", "Prince",
                     "Princess", "Chief", "Boss", "Archbishop", "Chancellor",
                     "Baroness", "Inquistor"]

# Parts for name generation
K_PARTS = [
    'br|cr|dr|fr|gr|j|kr|l|m|n|pr||||r|sh|tr|v|wh|x|y|z'.split('|'),
    'a|a|e|e|i|i|o|o|u|u|ae|ie|oo|ou'.split('|'),
    'b|ck|d|g|k|m|n|p|t|v|x|z'.split('|')
]

# Save game directory
SAVE_DIR = Path("./savegame")
SAVE_DIR.mkdir(exist_ok=True)

# Base save game structure (derived from savegame_scheme.json)
# Use deepcopy to avoid modifying the original template
DEFAULT_SAVE_SCHEMA = {
  "Traits": {"Name": "", "Race": "", "Class": "", "Level": 0},
  "dna": [0.0, 0.0, 0.0, 0], # Seed state from Alea
  "seed": [0.0, 0.0, 0.0, 0], # Current PRNG state
  "birthday": "",
  "birthstamp": 0,
  "Stats": {
    "seed": [0.0, 0.0, 0.0, 0], # Stat roll seed state
    "STR": 0, "CON": 0, "DEX": 0, "INT": 0, "WIS": 0, "CHA": 0,
    "HP Max": 0, "MP Max": 0,
    "best": "" # Best stat at creation time
  },
  "beststat": "", # Best current stat string (e.g., "STR 15")
  "task": "", # Internal task identifier (e.g., "kill|Goblin|1|ear")
  "tasks": 0, # Number of tasks completed
  "elapsed": 0, # Total time elapsed in seconds (from completed tasks)
  "bestequip": "", # Best equipment string
  "Equips": { k: "" for k in EQUIPS },
  "Inventory": [['Gold', 0]], # List of [item_name, quantity]
  "Spells": [], # List of [spell_name, level_roman]
  "act": 0,
  "bestplot": "", # Current act/plot string
  "Quests": [], # List of quest descriptions
  "questmonster": "", # Name|Level|Loot string for current quest monster target
  "questmonsterindex": -1, # Index in MONSTERS list for quest target
  "kill": "", # User-visible current action string
  "ExpBar": {"position": 0.0, "max": 0, "percent": 0, "remaining": 0, "time": "", "hint": ""},
  "EncumBar": {"position": 0, "max": 0, "percent": 0, "remaining": 0, "time": "", "hint": ""},
  "PlotBar": {"position": 0.0, "max": 0, "percent": 0, "remaining": 0, "time": "", "hint": ""},
  "QuestBar": {"position": 0.0, "max": 0, "percent": 0, "remaining": 0, "time": "", "hint": ""},
  "TaskBar": {"position": 0.0, "max": 0, "percent": 0, "remaining": 0, "time": "", "hint": ""},
  "queue": [], # List of future tasks ["task|duration|description"]
  "date": "", # Last saved date string
  "stamp": 0, # Last saved timestamp
  "saveName": "", # Character name, potentially with realm (unused here)
  "bestspell": "", # Best spell string (e.g., "Slime Finger I")
  "bestquest": "", # Current quest description string
  "log": {} # Optional logging {timestamp: message}
}

# --- PRNG (Simplified Alea-like state management) ---
_alea_state = [0.0, 0.0, 0.0, 0.0] # s0, s1, s2, c

def _mash(data):
    n = 0xefc8249d
    data = str(data)
    for char in data:
        n += ord(char)
        h = 0.02519603282416938 * n
        n = int(h) # Simulate >>> 0
        h -= n
        h *= n
        n = int(h) # Simulate >>> 0
        h -= n
        n += h * 0x100000000 # Simulate 2^32
    return (int(n) & 0xFFFFFFFF) * 2.3283064365386963e-10 # Simulate (n >>> 0) * 2^-32

def seed_random(seed_args=None):
    """Initialize or set the PRNG state."""
    global _alea_state
    s0, s1, s2 = 0.0, 0.0, 0.0
    c = 1.0

    if seed_args is None:
        seed_args = [time.time()]

    mash = _mash
    s0 = mash(' ')
    s1 = mash(' ')
    s2 = mash(' ')

    for arg in seed_args:
        s0 -= mash(arg)
        s0 += 1.0 if s0 < 0 else 0.0
        s1 -= mash(arg)
        s1 += 1.0 if s1 < 0 else 0.0
        s2 -= mash(arg)
        s2 += 1.0 if s2 < 0 else 0.0

    _alea_state = [s0, s1, s2, c]
    return _alea_state # Return the new state

def get_random_state():
    """Get the current PRNG state."""
    return _alea_state[:] # Return a copy

def set_random_state(state):
    """Set the PRNG state."""
    global _alea_state
    if state and len(state) == 4:
        _alea_state = state[:] # Use a copy

def random_alea():
    """Generate a random float [0, 1) using Alea state."""
    global _alea_state
    s0, s1, s2, c = _alea_state
    t = 2091639.0 * s0 + c * 2.3283064365386963e-10 # 2^-32
    s0 = s1
    s1 = s2
    s2 = t - math.floor(t)
    c = math.floor(t)
    _alea_state = [s0, s1, s2, c]
    return s2

def Random(n):
    """Return a random integer 0 <= x < n."""
    if n <= 0: return 0
    return math.floor(random_alea() * n)

def Pick(a):
    """Pick a random element from list a."""
    if not a: return None
    return a[Random(len(a))]

def RandomLow(below):
    """Return the minimum of two random numbers below 'below'."""
    return min(Random(below), Random(below))

def PickLow(s):
    """Pick an element from list s using RandomLow index."""
    if not s: return None
    return s[RandomLow(len(s))]

def RandSign():
  """Return 1 or -1 randomly."""
  return Random(2) * 2 - 1

# Initialize PRNG on module load
seed_random()

# --- Helper Functions ---

def div_floor(dividend, divisor):
    """Integer division that floors the result (like JS `a / b | 0`)."""
    if divisor == 0: return 0 # Or raise error
    res = dividend / divisor
    return math.floor(res) if res >= 0 else math.ceil(res) # Correct for negative numbers too

def level_up_time(level):
    """Calculate time in seconds to reach the next level."""
    # 20 minutes for level 1, exponential increase after that
    return round((20 + math.pow(1.15, level)) * 60)

def plural(s):
    """Return the plural form of a noun."""
    if not s: return ""
    s_lower = s.lower()
    if s_lower.endswith('y'):
        return s[:-1] + 'ies'
    elif s_lower.endswith('us'):
        return s[:-2] + 'i'
    elif s_lower.endswith(('ch', 'x', 's', 'sh')):
        return s + 'es'
    elif s_lower.endswith('f'):
        return s[:-1] + 'ves'
    elif s_lower.endswith('fe'):
        return s[:-2] + 'ves'
    elif s_lower.endswith('man'):
        return s[:-2] + 'en'
    else:
        return s + 's'

def indefinite(s, qty):
    """Return indefinite article ('a'/'an') + noun, or quantity + plural noun."""
    if qty == 1:
        if s and s[0].lower() in 'aeiou':
            return 'an ' + s
        else:
            return 'a ' + s
    else:
        return str(qty) + ' ' + plural(s)

def definite(s, qty):
    """Return 'the' + noun or plural noun."""
    if qty > 1:
        s = plural(s)
    return 'the ' + s

def generate_name():
    """Generate a random fantasy name."""
    result = ''
    for i in range(6): # 0 to 5
        result += Pick(K_PARTS[i % 3])
    return result.capitalize()

def str_to_int_def(s, default=0):
    """Convert string to int, return default on failure."""
    try:
        return int(s)
    except (ValueError, TypeError):
        return default

def _apply_prefix(prefixes, index, text, sep=' '):
    """Helper to apply prefixes based on modifier value."""
    # JS logic was `prefix(..., Abs(m), ...)` and `prefix(..., 6 - Abs(m), ...)`
    # Let's assume 'index' is the direct modifier value (-5 to +5 etc)
    # We need to map this index to the correct prefix list index
    idx = abs(index) -1 # Map 1..5 to 0..4
    if idx < 0 or idx >= len(prefixes):
        return text
    return prefixes[idx] + sep + text

def sick_prefix(modifier, text):
    """Apply sickness prefix based on negative modifier."""
    # Original JS: m = 6 - Abs(m); prefix(['dead',...], m, s);
    # If modifier is -1, m=5 ('undernourished'). If -5, m=1 ('dead')
    prefixes = ['dead', 'comatose', 'crippled', 'sick', 'undernourished']
    idx = 5 - abs(modifier) # Map -1..-5 to 4..0
    if idx < 0 or idx >= len(prefixes): return text
    return prefixes[idx] + ' ' + text

def young_prefix(modifier, text):
    """Apply youth prefix based on negative modifier."""
    # Original JS: m = 6 - Abs(m); prefix(['foetal',...], m, s);
    prefixes = ['foetal', 'baby', 'preadolescent', 'teenage', 'underage']
    idx = 5 - abs(modifier) # Map -1..-5 to 4..0
    if idx < 0 or idx >= len(prefixes): return text
    return prefixes[idx] + ' ' + text

def big_prefix(modifier, text):
    """Apply size prefix based on positive modifier."""
    prefixes = ['greater', 'massive', 'enormous', 'giant', 'titanic']
    idx = abs(modifier) -1
    if idx < 0 or idx >= len(prefixes): return text
    return prefixes[idx] + ' ' + text

def special_prefix(modifier, text):
    """Apply special prefix based on positive modifier."""
    prefixes_multi = ['veteran', 'cursed', 'warrior', 'undead', 'demon']
    prefixes_single = ['Battle-', 'cursed ', 'Were-', 'undead ', 'demon ']
    idx = abs(modifier) -1
    if idx < 0 or idx >= len(prefixes_multi): return text

    if ' ' in text: # Multi-word name
        return prefixes_multi[idx] + ' ' + text
    else: # Single word name
        return prefixes_single[idx] + text

def rough_time(seconds):
    """Convert seconds to human-readable duration string."""
    if seconds < 120: return f"{div_floor(seconds, 1)} seconds"
    if seconds < 60 * 120: return f"{div_floor(seconds, 60)} minutes"
    if seconds < 60 * 60 * 48: return f"{div_floor(seconds, 3600)} hours"
    if seconds < 60 * 60 * 24 * 60: return f"{div_floor(seconds, 3600 * 24)} days"
    if seconds < 60 * 60 * 24 * 30 * 24: return f"{div_floor(seconds, 3600 * 24 * 30)} months"
    return f"{div_floor(seconds, 3600 * 24 * 365)} years" # Approx year

_ROMAN_MAP = { 1: 'I', 4: 'IV', 5: 'V', 9: 'IX', 10: 'X', 40: 'XL', 50: 'L',
               90: 'XC', 100: 'C', 400: 'XD', 500: 'D', 900: 'CM', 1000: 'M',
               4000: 'MA', 5000: 'A', 9000: 'MT', 10000: 'T'} # T, A, MT added from JS
_ROMAN_KEYS = sorted(_ROMAN_MAP.keys(), reverse=True)
_ARABIC_MAP = {v: k for k, v in _ROMAN_MAP.items()}
# Need to handle multi-char Roman numerals first for parsing
_ARABIC_KEYS = sorted(_ARABIC_MAP.keys(), key=len, reverse=True)

def to_roman(n):
    """Convert integer to Roman numeral string."""
    if not isinstance(n, int) or n == 0: return "N"
    if n < 0: return "-" + to_roman(abs(n))

    result = ""
    num = n
    for val in _ROMAN_KEYS:
        while num >= val:
            result += _ROMAN_MAP[val]
            num -= val
    return result

def to_arabic(s):
    """Convert Roman numeral string to integer."""
    if not s or s == 'N': return 0
    s = s.upper()
    result = 0
    i = 0
    while i < len(s):
        found = False
        for key in _ARABIC_KEYS: # Check longer numerals first (e.g., 'CM' before 'C')
            if s[i:].startswith(key):
                result += _ARABIC_MAP[key]
                i += len(key)
                found = True
                break
        if not found: # Should not happen with valid Roman numerals
            # Fallback for single chars if multi-char check fails somehow
            if s[i] in _ARABIC_MAP:
                 result += _ARABIC_MAP[s[i]]
                 i += 1
            else:
                 i += 1 # Skip invalid char
                 print(f"Warning: Invalid Roman numeral character skipped: {s[i]}")

    return result


# --- Game State Manipulation ---

def _log_event(game_state, message):
    """Add an event to the game log."""
    if "log" not in game_state:
        game_state["log"] = {}
    game_state["log"][time.time()] = message

def get_trait(game_state, trait_name):
    """Get a specific trait value."""
    return game_state.get("Traits", {}).get(trait_name, "")

def get_trait_i(game_state, trait_name):
    """Get a specific trait value as integer."""
    return str_to_int_def(get_trait(game_state, trait_name))

def get_stat(game_state, stat_name):
    """Get a specific stat value."""
    return game_state.get("Stats", {}).get(stat_name, 0)

def get_equip(game_state, equip_slot):
    """Get equipment in a specific slot."""
    return game_state.get("Equips", {}).get(equip_slot, "")

def get_inventory_item_qty(game_state, item_name):
    """Get quantity of a specific item in inventory."""
    inventory = game_state.get("Inventory", [])
    for item, qty in inventory:
        if item == item_name:
            return qty
    return 0

def get_spell_level(game_state, spell_name):
    """Get the Roman numeral level of a specific spell."""
    spells = game_state.get("Spells", [])
    for name, level_roman in spells:
        if name == spell_name:
            return level_roman
    return ""

def get_spell_level_i(game_state, spell_name):
    """Get the integer level of a specific spell."""
    return to_arabic(get_spell_level(game_state, spell_name))


def update_trait(game_state, trait_name, value):
    """Update a trait value."""
    if "Traits" not in game_state: game_state["Traits"] = {}
    game_state["Traits"][trait_name] = value

def update_stat(game_state, stat_name, value):
    """Update a stat value."""
    if "Stats" not in game_state: game_state["Stats"] = {}
    game_state["Stats"][stat_name] = value
    if stat_name == 'STR': # Update encumbrance max if STR changes
        update_bar_max(game_state, "EncumBar", 10 + value)

def add_stat(game_state, stat_name, amount):
    """Add an amount to a stat."""
    current = get_stat(game_state, stat_name)
    update_stat(game_state, stat_name, current + amount)
    # Log gain/loss (optional)
    verb = "Gained" if amount > 0 else "Lost"
    #_log_event(game_state, f"{verb} {abs(amount)} {stat_name}")


def update_equip(game_state, equip_slot, item_name):
    """Update equipment in a slot."""
    if "Equips" not in game_state: game_state["Equips"] = {}
    game_state["Equips"][equip_slot] = item_name
    game_state["bestequip"] = find_best_equip_string(game_state) # Recalculate best equip

def find_inventory_item_index(game_state, item_name):
    """Find the index of an item in the inventory list."""
    inventory = game_state.get("Inventory", [])
    for i, (name, qty) in enumerate(inventory):
        if name == item_name:
            return i
    return -1

def add_inventory(game_state, item_name, quantity):
    """Add or remove quantity of an item from inventory. Updates encumbrance."""
    if not quantity: return # No change
    if "Inventory" not in game_state: game_state["Inventory"] = [['Gold', 0]]

    inventory = game_state["Inventory"]
    index = find_inventory_item_index(game_state, item_name)

    current_qty = 0
    if index != -1:
        current_qty = inventory[index][1]
        new_qty = current_qty + quantity
        if new_qty > 0:
            inventory[index][1] = new_qty
        else:
            # Remove item if quantity drops to 0 or less
            del inventory[index]
    elif quantity > 0:
        # Add new item if it doesn't exist and quantity is positive
        inventory.append([item_name, quantity])

    # Log gain/loss
    verb = "Gained" if quantity > 0 else "Lost"
    log_item_name = "gold piece" if item_name == "Gold" else item_name
    if item_name == "Gold":
        verb = "Got paid" if quantity > 0 else "Spent"
    _log_event(game_state, f"{verb} {indefinite(log_item_name, abs(quantity))}")

    # Update encumbrance
    update_encumbrance(game_state)


def update_encumbrance(game_state):
    """Recalculate and update encumbrance bar based on inventory."""
    inventory = game_state.get("Inventory", [])
    cubits = 0
    # Skip Gold for encumbrance calculation
    for item_name, qty in inventory:
        if item_name != "Gold":
            cubits += qty
    # Encumbrance max depends on STR
    enc_max = 10 + get_stat(game_state, 'STR')
    update_bar_max(game_state, "EncumBar", enc_max)
    set_bar_position(game_state, "EncumBar", cubits)


def add_spell(game_state, spell_name, level_increment=1):
    """Add a spell or increase its level."""
    if "Spells" not in game_state: game_state["Spells"] = []
    spells = game_state["Spells"]
    found = False
    for i, (name, level_roman) in enumerate(spells):
        if name == spell_name:
            current_level = to_arabic(level_roman)
            new_level = current_level + level_increment
            spells[i][1] = to_roman(new_level)
            found = True
            break
    if not found:
        spells.append([spell_name, to_roman(level_increment)])

    spells.sort(key=lambda x: x[0]) # Keep spells sorted alphabetically
    game_state["bestspell"] = find_best_spell_string(game_state) # Recalculate

    # Log
    _log_event(game_state, f"Learned/Improved {spell_name} to level {get_spell_level(game_state, spell_name)}")


def find_best_equip_string(game_state):
    """Find the 'best' equipment string (simple heuristic: longest name maybe?)."""
    # The JS version just stored the *last* generated equip name. Let's mimic that.
    # The `update_equip` function will call this, so we return the last set non-empty equip.
    # We'll rely on the `bestequip` field updated during `win_equip`.
    return game_state.get("bestequip", "Sharp Rock")


def find_best_spell_string(game_state):
    """Find the 'best' spell string (JS heuristic: (index+1)*level)."""
    spells = game_state.get("Spells", [])
    if not spells: return ""

    best_score = -1
    best_index = -1
    flat = 1 # Flattening constant from JS

    # Ensure spells are sorted alphabetically first, as JS likely iterated over the displayed list
    spells.sort(key=lambda x: x[0])

    for i, (name, level_roman) in enumerate(spells):
        level = to_arabic(level_roman)
        score = (i + flat) * level
        if score > best_score:
            best_score = score
            best_index = i

    if best_index != -1:
        best_name, best_level_roman = spells[best_index]
        return f"{best_name} {best_level_roman}"
    return ""

def find_best_stat_string(game_state):
    """Find the highest prime stat and return its string representation."""
    best_val = -1
    best_stat_name = ""
    for stat_name in PRIME_STATS:
        val = get_stat(game_state, stat_name)
        if val > best_val:
            best_val = val
            best_stat_name = stat_name
    if best_stat_name:
        return f"{best_stat_name} {best_val}"
    return ""


# --- Progress Bar Handling ---

def update_bar_max(game_state, bar_id, new_max):
    """Set the maximum value for a progress bar."""
    bar_id = bar_id.replace("Bar", "") # Normalize ID
    bar_key = f"{bar_id}Bar"
    if bar_key not in game_state: game_state[bar_key] = {}
    game_state[bar_key]['max'] = new_max
    # Re-calculate dependent fields after changing max
    set_bar_position(game_state, bar_key, game_state[bar_key].get('position', 0))

def set_bar_position(game_state, bar_id, new_position):
    """Set the current position for a progress bar and update related fields."""
    bar_id = bar_id.replace("Bar", "") # Normalize ID
    bar_key = f"{bar_id}Bar"
    if bar_key not in game_state: game_state[bar_key] = {}

    bar = game_state[bar_key]
    bar_max = bar.get('max', 1) # Avoid division by zero
    if bar_max <= 0: bar_max = 1

    bar['position'] = min(new_position, bar_max)

    # Update calculated fields for UI
    bar['percent'] = int(div_floor(100 * bar['position'], bar_max))
    remaining_val = bar_max - bar['position']

    if bar_id in ["Plot", "Exp"]: # Time-based bars
        bar['remaining'] = math.floor(remaining_val)
        bar['time'] = rough_time(bar['remaining'])
    elif bar_id == "Quest":
        bar['remaining'] = math.floor(remaining_val) # Or just use percent?
        bar['time'] = "" # Quests don't show time
    elif bar_id == "Encum":
         bar['remaining'] = math.floor(remaining_val)
         bar['time'] = "" # Encumbrance doesn't show time
    else: # TaskBar just uses percent
        bar['remaining'] = 0
        bar['time'] = ""


    # Update hint string based on bar type (matches JS templates)
    if bar_id == "Exp":
        bar['hint'] = f"{bar['remaining']} XP needed for next level"
    elif bar_id == "Encum":
        bar['hint'] = f"{int(bar['position'])}/{int(bar_max)} cubits"
    elif bar_id == "Plot":
        bar['hint'] = f"{bar['time']} remaining"
    elif bar_id == "Quest":
        bar['hint'] = f"{bar['percent']}% complete"
    elif bar_id == "Task":
         bar['hint'] = f"{bar['percent']}%" # Taskbar just shows percentage in JS hint too
    else:
        bar['hint'] = ""

def increment_bar(game_state, bar_id, increment):
    """Increment a progress bar's position."""
    bar_key = f"{bar_id}Bar" if not bar_id.endswith("Bar") else bar_id
    current_pos = game_state.get(bar_key, {}).get('position', 0)
    set_bar_position(game_state, bar_key, current_pos + increment)

def is_bar_done(game_state, bar_id):
    """Check if a progress bar is full."""
    bar_key = f"{bar_id}Bar" if not bar_id.endswith("Bar") else bar_id
    bar = game_state.get(bar_key, {})
    return bar.get('position', 0) >= bar.get('max', 1)


# --- Task Queue ---

def add_task_to_queue(game_state, task_string):
    """Add a task string (e.g., 'task|duration|description') to the queue."""
    if "queue" not in game_state: game_state["queue"] = []
    game_state["queue"].append(task_string)

def dequeue_task(game_state):
    """Get and remove the next task from the queue. Returns None if empty."""
    if game_state.get("queue"):
        return game_state["queue"].pop(0)
    return None

def set_current_task(game_state, description, duration_msec, internal_task_id=""):
    """Set the current task, resetting the TaskBar."""
    game_state["kill"] = description + "..."
    game_state["task"] = internal_task_id # Store the internal ID for task completion logic
    _log_event(game_state, game_state["kill"])
    update_bar_max(game_state, "TaskBar", duration_msec)
    set_bar_position(game_state, "TaskBar", 0)

# --- Item/Monster Generation ---

def boring_item():
    return Pick(BORING_ITEMS)

def interesting_item():
    return Pick(ITEM_ATTRIB) + ' ' + Pick(SPECIALS)

def special_item():
    return interesting_item() + ' of ' + Pick(ITEM_OFS)

def win_item(game_state):
    """Adds a random item to inventory."""
    inventory = game_state.get("Inventory", [])
    # JS logic: if inv length > max(250, rand(999)), pick existing, else new special
    threshold = max(250, Random(1000)) # JS rand(999) is 0-998, so use 1000
    if len(inventory) > threshold and len(inventory) > 1:
        # Pick existing non-gold item name
        non_gold_items = [item[0] for item in inventory if item[0] != "Gold"]
        if non_gold_items:
            item_name = Pick(non_gold_items)
            add_inventory(game_state, item_name, 1)
        else: # Only gold exists, add a special item
            add_inventory(game_state, special_item(), 1)
    else:
        add_inventory(game_state, special_item(), 1)


def _lpick(item_list, goal_level):
    """Pick item from list closest to goal_level (like JS LPick)."""
    if not item_list: return None
    result_item = Pick(item_list)
    best_diff = abs(goal_level - result_item[1]) # item_list expected [(name, level), ...]

    for _ in range(5): # Check 5 more times
        candidate = Pick(item_list)
        diff = abs(goal_level - candidate[1])
        if diff < best_diff:
            result_item = candidate
            best_diff = diff
    return result_item


def win_equip(game_state):
    """Generates and equips a random piece of equipment suitable for the level."""
    level = get_trait_i(game_state, 'Level')
    posn = Random(len(EQUIPS)) # 0 = Weapon, 1 = Shield, 2+ = Armor slots

    if posn == 0: # Weapon
        equip_slot = EQUIPS[posn]
        base_items = WEAPONS
        better_attribs = OFFENSE_ATTRIB
        worse_attribs = OFFENSE_BAD
    elif posn == 1: # Shield
        equip_slot = EQUIPS[posn]
        base_items = SHIELDS
        better_attribs = DEFENSE_ATTRIB
        worse_attribs = DEFENSE_BAD
    else: # Armor
        equip_slot = EQUIPS[posn]
        base_items = ARMORS
        better_attribs = DEFENSE_ATTRIB
        worse_attribs = DEFENSE_BAD

    # Pick base item closest to player level
    chosen_base = _lpick(base_items, level)
    if not chosen_base: return
    base_name, base_qual = chosen_base

    # Calculate plus/minus based on level difference
    plus = level - base_qual
    current_name = base_name
    attribs_to_use = better_attribs if plus >= 0 else worse_attribs

    count = 0
    remaining_plus = plus
    used_modifiers = set()

    while count < 2 and remaining_plus != 0 and attribs_to_use:
        # Pick modifier closest to remaining plus/minus, without going over
        best_mod = None
        best_mod_diff = float('inf')

        possible_mods = [mod for mod in attribs_to_use if mod[0] not in used_modifiers]
        if not possible_mods: break

        for mod_name, mod_qual in possible_mods:
            # Modifier must be in the same direction (positive/negative) as remaining_plus
            if (remaining_plus > 0 and mod_qual > 0) or (remaining_plus < 0 and mod_qual < 0) :
                 # Check if it doesn't "overshoot"
                 if abs(remaining_plus) >= abs(mod_qual):
                     # Prefer closer values
                      diff = abs(remaining_plus - mod_qual)
                      if diff < best_mod_diff:
                           best_mod_diff = diff
                           best_mod = (mod_name, mod_qual)

        if best_mod:
            mod_name, mod_qual = best_mod
            if mod_name in current_name: break # Avoid repeats like "Polished Polished"
            current_name = mod_name + ' ' + current_name
            remaining_plus -= mod_qual
            used_modifiers.add(mod_name)
            count += 1
        else:
            break # No suitable modifier found

    # Add remaining plus/minus as prefix
    if remaining_plus != 0:
        prefix = f"+{remaining_plus}" if remaining_plus > 0 else str(remaining_plus)
        current_name = prefix + ' ' + current_name

    update_equip(game_state, equip_slot, current_name)
    game_state["bestequip"] = current_name # Store this as the latest generated item


def win_spell(game_state):
    """Adds a random spell, favoring lower index spells (JS RandomLow)."""
    wis = get_stat(game_state, 'WIS')
    level = get_trait_i(game_state, 'Level')
    max_spell_index = min(wis + level, len(SPELLS))
    if max_spell_index > 0:
         spell_index = RandomLow(max_spell_index)
         add_spell(game_state, SPELLS[spell_index], 1)


def win_stat(game_state):
    """Increases a random stat, favoring the current highest stat."""
    if Random(2) == 0:
        # Pick any stat (including HP/MP Max)
        stat_to_increase = Pick(STATS)
    else:
        # Favor prime stats based on squared value (like JS)
        total_sq = sum(get_stat(game_state, s)**2 for s in PRIME_STATS)
        if total_sq <= 0: # Handle case where all stats are 0
            stat_to_increase = Pick(PRIME_STATS)
        else:
            roll = Random(total_sq)
            current_sum = 0
            stat_to_increase = PRIME_STATS[-1] # Default to last if loop fails
            for s in PRIME_STATS:
                current_sum += get_stat(game_state, s)**2
                if roll < current_sum:
                    stat_to_increase = s
                    break
    add_stat(game_state, stat_to_increase, 1)


def named_monster(game_state, target_level):
    """Generate a named monster close to the target level."""
    best_monster_info = None
    min_diff = float('inf')

    for _ in range(5): # Check 5 monsters
        monster_tuple = Pick(MONSTERS)
        m_name, m_level, m_loot = monster_tuple
        diff = abs(target_level - m_level)
        if best_monster_info is None or diff < min_diff:
            min_diff = diff
            best_monster_info = monster_tuple

    if best_monster_info:
        m_name, m_level, m_loot = best_monster_info
        return f"{generate_name()} the {m_name}"
    return "a generic foe" # Fallback


def impressive_guy(game_state):
    """Generate a name for an impressive NPC."""
    if Random(2) == 0:
        race_name = plural(Pick(RACES)[0])
        title = Pick(IMPRESSIVE_TITLES)
        return f"the {title} of the {race_name}"
    else:
        title = Pick(IMPRESSIVE_TITLES)
        return f"{title} {generate_name()} of {generate_name()}"


def monster_task(game_state):
    """Generates the next monster encounter task."""
    level = get_trait_i(game_state, 'Level')
    # Adjust level slightly randomly (like JS loop)
    for _ in range(level):
        if Random(5) < 2: # Odds(2,5)
            level += RandSign()
    level = max(1, level) # Ensure level is at least 1

    target_level = level
    qty = 1
    definite_article = False

    # Pick monster closest to target level
    # (Simplified: JS picks 5 random, we pick the best of 5 attempts)
    monster_tuple = None
    min_diff = float('inf')
    # Check quest monster first? JS does: `if game.questmonster and Odds(1,4)`
    if game_state.get("questmonster") and Random(4) == 0:
         monster_tuple = game_state["questmonster"] # Use quest monster tuple
    else:
         for _ in range(5):
              candidate = Pick(MONSTERS)
              diff = abs(target_level - candidate[1])
              if monster_tuple is None or diff < min_diff:
                   min_diff = diff
                   monster_tuple = candidate

    if not monster_tuple: monster_tuple = MONSTERS[0] # Fallback

    base_name, base_level, base_loot = monster_tuple
    current_name = base_name
    level_diff = target_level - base_level

    # Handle level disparity: quantity or modifiers
    if level_diff > 10 and base_level > 0:
        # Too weak, multiply quantity
        qty = div_floor(target_level + Random(base_level), base_level)
        qty = max(1, qty)
        target_level = div_floor(target_level, qty) # Adjust effective level per monster
        level_diff = target_level - base_level # Recalculate diff for modifiers
    elif level_diff < -10:
        current_name = 'imaginary ' + current_name
    elif level_diff < 0:
        # Apply negative modifiers (sick/young)
        i = 10 + level_diff # Range 0 to 9 for diff -10 to -1
        mod1_strength = 5 - Random(abs(i) + 1) # Strength for first modifier (max 5)
        mod2_strength = level_diff - mod1_strength # Remaining difference

        if Random(2) == 0: # Randomly pick order
            current_name = sick_prefix(mod1_strength, young_prefix(mod2_strength, current_name))
        else:
            current_name = young_prefix(mod1_strength, sick_prefix(mod2_strength, current_name))

    elif level_diff > 0 :
         # Apply positive modifiers (big/special)
         i = 10 - level_diff # Range 0 to 9 for diff 10 to 1
         mod1_strength = 5 - Random(abs(i) + 1)
         mod2_strength = level_diff - mod1_strength

         if Random(2) == 0:
              current_name = big_prefix(mod1_strength, special_prefix(mod2_strength, current_name))
         else:
              current_name = special_prefix(mod1_strength, big_prefix(mod2_strength, current_name))

    # Recalculate final effective level for XP/duration?
    final_level = target_level * qty

    # Set task duration based on relative difficulty
    player_level = get_trait_i(game_state, 'Level')
    duration_factor = 3 # From JS formula inspection
    duration_msec = div_floor(2 * duration_factor * final_level * 1000, player_level)
    duration_msec = max(500, duration_msec) # Ensure minimum duration

    # Prepare display name
    display_name = indefinite(current_name, qty) if not definite_article else definite(current_name, qty)

    # Set the task
    internal_task_id = f"kill|{base_name}|{base_level}|{base_loot}" # Store original monster info
    set_current_task(game_state, f"Executing {display_name}", duration_msec, internal_task_id)


# --- Game Progression ---

def complete_quest(game_state):
    """Complete the current quest and start a new one."""
    quest_bar_max = 50 + Random(100)
    update_bar_max(game_state, "QuestBar", quest_bar_max)
    set_bar_position(game_state, "QuestBar", 0)

    quests = game_state.get("Quests", [])
    if quests:
        _log_event(game_state, f"Quest completed: {game_state.get('bestquest', 'an unknown quest')}")
        # Award reward
        reward_func = Pick([win_spell, win_equip, win_stat, win_item])
        reward_func(game_state) # Call the chosen reward function

    # Limit quest log length (like JS)
    while len(quests) >= 100: # JS used > 99
        quests.pop(0)

    # Generate new quest
    game_state["questmonster"] = None # Clear quest monster target
    game_state["questmonsterindex"] = -1
    caption = ""
    quest_type = Random(5)

    if quest_type == 0: # Exterminate
        level = get_trait_i(game_state, 'Level')
        best_monster = None
        min_diff = float('inf')
        for i in range(4): # Pick best of 4 for quest target
            montag = Random(len(MONSTERS))
            m_tuple = MONSTERS[montag]
            diff = abs(m_tuple[1] - level)
            if best_monster is None or diff < min_diff:
                min_diff = diff
                best_monster = m_tuple
                game_state["questmonsterindex"] = montag # Store index

        if best_monster:
            game_state["questmonster"] = best_monster # Store tuple (Name, Level, Loot)
            caption = f"Exterminate {definite(best_monster[0], 2)}"
        else:
             caption = "Exterminate something nasty" # Fallback

    elif quest_type == 1: # Seek Item
        caption = f"Seek {definite(interesting_item(), 1)}"
    elif quest_type == 2: # Deliver Item
        caption = f"Deliver this {boring_item()}"
    elif quest_type == 3: # Fetch Item
        caption = f"Fetch me {indefinite(boring_item(), 1)}"
    elif quest_type == 4: # Placate Monster
        level = get_trait_i(game_state, 'Level')
        best_monster = None
        min_diff = float('inf')
        for i in range(2): # Pick best of 2 for placate target
            m_tuple = Pick(MONSTERS)
            diff = abs(m_tuple[1] - level)
            if best_monster is None or diff < min_diff:
                min_diff = diff
                best_monster = m_tuple
        if best_monster:
             caption = f"Placate {definite(best_monster[0], 2)}"
             # Don't set questmonster target for placate quests
        else:
             caption = "Placate someone important" # Fallback

    if not caption: caption = "Do something heroic" # Ultimate fallback

    quests.append(caption)
    game_state["bestquest"] = caption
    _log_event(game_state, f"Commencing quest: {caption}")
    # SaveGame() call removed, should be handled by main loop


def complete_act(game_state):
    """Complete the current act and start the next."""
    game_state["act"] += 1
    act_roman = to_roman(game_state["act"])
    game_state["bestplot"] = f"Act {act_roman}"

    # Calculate plot bar max for the new act
    # JS: 60 * 60 * (1 + 5 * game.act) -> 1 hour + 5 hours per act
    plot_bar_max = 3600 * (1 + 5 * game_state["act"])
    update_bar_max(game_state, "PlotBar", plot_bar_max)
    set_bar_position(game_state, "PlotBar", 0)

    # Add act to plot list (like JS Plots.AddUI)
    # We don't need a separate plot list, bestplot tracks current
    if game_state["act"] > 1: # Rewards only after Act I
        win_item(game_state)
        win_equip(game_state)

    _log_event(game_state, f"Act Completed! Starting {game_state['bestplot']}")
    # Brag('a') call removed (online feature)


def level_up(game_state):
    """Handle character leveling up."""
    current_level = get_trait_i(game_state, 'Level')
    update_trait(game_state, 'Level', current_level + 1)

    # Increase HP/MP Max
    con = get_stat(game_state, 'CON')
    intel = get_stat(game_state, 'INT')
    add_stat(game_state, 'HP Max', div_floor(con, 3) + 1 + Random(4))
    add_stat(game_state, 'MP Max', div_floor(intel, 3) + 1 + Random(4))

    # Gain stats and spell
    win_stat(game_state)
    win_stat(game_state)
    win_spell(game_state)

    # Reset XP bar for the new level
    new_xp_max = level_up_time(current_level + 1)
    update_bar_max(game_state, "ExpBar", new_xp_max)
    set_bar_position(game_state, "ExpBar", 0)

    # Update best stat string
    game_state["beststat"] = find_best_stat_string(game_state)

    _log_event(game_state, f"Leveled up to Level {current_level + 1}!")
    # Brag('l') call removed


def interplot_cinematic(game_state):
    """Adds cinematic task sequences to the queue."""
    choice = Random(3)
    if choice == 0:
        add_task_to_queue(game_state, 'task|1000|Exhausted, you arrive at a friendly oasis in a hostile land')
        add_task_to_queue(game_state, 'task|2000|You greet old friends and meet new allies')
        add_task_to_queue(game_state, 'task|2000|You are privy to a council of powerful do-gooders')
        add_task_to_queue(game_state, 'task|1000|There is much to be done. You are chosen!')
    elif choice == 1:
        level = get_trait_i(game_state, 'Level')
        nemesis = named_monster(game_state, level + 3)
        add_task_to_queue(game_state, 'task|1000|Your quarry is in sight, but a mighty enemy bars your path!')
        add_task_to_queue(game_state, f'task|4000|A desperate struggle commences with {nemesis}')
        s = Random(3)
        for _ in range(Random(1 + game_state.get('act', 0) + 1)):
            s += 1 + Random(2)
            duration = 2000
            if s % 3 == 0: desc = f'Locked in grim combat with {nemesis}'
            elif s % 3 == 1: desc = f'{nemesis} seems to have the upper hand'
            else: desc = f'You seem to gain the advantage over {nemesis}'
            add_task_to_queue(game_state, f'task|{duration}|{desc}')
        add_task_to_queue(game_state, f'task|3000|Victory! {nemesis} is slain! Exhausted, you lose consciousness')
        add_task_to_queue(game_state, 'task|2000|You awake in a friendly place, but the road awaits')
    elif choice == 2:
        nemesis2 = impressive_guy(game_state)
        add_task_to_queue(game_state, f"task|2000|Oh sweet relief! You've reached the kind protection of {nemesis2}")
        add_task_to_queue(game_state, f'task|3000|There is rejoicing, and an unnerving encounter with {nemesis2} in private')
        add_task_to_queue(game_state, f'task|2000|You forget your {boring_item()} and go back to get it')
        add_task_to_queue(game_state, "task|2000|What's this!? You overhear something shocking!")
        add_task_to_queue(game_state, f'task|2000|Could {nemesis2} be a dirty double-dealer?')
        add_task_to_queue(game_state, 'task|3000|Who can possibly be trusted with this news!? -- Oh yes, of course')

    # End cinematic with a plot loading task
    add_task_to_queue(game_state, 'plot|1000|Loading') # Duration 1 sec for loading


def process_task_completion(game_state):
    """Handles logic after the current task finishes."""
    task_id = game_state.get("task", "")

    if task_id.startswith('kill|'):
        parts = task_id.split('|')
        if len(parts) == 4:
            monster_name, level_str, loot = parts[1], parts[2], parts[3]
            if loot == '*': # Special loot (like dragon hoard?) -> WinItem
                win_item(game_state)
            elif loot: # Specific loot part
                item_name = f"{monster_name.lower()} {loot.capitalize()}"
                add_inventory(game_state, item_name, 1)
            # else: No loot for this monster type
    elif task_id == 'buying':
        level = get_trait_i(game_state, 'Level')
        price = 5 * level**2 + 10 * level + 20
        add_inventory(game_state, 'Gold', -price)
        win_equip(game_state)
    elif task_id == 'sell':
        # Selling logic is handled within the dequeue loop now
        pass
    elif task_id == 'market':
         # Just arrived, selling starts on next tick if needed
         pass
    elif task_id == 'heading':
         # Just arrived, killing starts next tick
         pass

    # Task completed, clear internal task id
    game_state["task"] = ""

def process_tick(game_state, elapsed_msec):
    """Process one tick of game time."""
    increment_bar(game_state, "TaskBar", elapsed_msec)

    if not is_bar_done(game_state, "TaskBar"):
        return # Current task not finished

    # --- Task is Done ---
    completed_task_duration = game_state.get("TaskBar", {}).get("max", 0)
    game_state["tasks"] = game_state.get("tasks", 0) + 1
    game_state["elapsed"] = game_state.get("elapsed", 0) + div_floor(completed_task_duration, 1000)

    process_task_completion(game_state)

    # Check for level up / quest / plot progression (only after kill tasks usually)
    is_kill_task = game_state.get("task", "").startswith("kill|") # Check based on *previous* task id if needed
                                                                 # For now, check if *next* task is likely kill
    is_advancement_tick = is_kill_task or not game_state.get("act", 0) # Advance on kills or before Act 1

    if is_advancement_tick:
        # Experience and Level Up
        if is_bar_done(game_state, "ExpBar"):
            level_up(game_state)
        else:
            increment_bar(game_state, "ExpBar", div_floor(completed_task_duration, 1000))

        # Quest Progression (only after Act 0)
        if game_state.get("act", 0) >= 1:
            if not game_state.get("Quests"): # No quests yet? Start one.
                complete_quest(game_state)
            elif is_bar_done(game_state, "QuestBar"):
                 complete_quest(game_state)
            else:
                 increment_bar(game_state, "QuestBar", div_floor(completed_task_duration, 1000))

        # Plot Progression
        if is_bar_done(game_state, "PlotBar"):
            interplot_cinematic(game_state)
        else:
            increment_bar(game_state, "PlotBar", div_floor(completed_task_duration, 1000))


    # --- Dequeue Next Task ---
    while is_bar_done(game_state, "TaskBar"): # Process queue until a task takes time
        next_task_str = dequeue_task(game_state)

        if next_task_str:
            parts = next_task_str.split('|')
            task_type = parts[0]
            duration = str_to_int_def(parts[1], 1) * 1000 # Duration in seconds from queue
            description = parts[2] if len(parts) > 2 else "Doing something..."

            if task_type == 'plot':
                complete_act(game_state)
                # Description is usually "Loading", set by complete_act->interplot or directly
                set_current_task(game_state, game_state["bestplot"], duration, "plot_loading")
            elif task_type == 'task':
                set_current_task(game_state, description, duration, "queued_task")
            else:
                print(f"Warning: Unknown task type in queue: {task_type}")
                set_current_task(game_state, "Thinking...", 500, "unknown_task") # Placeholder

        # If queue empty, decide next action
        elif is_bar_done(game_state, "EncumBar"):
            set_current_task(game_state, "Heading to market to sell loot", 4000, "market")
        elif game_state.get("task") in ['market', 'sell']: # Check if currently selling
            inventory = game_state.get("Inventory", [])
            item_to_sell = None
            sell_index = -1
            # Find first non-Gold item to sell
            for i, (name, qty) in enumerate(inventory):
                 if name != "Gold":
                      item_to_sell = name
                      sell_index = i
                      break

            if item_to_sell:
                # Calculate sale price
                level = get_trait_i(game_state, 'Level')
                base_price = level # Base price per item = level
                if ' of ' in item_to_sell: # Magic item bonus
                    base_price *= (1 + RandomLow(10)) * (1 + RandomLow(level))
                amt = inventory[sell_index][1] * base_price

                # Set selling task
                sell_desc = f"Selling {indefinite(item_to_sell, inventory[sell_index][1])}"
                set_current_task(game_state, sell_desc, 1000, "sell") # 1 sec to sell

                # Perform sale transaction *now* before the task starts visually
                # (Original JS did it after task completion)
                add_inventory(game_state, item_to_sell, -inventory[sell_index][1]) # Remove sold item
                add_inventory(game_state, 'Gold', amt) # Add gold

            else: # Nothing left to sell
                 game_state["task"] = "" # Clear market/sell status
                 set_current_task(game_state, "Heading to the killing fields", 4000, "heading")

        # Buy equipment if affordable and not just finished selling/heading
        elif (get_inventory_item_qty(game_state, 'Gold') > (5 * get_trait_i(game_state, 'Level')**2 + 10 * get_trait_i(game_state, 'Level') + 20)) and \
             game_state.get("task") not in ['heading', 'market', 'sell']:
             set_current_task(game_state, "Negotiating purchase of better equipment", 5000, "buying")

        # Default: Go killing
        else:
             monster_task(game_state) # This sets the task description and duration

        # Make sure taskbar isn't already done if duration was 0
        if game_state.get("TaskBar", {}).get("max", 0) == 0:
             set_bar_position(game_state, "TaskBar", 1) # Ensure it's not done immediately


# --- Character Creation ---

def roll_stats():
    """Roll 6 primary stats (3d6 each) and calculate HP/MP."""
    stats = {"seed": get_random_state()} # Store seed used for these rolls
    total = 0
    best_val = -1
    best_stat_name = ""
    for stat_name in PRIME_STATS:
        roll = 3 + Random(6) + Random(6) + Random(6)
        stats[stat_name] = roll
        total += roll
        if roll > best_val:
            best_val = roll
            best_stat_name = stat_name

    stats["best"] = best_stat_name # Store best stat *at creation*
    stats['HP Max'] = Random(8) + div_floor(stats.get('CON', 0), 6)
    stats['MP Max'] = Random(8) + div_floor(stats.get('INT', 0), 6)
    stats["total"] = total # Store total roll for display/color coding if needed
    return stats

def create_new_character(name, race_name, class_name, stats_dict):
    """Creates a new game state dictionary for a starting character."""
    game_state = copy.deepcopy(DEFAULT_SAVE_SCHEMA) # Start with schema

    # Basic Info
    game_state["Traits"]["Name"] = name
    game_state["Traits"]["Race"] = race_name
    game_state["Traits"]["Class"] = class_name
    game_state["Traits"]["Level"] = 1
    game_state["birthday"] = time.strftime("%Y-%m-%d %H:%M:%S")
    game_state["birthstamp"] = time.time()
    game_state["date"] = game_state["birthday"]
    game_state["stamp"] = game_state["birthstamp"]
    game_state["saveName"] = name

    # Stats
    game_state["Stats"] = stats_dict # Use the rolled stats
    game_state["dna"] = stats_dict["seed"] # Use the seed from stat rolling as DNA
    game_state["seed"] = get_random_state() # Set current PRNG state

    # Initial Equipment
    game_state["Equips"]["Weapon"] = "Sharp Rock"
    game_state["Equips"]["Hauberk"] = "-3 Burlap" # Default starting armor
    game_state["bestequip"] = "Sharp Rock" # Initial best

    # Initial State
    game_state["act"] = 0
    game_state["bestplot"] = "Prologue"
    game_state["kill"] = "Loading...."
    game_state["Inventory"] = [['Gold', 0]] # Ensure starting gold is 0
    game_state["Spells"] = []
    game_state["Quests"] = []

    # Initial Bar Values
    update_bar_max(game_state, "ExpBar", level_up_time(1))
    update_bar_max(game_state, "EncumBar", 10 + get_stat(game_state, 'STR'))
    update_bar_max(game_state, "PlotBar", 26) # Initial prologue time? JS seems low. Let's use JS value.
    update_bar_max(game_state, "QuestBar", 1) # Will be reset on first quest
    update_bar_max(game_state, "TaskBar", 2000) # Initial loading task

    set_bar_position(game_state, "ExpBar", 0)
    set_bar_position(game_state, "EncumBar", 0)
    set_bar_position(game_state, "PlotBar", 0)
    set_bar_position(game_state, "QuestBar", 0)
    set_bar_position(game_state, "TaskBar", 0)

    # Initial Task Queue (Prologue)
    game_state["queue"] = [
      'task|10|Experiencing an enigmatic and foreboding night vision',
      "task|6|Much is revealed about that wise old bastard you'd underestimated",
      'task|6|A shocking series of events leaves you alone and bewildered, but resolute',
      'task|4|Drawing upon an unrealized reserve of determination, you set out on a long and dangerous journey',
      'plot|2|Loading' # Ends prologue, starts Act 1 loading
    ]

    # Calculate initial best stat/spell strings
    game_state["beststat"] = find_best_stat_string(game_state)
    game_state["bestspell"] = find_best_spell_string(game_state) # Will be empty

    return game_state


# --- Save/Load ---

def b64_encode(data):
    """Encode dictionary to base64 string."""
    json_str = json.dumps(data, separators=(',', ':')) # Compact JSON
    json_bytes = json_str.encode('utf-8')
    b64_bytes = base64.b64encode(json_bytes)
    return b64_bytes.decode('utf-8')

def b64_decode(b64_str):
    """Decode base64 string back to dictionary."""
    try:
        json_bytes = base64.b64decode(b64_str)
        json_str = json_bytes.decode('utf-8')
        return json.loads(json_str)
    except (base64.binascii.Error, json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"Error decoding save data: {e}")
        return None

def save_game(game_state, filename=None):
    """Saves the game state to a .pqw file (base64 encoded JSON)."""
    if not game_state or "Traits" not in game_state:
        print("Invalid game state, cannot save.")
        return False

    # Update timestamp and current seed before saving
    game_state["date"] = time.strftime("%Y-%m-%d %H:%M:%S")
    game_state["stamp"] = time.time()
    game_state["seed"] = get_random_state() # Capture current PRNG state

    # Recalculate bests before saving (like JS HotOrNot)
    game_state["beststat"] = find_best_stat_string(game_state)
    game_state["bestspell"] = find_best_spell_string(game_state)
    # bestequip is updated dynamically

    if filename is None:
        char_name = game_state.get("Traits", {}).get("Name", "UnnamedCharacter")
        filename = f"{char_name}.pqw"

    filepath = SAVE_DIR / filename
    try:
        b64_data = b64_encode(game_state)
        with open(filepath, 'w') as f:
            f.write(b64_data)
        # _log_event(game_state, f"Game saved: {filename}") # Log after successful save
        print(f"Game saved to {filepath}")
        return True
    except Exception as e:
        print(f"Error saving game to {filepath}: {e}")
        # _log_event(game_state, f"Save FAILED: {e}")
        return False


def load_game(filename):
    """Loads a game state from a .pqw file."""
    filepath = SAVE_DIR / filename
    if not filepath.is_file():
        print(f"Save file not found: {filepath}")
        return None

    try:
        # Use a separate try block just for file reading to ensure proper closure
        b64_data = None
        try:
            with open(filepath, 'r') as f:
                b64_data = f.read()
        except Exception as file_error:
            print(f"Error reading file {filepath}: {file_error}")
            return None

        if not b64_data:
            print(f"Empty or invalid file: {filepath}")
            return None

        game_state = b64_decode(b64_data)

        if game_state:
            # Restore PRNG state
            set_random_state(game_state.get("seed"))
            # _log_event(game_state, f"Game loaded: {filename}")
            print(f"Game loaded from {filepath}")

            # Ensure essential keys exist, merging with default schema if necessary
            # This handles loading older saves that might lack newer fields.
            merged_state = copy.deepcopy(DEFAULT_SAVE_SCHEMA)
            # Update recursively to preserve nested structure
            def recursive_update(target, source):
                for key, value in source.items():
                    if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                        recursive_update(target[key], value)
                    elif key in target: # Only update if key exists in schema
                         target[key] = value
                    # Do not add keys not present in the schema

            recursive_update(merged_state, game_state)

             # Recalculate bar hints after loading, as they are transient
            for bar_key in ["ExpBar", "EncumBar", "PlotBar", "QuestBar", "TaskBar"]:
                set_bar_position(merged_state, bar_key, merged_state[bar_key].get('position', 0))

            # Ensure encumbrance is correct after load
            update_encumbrance(merged_state)

            return merged_state
        else:
            print(f"Failed to decode game data from {filepath}")
            return None # Decoding failed

    except Exception as e:
        print(f"Error loading game from {filepath}: {e}")
        return None

def get_saved_games():
    """Returns a list of .pqw filenames in the savegame directory."""
    return [f.name for f in SAVE_DIR.glob("*.pqw")]

def delete_save_game(filename):
    """Deletes a save game file."""
    filepath = SAVE_DIR / filename
    try:
        if filepath.is_file():
            os.remove(filepath)
            print(f"Deleted save file: {filepath}")
            return True
        else:
            print(f"Save file not found for deletion: {filepath}")
            return False
    except Exception as e:
        print(f"Error deleting save file {filepath}: {e}")
        return False