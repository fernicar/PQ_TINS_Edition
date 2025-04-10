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