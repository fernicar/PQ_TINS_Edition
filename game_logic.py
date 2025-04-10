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
        self.task_type = "idle" # Initialize task type
        self.item_being_sold = None # Initialize item being sold

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

        # Always update UI to show smooth progress bar movement
        needs_ui_update = True

        if self.task_progress >= self.task_max:
            # --- Task Completion ---
            completed_task_type = self.task_description.split(" ")[0].lower() # e.g., "executing", "selling"
            is_productive_task = completed_task_type in ["executing", "exploring", "training"] # Tasks that grant XP etc.

            # 1. Resolve Task Effects (Loot, etc.)
            if completed_task_type == "executing" and self.current_target_monster:
                # Grant loot from monster
                loot_item_name = self.current_target_monster.get("loot")
                if loot_item_name and loot_item_name != '*':
                    item_base = f"{self.current_target_monster['name_mod']} {loot_item_name}"
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

    def get_state_for_saving(self):
        """Return a dictionary representing the current game state for saving to disk."""
        # For now, we'll use the same state as for UI updates, but this could be extended
        # to include additional data needed for saving/loading
        state = self.get_state()
        # Add any additional data needed for saving
        state["task_type"] = self.task_type
        state["item_being_sold"] = self.item_being_sold
        state["current_target_monster"] = self.current_target_monster
        state["last_tick_time"] = self.last_tick_time
        return state

    def apply_loaded_state(self, loaded_state):
        """Apply a loaded state to the game logic."""
        # Extract data from loaded_state and apply it to the current instance
        self.character = loaded_state["character"]
        self.plot_acts = loaded_state["plot_acts"]
        self.quests = loaded_state["quests"]
        self.task_description = loaded_state["task_description"]
        self.task_progress = loaded_state["task_progress"]
        self.task_max = loaded_state["task_max"]
        self.xp_progress = loaded_state["xp_progress"]
        self.xp_max = loaded_state["xp_max"]
        self.quest_description = loaded_state["quest_description"]
        self.quest_progress = loaded_state["quest_progress"]
        self.quest_max = loaded_state["quest_max"]
        self.plot_progress = loaded_state["plot_progress"]
        self.plot_max = loaded_state["plot_max"]
        self.encumbrance = loaded_state["encumbrance"]
        self.encumbrance_max = loaded_state["encumbrance_max"]

        # Handle additional data that might be in the saved state
        self.task_type = loaded_state.get("task_type", "idle")
        self.item_being_sold = loaded_state.get("item_being_sold", None)
        self.current_target_monster = loaded_state.get("current_target_monster", None)
        self.last_tick_time = loaded_state.get("last_tick_time", time.monotonic() * 1000)

        self.game_loaded = True