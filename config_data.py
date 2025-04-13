# START OF FILE: config_data.py
# File: config_data.py
# Holds the game configuration data, similar to Config.pas/Config.dfm
import math
import re
import time
import datetime # For timestamps
import sys

# ----------------------------------------------------------------------------
# Alea PRNG Port (Based on Johannes Baagøe's JavaScript implementation)
# ----------------------------------------------------------------------------
class Mash:
    def __init__(self):
        self.n = 0xefc8249d

    def mash(self, data):
        data_str = str(data)
        for char in data_str:
            self.n += ord(char)
            h = 0.02519603282416938 * self.n
            self.n = int(h) & 0xffffffff # Use unsigned 32-bit int directly
            h -= self.n
            h *= self.n
            self.n = int(h) & 0xffffffff
            h -= self.n
            self.n += int(h * 0x100000000) # 2^32
        # Ensure result is a non-negative float between 0 and 1
        return (self.n & 0xffffffff) * 2.3283064365386963e-10 # 2^-32

class Alea:
    def __init__(self, *args):
        self.s0 = 0
        self.s1 = 0
        self.s2 = 0
        self.c = 1
        self.args = args if args else [time.time()] # Use current time if no seed

        mash_instance = Mash()
        self.s0 = mash_instance.mash(' ')
        self.s1 = mash_instance.mash(' ')
        self.s2 = mash_instance.mash(' ')

        for arg in self.args:
            self.s0 -= mash_instance.mash(arg)
            if self.s0 < 0: self.s0 += 1
            self.s1 -= mash_instance.mash(arg)
            if self.s1 < 0: self.s1 += 1
            self.s2 -= mash_instance.mash(arg)
            if self.s2 < 0: self.s2 += 1

    def random(self):
        t = 2091639 * self.s0 + self.c * 2.3283064365386963e-10 # 2^-32
        self.s0 = self.s1
        self.s1 = self.s2
        # Ensure c remains within integer bounds if possible, or handle potential overflow
        # The JS `t | 0` performs a ToInt32 operation.
        c_int = int(t) # Truncate towards zero
        self.c = c_int
        self.s2 = t - self.c
        # Return value should be in [0, 1)
        return self.s2

    def uint32(self):
        # In JS `random() * 0x100000000` might exceed standard float precision
        # but ultimately gets treated as a 32-bit unsigned int.
        # We can simulate this by scaling and taking the integer part modulo 2^32.
        val = int(self.random() * (2**32))
        return val & 0xFFFFFFFF # Ensure it's treated as unsigned 32-bit

    def fract53(self):
        # High precision fraction using two calls
        return self.random() + (int(self.random() * 0x200000) & 0xFFFFFFFF) * 1.1102230246251565e-16 # 2^-53

    def state(self, newstate=None):
        if newstate and len(newstate) == 4:
            # Handle potential type issues if loading from JSON (floats vs ints)
            self.s0 = float(newstate[0])
            self.s1 = float(newstate[1])
            self.s2 = float(newstate[2])
            self.c = float(newstate[3]) # c can be float in calculation, though JS truncates
        # Return state as a list of floats for JSON compatibility
        return [float(self.s0), float(self.s1), float(self.s2), float(self.c)]

# Global RNG instance
_alea_instance = Alea() # Initialize with default seed (time)

def randseed(set_value=None):
    """Gets or sets the current state of the global Alea PRNG."""
    global _alea_instance
    if set_value is not None:
         # If setting, ensure it's a valid state list/tuple
         if isinstance(set_value, (list, tuple)) and len(set_value) == 4:
              _alea_instance.state(set_value)
         else:
              # If not a valid state, assume it's a seed value and re-initialize
              print(f"Warning: Invalid RNG state provided: {set_value}. Re-seeding.")
              _alea_instance = Alea(set_value)
    # Always return the current state
    return _alea_instance.state()


def Random(n):
    """Generate a random integer between 0 and n-1 (inclusive)."""
    if n <= 0: return 0
    return _alea_instance.uint32() % n

# ----------------------------------------------------------------------------

# --- Game Content Data (Aligned with config.js where possible) ---

RACES = {
    # Name: {bonuses: [list_of_bonuses]}
    "Half Orc": {"bonuses": ["HP Max"]},
    "Half Man": {"bonuses": ["CHA"]},
    "Half Halfling": {"bonuses": ["DEX"]},
    "Double Hobbit": {"bonuses": ["STR"]},
    "Hob-Hobbit": {"bonuses": ["DEX", "CON"]},
    "Low Elf": {"bonuses": ["CON"]},
    "Dung Elf": {"bonuses": ["WIS"]},
    "Talking Pony": {"bonuses": ["MP Max", "INT"]},
    "Gyrognome": {"bonuses": ["DEX"]},
    "Lesser Dwarf": {"bonuses": ["CON"]},
    "Crested Dwarf": {"bonuses": ["CHA"]},
    "Eel Man": {"bonuses": ["DEX"]},
    "Panda Man": {"bonuses": ["CON", "STR"]},
    "Trans-Kobold": {"bonuses": ["WIS"]},
    "Enchanted Motorcycle": {"bonuses": ["MP Max"]}, # Originally Bonus=MPMax
    "Will o' the Wisp": {"bonuses": ["WIS"]}, # Originally Bonus=WIS
    "Battle-Finch": {"bonuses": ["DEX", "INT"]},
    "Double Wookiee": {"bonuses": ["STR"]},
    "Skraeling": {"bonuses": ["WIS"]},
    "Demicanadian": {"bonuses": ["CON"]},
    "Land Squid": {"bonuses": ["STR", "HP Max"]},
}

KLASSES = {
    # Name: {bonuses: [list_of_bonuses]}
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
    # "Lowling": {"bonuses": ["WIS"]}, # Missing from original Python, present in JS
    "Jungle Clown": {"bonuses": ["DEX", "CHA"]}, # Present in Python, missing from JS
    "Birdrider": {"bonuses": ["WIS"]},
    "Vermineer": {"bonuses": ["INT"]},
}

# Use tuples (Name, Level) matching Python structure but data from JS
WEAPONS = [
    ("Stick", 0), ("Broken Bottle", 1), ("Shiv", 1), ("Sprig", 1), ("Oxgoad", 1),
    ("Eelspear", 2), ("Bowie Knife", 2), ("Claw Hammer", 2), ("Handpeen", 2),
    ("Andiron", 3), ("Hatchet", 3), ("Tomahawk", 3), ("Hackbarm", 3),
    ("Crowbar", 4), ("Mace", 4), ("Battleadze", 4),
    ("Leafmace", 5), ("Shortsword", 5), ("Longiron", 5), ("Poachard", 5), ("Baselard", 5),
    ("Whinyard", 6), ("Blunderbuss", 6), ("Longsword", 6), ("Crankbow", 6),
    ("Blibo", 7), ("Broadsword", 7), ("Kreen", 7), ("Warhammer", 7), # Warhammer from JS
    ("Morning Star", 8), ("Pole-adze", 8), ("Spontoon", 8),
    ("Bastard Sword", 9), ("Peen-arm", 9),
    ("Culverin", 10), ("Lance", 10),
    ("Halberd", 11), ("Poleax", 12),
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

# Use tuples (Name, Modifier)
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

SPELLS = [ # From JS config.js, slightly different than original Python
    'Slime Finger', 'Rabbit Punch', 'Hastiness', 'Good Move', 'Sadness',
    'Seasick', 'Shoelaces', 'Inoculate', 'Cone of Annoyance', 'Magnetic Orb',
    'Invisible Hands', 'Revolting Cloud', 'Aqueous Humor', 'Spectral Miasma',
    'Clever Fellow', 'Lockjaw', 'History Lesson', 'Hydrophobia', 'Big Sister',
    'Cone of Paste', 'Mulligan', "Nestor's Bright Idea", 'Holy Batpole',
    'Tumor (Benign)', 'Braingate', #'Summon a Bitch', # Excluded from JS, originally in C++? Keep excluded.
    'Nonplus', 'Animate Nightstand',
    'Eye of the Troglodyte', 'Curse Name', 'Dropsy', 'Vitreous Humor',
    "Roger's Grand Illusion", 'Covet', #'Black Idaho', # Excluded from JS
    'Astral Miasma', 'Spectral Oyster',
    'Acrid Hands', 'Angioplasty', "Grognor's Big Day Off", 'Tumor (Malignant)',
    'Animate Tunic', 'Ursine Armor', 'Holy Roller', 'Tonsillectomy',
    'Curse Family', 'Infinite Confusion',
]


BORING_ITEMS = [ # From JS config.js
    'nail', 'lunchpail', 'sock', 'I.O.U.', 'cookie', 'pint', 'toothpick',
    'writ', 'newspaper', 'letter', 'plank', 'hat', 'egg', 'coin', 'needle',
    'bucket', 'ladder', 'chicken', 'twig', 'dirtclod', 'counterpane',
    'vest', 'teratoma', 'bunny', 'rock', 'pole', 'carrot', 'canoe',
    'inkwell', 'hoe', 'bandage', 'trowel', 'towel', 'planter box',
    'anvil', 'axle', 'tuppence', 'casket', 'nosegay', 'trinket',
    'credenza', 'writ', # Writ appears twice in JS as well
]

SPECIALS = [ # Base name for special items (From JS)
    'Diadem', 'Festoon', 'Gemstone', 'Phial', 'Tiara', 'Scabbard', 'Arrow',
    'Lens', 'Lamp', 'Hymnal', 'Fleece', 'Laurel', 'Brooch', 'Gimlet',
    'Cobble', 'Albatross', 'Brazier', 'Bandolier', 'Tome', 'Garnet',
    'Amethyst', 'Candelabra', 'Corset', 'Sphere', 'Sceptre', 'Ankh',
    'Talisman', 'Orb', 'Gammel', 'Ornament', 'Brocade', 'Galoon', 'Bijou',
    'Spangle', 'Gimcrack', 'Hood', 'Vulpeculum',
]

ITEM_ATTRIB = [ # Prefixes for special items (From JS)
    'Golden', 'Gilded', 'Spectral', 'Astral', 'Garlanded', 'Precious',
    'Crafted', 'Dual', 'Filigreed', 'Cruciate', 'Arcane', 'Blessed',
    'Reverential', 'Lucky', 'Enchanted', 'Gleaming', 'Grandiose', 'Sacred',
    'Legendary', 'Mythic', 'Crystalline', 'Austere', 'Ostentatious',
    'One True', 'Proverbial', 'Fearsome', 'Deadly', 'Benevolent',
    'Unearthly', 'Magnificent', 'Iron', 'Ormolu', 'Puissant',
]

ITEM_OFS = [ # Suffixes for special items ("of X") (From JS)
    'Foreboding', 'Foreshadowing', 'Nervousness', 'Happiness', 'Torpor',
    'Danger', 'Craft', 'Silence', 'Invisibility', 'Rapidity', 'Pleasure',
    'Practicality', 'Hurting', 'Joy', 'Petulance', 'Intrusion', 'Chaos',
    'Suffering', 'Extroversion', 'Frenzy', 'Sisu', # Added from JS
    'Solitude', 'Punctuality',
    'Efficiency', 'Comfort', 'Patience', 'Internment', 'Incarceration',
    'Misapprehension', 'Loyalty', 'Envy', 'Acrimony', 'Worry', 'Fear',
    'Awe', 'Guile', 'Prurience', 'Fortune', 'Perspicacity', 'Domination',
    'Submission', 'Fealty', 'Hunger', 'Despair', 'Cruelty', 'Grob',
    'Dignard', 'Ra', 'the Bone', 'Diamonique', 'Electrum', 'Hydragyrum',
]

MONSTERS = [ # From JS config.js, formatted as (Name, Level, LootItem | * for generic)
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
    ("Naga", 9, "rattle"), ("Nebbish", 1, "belly"), ("Neo-Otyugh", 11, "organ "), # Trailing space in original JS
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
    ("Vampire", 8, "pancreas"), ("Wight", 4, "lung"), ("Will-o'-the-Wisp", 9, "wisp"), # Corrected typo from original python
    ("Wraith", 5, "finger"), ("Wyvern", 7, "wing"), ("Xorn", 7, "jaw"),
    ("Yeti", 4, "fur"), ("Zombie", 2, "forehead"), ("Wasp", 0, "stinger"),
    ("Rat", 1, "tail"), ("Bunny", 0, "ear"), ("Moth", 0, "dust"),
    ("Beagle", 0, "collar"), ("Midge", 0, "corpse"), ("Ostrich", 1, "beak"),
    ("Billy Goat", 1, "beard"), ("Bat", 1, "wing"), ("Koala", 2, "heart"),
    ("Wolf", 2, "paw"), ("Whippet", 2, "collar"), ("Uruk", 2, "boot"),
    ("Poroid", 4, "node"), ("Moakum", 8, "frenum"), ("Fly", 0, "*"),
    ("Hogbird", 3, "curl"),
    #("Wolog", 4, "lemma") # In JS, missing from original Python. Add it.
]

MONSTER_MODS = [ # From JS K.MonMods, tuple (LevelAdj, Pattern | * is placeholder)
    (-4, 'foetal *'), (-4, 'dying *'), (-3, 'crippled *'), (-3, 'baby *'),
    (-2, 'adolescent *'), (-2, 'very sick *'), (-1, 'lesser *'), (-1, 'undernourished *'),
    (1, 'greater *'), (1, '* Elder'), (2, 'war *'), (2, 'Battle-*'),
    (3, 'Were-*'), (3, 'undead *'), (4, 'giant *'), (4, '* Rex'),
]

EQUIPMENT_SLOTS = [ # Order from JS K.Equips
    "Weapon", "Shield", "Helm", "Hauberk", "Brassairts", "Vambraces",
    "Gauntlets", "Gambeson", "Cuisses", "Greaves", "Sollerets"
]

TITLES = ['Mr.', 'Mrs.', 'Sir', 'Sgt.', 'Ms.', 'Captain', 'Chief', 'Admiral', 'Saint']
IMPRESSIVE_TITLES = [ # From JS K.ImpressiveTitles
    "King", "Queen", "Lord", "Lady", "Viceroy", "Mayor", "Prince",
    "Princess", "Chief", "Boss", "Archbishop", "Chancellor", # Chancellor from JS
    "Baroness", #"Inquistor" # Inquisitor missing from JS, maybe typo? Use JS list.
]

NAME_PARTS = [ # From JS KParts
    # Consonants/clusters (start/mid) - adjusted '' frequency based on JS
    ['br', 'cr', 'dr', 'fr', 'gr', 'j', 'kr', 'l', 'm', 'n', 'pr', '', '', '', 'r', 'sh', 'tr', 'v', 'wh', 'x', 'y', 'z'],
    # Vowels
    ['a', 'a', 'e', 'e', 'i', 'i', 'o', 'o', 'u', 'u', 'ae', 'ie', 'oo', 'ou'],
    # Consonants (end/mid)
    ['b', 'ck', 'd', 'g', 'k', 'm', 'n', 'p', 't', 'v', 'x', 'z']
]

# --- Constants ---
BASE_ENCUMBRANCE = 10
SAVE_FILE_EXT = ".pqw"
BACKUP_FILE_EXT = ".bak"
TIMER_INTERVAL_MS = 33 # Match JS clock worker interval (20 fps)
SAVEGAME_FOLDER = "savegame" # Define save folder name

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
    background-color: #507a15; /* Match JS bar color */
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

/* Add these menu-specific styles */
QMenuBar {
    background-color: #2b2b2b;
    color: #f0f0f0;
}

QMenuBar::item:selected {
    background-color: #3a3a3a;
}

QMenuBar::item:pressed {
    background-color: #4a4a4a;
}

QMenu {
    background-color: #2b2b2b;
    border: 1px solid #3a3a3a;
}

QMenu::item {
    padding: 5px 20px;
}

QMenu::item:selected {
    background-color: #3a3a3a;
}

QMenu::item:pressed {
    background-color: #4a4a4a;
}
"""

# ----------------------------------------------------------------------------
# Helper Functions (Ported/Adapted from Delphi/JS)
# ----------------------------------------------------------------------------

def pick(items):
    """Pick a random item from a list using game RNG."""
    if not items:
        return None
    return items[Random(len(items))]

def pick_low(items):
    """Pick a random item, biased towards the lower end using game RNG."""
    if not items:
        return None
    count = len(items)
    if count == 0: return None
    idx1 = Random(count)
    idx2 = Random(count)
    return items[min(idx1, idx2)]

def odds(chance, outof):
    """Return True with a 'chance' out of 'outof' probability using game RNG."""
    if outof <= 0: return False # Avoid division by zero or weirdness
    return Random(outof) < chance

def rand_sign():
    """Return 1 or -1 randomly using game RNG."""
    return Random(2) * 2 - 1 # Results in -1 or 1

def ends(s, e):
    """Check if string s ends with string e."""
    return s.endswith(e)

def plural(s):
    """Pluralization logic based on JS version."""
    if not s: return ""
    s_lower = s.lower()

    # Handle specific cases from JS (man/Man)
    if ends(s, 'Man') or ends(s, 'man'):
        return s[:-2] + 'en'
    # JS rules
    elif ends(s_lower, 'y'):
        return s[:-1] + 'ies'
    elif ends(s_lower, 'us'):
        return s[:-2] + 'i'
    elif ends(s_lower, 'ch') or ends(s_lower, 'x') or ends(s_lower, 's') or ends(s_lower, 'sh'):
        return s + 'es'
    elif ends(s_lower, 'f'):
        return s[:-1] + 'ves'
    else:
        return s + 's'

def indefinite_article(s):
    """Return 'a' or 'an' based on the first letter of s (JS logic)."""
    if not s: return ""
    # Basic check matching JS Pos(s[0], 'AEIOUaeiou') > 0
    return 'an' if s[0].lower() in 'aeiouü' else 'a' # Include ü like JS

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
    """Convert an integer to Roman numeral string (Handles up to 39999). Matches JS toRoman."""
    if not isinstance(num, int): return "N" # Match JS null/NaN case
    if num == 0: return "N"
    if not 0 < abs(num) < 40000:
        return str(num) # Fallback for out-of-range

    s = ""
    n = num
    if n < 0:
        s = "-"
        n = -n

    roman_map = [
        (10000, "T"), (9000, "MT"), (5000, "A"), (4000, "MA"), (1000, "M"),
        (900, "CM"), (500, "D"), (400, "CD"), (100, "C"),
        (90, "XC"), (50, "L"), (40, "XL"), (10, "X"),
        (9, "IX"), (5, "V"), (4, "IV"), (1, "I")
    ]

    for val, sym in roman_map:
        while n >= val:
            s += sym
            n -= val

    return s

def roman_to_int(s):
    """Convert a Roman numeral string (potentially with T, A, M) to an integer. Matches JS toArabic."""
    if not isinstance(s, str) or not s or s.upper() == 'N': return 0
    original_s = s
    s = s.upper()
    n = 0

    roman_map = [ # Order matters for parsing
        ("MT", 9000), ("MA", 4000), ("CM", 900), ("CD", 400),
        ("XC", 90), ("XL", 40), ("IX", 9), ("IV", 4),
        ("T", 10000), ("A", 5000), ("M", 1000), ("D", 500),
        ("C", 100), ("L", 50), ("X", 10), ("V", 5), ("I", 1)
    ]

    for sym, val in roman_map:
        while s.startswith(sym):
             n += val
             s = s[len(sym):]

    if s: # If characters remain after parsing Roman, it's not a valid Roman numeral
        # Fallback: try converting original string to int
        try: return int(original_s)
        except ValueError: return 0
    return n


def generate_name():
    """Generate a random fantasy-style name using game RNG, matching JS logic."""
    name = ""
    # JS version uses 6 parts, alternating KParts[0], KParts[1], KParts[2]
    for i in range(6):
        name += pick(NAME_PARTS[i % 3])

    name = re.sub(r'^[^a-zA-Z]+', '', name) # Remove leading non-alpha
    name = re.sub(r'[^a-zA-Z]+$', '', name) # Remove trailing non-alpha

    if not name: return "Adventurer" # Fallback

    # Capitalize first letter only
    return name[0].upper() + name[1:].lower()


def calculate_level_up_time(level):
    """Calculate the total time (in seconds) needed to reach the *next* level. Matches JS LevelUpTime."""
    if level <= 0: level = 1 # Ensure level is at least 1 for calculation
    # 20 minutes base duration for level 1, exponential increase
    # Matches: Math.round((20 + Math.pow(1.15, level)) * 60)
    try:
        # Use level for exponent directly (JS uses `level` which means for *next* level)
        level_factor = math.pow(1.15, level)
    except OverflowError:
        level_factor = float('inf') # Handle very high levels

    return round((20.0 + level_factor) * 60.0) # Result in seconds


def rough_time(seconds_float):
    """Convert seconds (float) into a human-readable duration string. Matches JS RoughTime."""
    if not isinstance(seconds_float, (int, float)) or seconds_float < 0:
        return "???"
    seconds = int(seconds_float)
    if seconds < 120:
        return f"{seconds} seconds"
    elif seconds < 60 * 120: # 2 hours
        minutes = seconds // 60
        return f"{minutes} minutes"
    elif seconds < 60 * 60 * 48: # 2 days
        hours = seconds // 3600
        return f"{hours} hours"
    elif seconds < 60 * 60 * 24 * 60: # 60 days (~2 months)
        days = seconds // (3600 * 24)
        return f"{days} days"
    elif seconds < 60 * 60 * 24 * 30 * 24: # ~2 years
        months = seconds // (3600 * 24 * 30) # Approximate months
        return f"{months} months"
    else:
        years = seconds // (3600 * 24 * 365) # Approximate years
        return f"{years} years"

def get_current_timestamp_iso():
    """Returns the current timestamp in ISO 8601 format."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def get_current_timestamp_ms():
    """Returns the current timestamp in milliseconds since epoch."""
    return int(time.time() * 1000)

# END OF FILE: config_data.py