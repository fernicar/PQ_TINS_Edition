# START OF FILE: game_logic.py
# File: game_logic.py
import time
import json
import math
import re
from config_data import * # Import all data and helper functions

from PySide6.QtCore import QObject, Signal

class GameLogic(QObject):
    # Signal emitted when UI needs refresh, includes a string describing the major change (optional)
    state_updated = Signal(str)

    def __init__(self):
        super().__init__()
        self.character = {}
        self.plot_acts = []
        self.quests = [] # List of quest description strings
        self.task_queue = [] # Queue for cinematic/scripted tasks
        self.game_loaded = False
        self.last_tick_time = 0
        self.paused = False # Start unpaused by default

        # Specific state variables matching JS 'game' object structure
        self.dna = [] # Seed state from character creation
        self.seed = [] # Current RNG state
        self.birthday = "" # ISO Timestamp string
        self.birthstamp = 0 # Milliseconds timestamp
        self.beststat = "" # e.g., "STR 15"
        self.task = "" # Internal task identifier, e.g., "kill|Orc|1|snout"
        self.tasks = 0 # Counter for completed tasks
        self.elapsed = 0 # Total elapsed game time in seconds
        self.bestequip = "" # Last equipped item name
        self.bestplot = "" # Current act name string
        self.bestquest = "" # Current quest description string
        self.questmonster = "" # Name of monster for exterminate/placate quests
        self.questmonsterindex = -1 # Index in MONSTERS list for quest monster
        self.kill = "" # Current task description displayed to user (TaskBar label)

        # Progress bar data (matching JS structure for saving)
        self.ExpBar = {"position": 0.0, "max": 1, "percent": 0, "remaining": 0, "time": "", "hint": ""}
        self.EncumBar = {"position": 0, "max": 1, "percent": 0, "remaining": 0, "time": "", "hint": ""}
        self.PlotBar = {"position": 0.0, "max": 1, "percent": 0, "remaining": 0, "time": "", "hint": ""}
        self.QuestBar = {"position": 0.0, "max": 1, "percent": 0, "remaining": 0, "time": "", "hint": ""}
        self.TaskBar = {"position": 0, "max": 1, "percent": 0, "remaining": 0, "time": "", "hint": ""}

        # Other state variables
        self.act = 0 # Current act number (0=Prologue, 1=Act I, etc.)
        self.saveName = "" # Character name used for saving

        self.reset_state() # Initialize with default empty state

    def reset_state(self):
        """Resets the game state to initial defaults (before character creation)."""
        # Character dictionary remains for internal logic convenience
        self.character = {
            "Name": "Adventurer",
            "Race": "Human",
            "Class": "Fighter",
            "Level": 0,
            "Stats": {"STR": 10, "CON": 10, "DEX": 10, "INT": 10, "WIS": 10, "CHA": 10, "HP Max": 10, "MP Max": 10, "seed":[], "best":""},
            "Equipment": {slot: "" for slot in EQUIPMENT_SLOTS},
            "Inventory": {"Gold": 0}, # Use "Gold" key like JS {ItemName: Quantity}
            "Spells": {}, # SpellName: RomanLevelString
        }
        # Web-like state variables
        self.dna = []
        self.seed = randseed() # Initialize with current RNG state
        self.birthday = ""
        self.birthstamp = 0
        self.beststat = ""
        self.task = ""
        self.tasks = 0
        self.elapsed = 0
        self.bestequip = ""
        self.act = 0
        self.bestplot = "Prologue"
        self.quests = [] # Store quest description strings
        self.questmonster = ""
        self.questmonsterindex = -1
        self.bestquest = ""
        self.kill = "Initializing..."

        # Reset progress bars
        self.ExpBar = {"position": 0.0, "max": calculate_level_up_time(1), "percent": 0, "remaining": calculate_level_up_time(1), "time": "", "hint": ""}
        self.EncumBar = {"position": 0, "max": BASE_ENCUMBRANCE + 10, "percent": 0, "remaining": BASE_ENCUMBRANCE + 10, "time": "", "hint": ""}
        self.PlotBar = {"position": 0.0, "max": 26, "percent": 0, "remaining": 26, "time": "", "hint": ""} # JS prologue max = 26s? Seems short. Let's use level 1 time. -> No, JS uses 26. Stick to JS.
        self.QuestBar = {"position": 0.0, "max": 1, "percent": 0, "remaining": 1, "time": "", "hint": ""} # No quest initially
        self.TaskBar = {"position": 0, "max": 1, "percent": 0, "remaining": 0, "time": "", "hint": ""}

        self.task_queue = [] # Clear task queue

        self.last_tick_time = time.monotonic() * 1000 # Milliseconds
        self.game_loaded = False # Flag to prevent ticks before ready

    def initialize_new_character(self, name, race, klass, stats_dict):
        """Set up the character after creation, matching JS `sold` function."""
        self.reset_state() # Start fresh

        # Store initial seed state as 'dna'
        self.dna = stats_dict.get("seed", [])
        # Set current seed state
        self.seed = stats_dict.get("seed", [])
        randseed(self.seed) # Ensure game RNG is set to the rolled seed

        # Populate character dictionary
        self.character["Name"] = name
        self.character["Race"] = race
        self.character["Class"] = klass
        self.character["Level"] = 1
        self.character["Stats"] = stats_dict.copy() # Includes STR-CHA, HPMax, MPMax, seed, best
        self.character["Equipment"] = {slot: "" for slot in EQUIPMENT_SLOTS}
        self.character["Equipment"]["Weapon"] = "Sharp Rock" # JS default
        self.character["Equipment"]["Hauberk"] = "-3 Burlap" # JS default
        self.character["Inventory"] = {"Gold": 0} # JS starts with Gold: 0
        self.character["Spells"] = {}

        # Populate web-like state variables
        self.saveName = name
        self.birthday = get_current_timestamp_iso()
        self.birthstamp = get_current_timestamp_ms()
        self.beststat = f"{stats_dict.get('best','???')} {stats_dict.get(stats_dict.get('best','STR'), '?')}"
        self.task = "" # Start with no specific internal task
        self.tasks = 0
        self.elapsed = 0
        self.bestequip = "Sharp Rock"
        self.act = 0
        self.bestplot = "Prologue"
        self.quests = []
        self.questmonster = ""
        self.questmonsterindex = -1
        self.bestquest = ""
        self.kill = "Loading...." # Initial task description

        # Setup progress bars based on initial stats
        self.ExpBar["max"] = calculate_level_up_time(1) # Time for level 2
        self.ExpBar["position"] = 0
        self.EncumBar["max"] = BASE_ENCUMBRANCE + self.character["Stats"].get("STR", 10)
        self.EncumBar["position"] = self.calculate_encumbrance()
        self.PlotBar["max"] = 26 # JS prologue duration
        self.PlotBar["position"] = 0
        self.QuestBar["max"] = 1 # No quest yet
        self.QuestBar["position"] = 0
        self.TaskBar["max"] = 2000 # Initial "Loading..." task duration from JS
        self.TaskBar["position"] = 0
        self._update_progress_bar_hints() # Calculate initial hints

        # Initial task queue (matches JS `sold` function)
        self.task_queue = [
            'task|10|Experiencing an enigmatic and foreboding night vision',
            "task|6|Much is revealed about that wise old bastard you'd underestimated",
            'task|6|A shocking series of events leaves you alone and bewildered, but resolute',
            'task|4|Drawing upon an unrealized reserve of determination, you set out on a long and dangerous journey',
            'plot|2|Loading....' # Triggers act completion check
        ]

        self.game_loaded = True
        self.last_tick_time = time.monotonic() * 1000 # Reset tick time
        print(f"Character Initialized: {self.character['Name']}")
        self.state_updated.emit("Character Created")
        self.dequeue_task() # Start the first task from the queue

    def tick(self):
        """Main game loop tick, following JS Timer1Timer logic."""
        if not self.game_loaded or self.paused:
            self.last_tick_time = time.monotonic() * 1000 # Update time but don't process
            return

        current_time = time.monotonic() * 1000
        elapsed_ms = current_time - self.last_tick_time
        # Clamp elapsed time (JS uses 100ms max, uses interval timer)
        # Python timer interval is TIMER_INTERVAL_MS (50ms)
        elapsed_ms = min(max(0, elapsed_ms), TIMER_INTERVAL_MS * 4) # Allow catching up a bit
        self.last_tick_time = current_time

        if elapsed_ms <= 0: return

        major_update_reason = None

        if self.TaskBar["position"] >= self.TaskBar["max"]:
            # --- Task Completion (JS TaskBar.done() is true) ---
            self.tasks += 1
            task_duration_seconds = self.TaskBar["max"] / 1000.0
            self.elapsed += task_duration_seconds

            # 1. Update Progress Bars based on *completed task duration*
            xp_gain = 0
            quest_gain = 0
            plot_gain = 0
            is_productive_task = self.task.startswith("kill|") or self.task.startswith("heading") or self.task.startswith("cinematic") # Define productive tasks

            if is_productive_task:
                xp_gain = task_duration_seconds
                quest_gain = task_duration_seconds
                plot_gain = task_duration_seconds

            # Update XP
            if xp_gain > 0:
                 if self.ExpBar["position"] + xp_gain >= self.ExpBar["max"]:
                     self.level_up() # Handles XP reset and gain application
                     major_update_reason = "Level Up"
                 else:
                     self.ExpBar["position"] += xp_gain

            # Update Quest
            if quest_gain > 0 and self.act >= 1: # Quests start after prologue
                 if self.QuestBar["position"] + quest_gain >= self.QuestBar["max"] or not self.quests:
                     self.complete_quest() # Handles progress reset and reward
                     major_update_reason = "Quest Complete"
                 else:
                     self.QuestBar["position"] += quest_gain

            # Update Plot
            if plot_gain > 0 or self.act == 0: # Prologue always advances
                 if self.PlotBar["position"] + plot_gain >= self.PlotBar["max"]:
                     # Trigger cinematic queue before advancing act
                     self.interplot_cinematic()
                     major_update_reason = "Act Transition"
                     # Note: complete_act() is now triggered by the 'plot|...' task from interplot_cinematic
                 else:
                     self.PlotBar["position"] += plot_gain

            # 2. Resolve Specific Task Effects (after progress updates)
            if self.task.startswith('kill|'):
                monster_parts = self.task.split('|')
                if len(monster_parts) > 3:
                    loot_type = monster_parts[3]
                    if loot_type == '*':
                        self.win_item() # Generic win
                    elif loot_type:
                        monster_name = monster_parts[1]
                        # Add specific loot (lowercase name + ProperCase loot)
                        item_name = f"{monster_name.lower()} {loot_type[0].upper() + loot_type[1:]}"
                        self.add_inventory_item(item_name, 1)
            elif self.task == 'buying':
                cost = self.calculate_equip_price()
                if self.character["Inventory"].get("Gold", 0) >= cost:
                    self.add_inventory_item("Gold", -cost)
                    print(f"Spent {cost} gold on equipment.")
                    self.win_equip() # Grant the equipment
                    major_update_reason = "Equipment Bought"
                else:
                    print("Could not afford new equipment.")
            elif self.task == 'sell':
                item_to_sell = self.get_sellable_item_name()
                if item_to_sell:
                    qty = self.character["Inventory"].get(item_to_sell, 0)
                    if qty > 0:
                         # Calculate sale price (matches JS)
                         base_value = 1 # Assume base value 1 unless special
                         level = self.character.get("Level", 1)
                         amt = qty * level
                         if " of " in item_to_sell: # JS check for special item
                              amt *= (1 + Random(level)) * (1 + Random(10)) # Approximation of JS RandomLow

                         # Remove *one* item being sold, even if qty > 1
                         self.add_inventory_item(item_to_sell, -1)
                         self.add_inventory_item("Gold", max(1, amt)) # Ensure at least 1 gold
                         major_update_reason = "Item Sold"
            # No specific action for 'market' completion, it transitions in dequeue_task
            # No specific action for 'heading' completion

            # 3. Dequeue and Set Next Task
            self.dequeue_task() # Determines and sets the next task

        else:
            # --- Task In Progress ---
            self.TaskBar["position"] += elapsed_ms

        # --- Update UI ---
        # Update progress bar hints/display values
        self._update_progress_bar_hints()
        # Emit signal for UI refresh
        self.state_updated.emit(major_update_reason or "Tick")

    def _update_progress_bar_hints(self):
        """Recalculate bar percentages and hint text."""
        for bar_name, bar_data in [("ExpBar", self.ExpBar), ("EncumBar", self.EncumBar),
                                   ("PlotBar", self.PlotBar), ("QuestBar", self.QuestBar),
                                   ("TaskBar", self.TaskBar)]:
            max_val = bar_data["max"]
            pos_val = bar_data["position"]
            safe_max = max(1e-9, max_val) # Avoid division by zero but allow float max

            bar_data["percent"] = int((pos_val / safe_max) * 100)
            bar_data["remaining"] = max_val - pos_val

            # Update specific hint text based on JS templates
            if bar_name == "ExpBar":
                bar_data["hint"] = f"{int(bar_data['remaining']):,} XP needed for next level"
            elif bar_name == "EncumBar":
                 # Recalculate encumbrance position just before update
                 bar_data["position"] = self.calculate_encumbrance()
                 bar_data["hint"] = f"{bar_data['position']}/{bar_data['max']} cubits"
            elif bar_name == "PlotBar":
                 bar_data["time"] = rough_time(max(0, bar_data["remaining"]))
                 bar_data["hint"] = f"{bar_data['time']} remaining"
            elif bar_name == "QuestBar":
                 bar_data["hint"] = f"{bar_data['percent']}% complete"
            elif bar_name == "TaskBar":
                 bar_data["time"] = rough_time(max(0, bar_data["remaining"] / 1000)) # Task time remaining
                 bar_data["hint"] = f"{bar_data['percent']}%" # JS TaskBar hint is just percent

    def set_new_task(self, description, duration_ms, internal_task_id=""):
        """Sets the current task description, duration, and internal ID. Matches JS Task()."""
        self.kill = description + "..." # User-facing description
        self.TaskBar["max"] = max(100, duration_ms) # Ensure minimum duration
        self.TaskBar["position"] = 0
        self.task = internal_task_id if internal_task_id else "generic" # Internal identifier
        print(f"New Task [{self.task}]: {self.kill} ({self.TaskBar['max']/1000:.1f}s)")
        # Log(self.kill) # TODO: Implement proper logging if needed

    def dequeue_task(self):
        """Handles task queue and determines next action, mimicking JS Dequeue()."""
        # Check queue first
        if self.task_queue:
            task_str = self.task_queue.pop(0)
            parts = task_str.split('|')
            command = parts[0]
            param1 = int(parts[1]) if len(parts) > 1 else 0
            param2 = parts[2] if len(parts) > 2 else ""

            if command == 'task':
                self.set_new_task(param2, param1 * 1000, internal_task_id="cinematic") # Mark queued tasks as cinematic
            elif command == 'plot':
                # This task triggers the actual act completion logic
                self.complete_act()
                act_name = self.bestplot if self.bestplot else f"Act {int_to_roman(self.act)}"
                self.set_new_task(f"Loading {act_name}", param1 * 1000, internal_task_id="plot_load")
            else:
                print(f"Warning: Unknown queue command '{command}'")
                self.determine_next_task_action() # Fallback to normal logic
            return # Task set from queue

        # If queue is empty, determine next action based on state (JS Dequeue logic)
        self.determine_next_task_action()

    def determine_next_task_action(self):
        """Decides the next action when the task queue is empty."""
        encumbrance = self.calculate_encumbrance()
        self.EncumBar["position"] = encumbrance # Update bar position data

        # Check if encumbered (and not already heading to/at market/selling)
        if encumbrance >= self.EncumBar["max"] and self.task not in ['market', 'sell', 'heading_market']:
            self.set_new_task("Heading to market to sell loot", 4 * 1000, "heading_market")
        # Check if just arrived at market
        elif self.task == 'heading_market':
             item_to_sell = self.get_sellable_item_name()
             if item_to_sell:
                  self.set_new_task(f"Selling {indefinite(item_to_sell, 1)}", 1 * 1000, "sell")
             else: # No items to sell
                  self.set_new_task("Leaving market", 2 * 1000, "heading_fields")
        # Check if finished selling an item
        elif self.task == 'sell':
             item_to_sell = self.get_sellable_item_name()
             if item_to_sell: # Sell next item
                  self.set_new_task(f"Selling {indefinite(item_to_sell, 1)}", 1 * 1000, "sell")
             else: # Finished selling all items
                  # Decide whether to buy equipment
                  if self.character["Inventory"].get("Gold", 0) > self.calculate_equip_price():
                       self.set_new_task("Negotiating purchase of better equipment", 5 * 1000, "buying")
                  else: # Cannot afford, leave market
                       self.set_new_task("Leaving market", 2 * 1000, "heading_fields")
        # Check if finished buying or couldn't afford/didn't buy after selling
        elif self.task in ['buying', 'leaving_market']:
              self.set_new_task("Heading to the killing fields", 4 * 1000, "heading_fields")
        # Spontaneous decision to buy if rich (lower chance than JS odds(1,8)?)
        elif self.character["Inventory"].get("Gold", 0) > self.calculate_equip_price() * 1.5 and odds(1, 20):
             self.set_new_task("Negotiating purchase of better equipment", 5 * 1000, "buying")
        # Default: Go fight something
        else:
             # If previous task wasn't combat-related, add travel time
             if not self.task.startswith("kill|") and self.task != "heading_fields":
                 self.set_new_task("Heading to the killing fields", 4 * 1000, "heading_fields")
             else: # Already in the fields or just finished fighting/traveling
                 self.generate_monster_encounter_task()

    def get_sellable_item_name(self):
        """Finds the name of the first sellable item (not Gold)."""
        for name, qty in self.character.get("Inventory", {}).items():
            if name != "Gold" and qty > 0:
                return name
        return None

    def level_up(self):
        """Handle level up logic, matches JS LevelUp."""
        self.ExpBar["position"] = (self.ExpBar["position"] - self.ExpBar["max"]) # Rollover XP
        self.character["Level"] += 1
        print(f"LEVEL UP! Reached Level {self.character['Level']}")

        # Update HP/MP Max
        con_bonus = self.character["Stats"].get("CON", 0) // 6
        int_bonus = self.character["Stats"].get("INT", 0) // 6
        # Random(4) gives 0-3, add 1 to match JS 1+Random(4)
        hp_gain = max(1, Random(4) + 1 + con_bonus)
        mp_gain = max(1, Random(4) + 1 + int_bonus)
        self.character["Stats"]["HP Max"] = self.character["Stats"].get("HP Max", 0) + hp_gain
        self.character["Stats"]["MP Max"] = self.character["Stats"].get("MP Max", 0) + mp_gain

        # Grant stat points (JS gives 2 points)
        self.win_stat()
        self.win_stat()

        # Learn a new spell
        self.win_spell()

        # Reset XP bar for next level
        self.ExpBar["max"] = calculate_level_up_time(self.character["Level"]) # Pass current level
        self.ExpBar["position"] = max(0, self.ExpBar["position"]) # Ensure position isn't negative

        # Update Encumbrance Max based on potentially increased STR
        self.EncumBar["max"] = BASE_ENCUMBRANCE + self.character["Stats"].get("STR", 10)
        self._update_progress_bar_hints() # Update hints immediately

        # Update best stat string
        self.update_best_stat()

        # Brag('l') # Skip online features

    def win_stat(self):
        """Increase a random stat, biased towards the best stat. Matches JS WinStat."""
        stat_to_increase = ""
        if odds(1, 2): # 50% chance for any stat (including HP/MP Max)
            stat_to_increase = pick(list(self.character["Stats"].keys() - {"seed", "best"})) # Exclude non-numeric stats
        else:
            # Favor the best stat (JS uses sum of squares)
            prime_stats = ["STR", "CON", "DEX", "INT", "WIS", "CHA"]
            total_squares = sum(self.character["Stats"].get(s, 0)**2 for s in prime_stats)
            if total_squares <= 0: # Handle edge case where all stats are 0
                 stat_to_increase = pick(prime_stats)
            else:
                 roll = Random(total_squares)
                 current_sum = 0
                 for stat_name in prime_stats:
                      current_sum += self.character["Stats"].get(stat_name, 0)**2
                      if roll < current_sum:
                           stat_to_increase = stat_name
                           break
                 if not stat_to_increase: # Should not happen if total_squares > 0
                      stat_to_increase = pick(prime_stats)

        if stat_to_increase:
             self.character["Stats"][stat_to_increase] = self.character["Stats"].get(stat_to_increase, 0) + 1
             print(f"Stat Increased: {stat_to_increase} to {self.character['Stats'][stat_to_increase]}")
             if stat_to_increase == "STR": # Update encumbrance max if STR changes
                 self.EncumBar["max"] = BASE_ENCUMBRANCE + self.character["Stats"]["STR"]
             # Update best stat string after any stat change
             self.update_best_stat()

    def update_best_stat(self):
        """Recalculates and updates the best stat string."""
        best_val = -1
        best_name = ""
        prime_stats = ["STR", "CON", "DEX", "INT", "WIS", "CHA"]
        for stat_name in prime_stats:
             val = self.character["Stats"].get(stat_name, 0)
             if val >= best_val: # JS logic takes the last one in case of tie
                  best_val = val
                  best_name = stat_name
        self.character["Stats"]["best"] = best_name
        self.beststat = f"{best_name} {best_val}"


    def win_spell(self):
         """Try to learn a new spell based on WIS and Level. Matches JS WinSpell."""
         # Eligible spell index limit based on WIS + Level
         max_spell_index = self.character["Stats"].get("WIS", 0) + self.character.get("Level", 1)
         eligible_spells = [(i, s) for i, s in enumerate(SPELLS)
                            if s not in self.character["Spells"] and i < max_spell_index]

         if eligible_spells:
             # PickLow equivalent: choose from eligible spells, biasing towards lower index
             idx1 = Random(len(eligible_spells))
             idx2 = Random(len(eligible_spells))
             chosen_index, new_spell = eligible_spells[min(idx1, idx2)]

             # Calculate spell level (starts at I, increases slowly)
             spell_level_int = 1 + (self.character["Level"] // 7) # Integer division gives floor
             spell_level_roman = int_to_roman(spell_level_int)

             self.character["Spells"][new_spell] = spell_level_roman
             print(f"Learned Spell: {new_spell} {spell_level_roman}")
             # Update bestspell? JS does this in SaveGame via HotOrNot
             self.update_best_spell() # Do it immediately


    def update_best_spell(self):
        """Recalculates and updates the best spell string."""
        best_spell_name = ""
        best_spell_rank = -1 # Use a numerical rank for comparison
        flat = 1 # JS flattening constant

        spell_indices = {name: i for i, name in enumerate(SPELLS)}

        for name, level_roman in self.character.get("Spells", {}).items():
            level_int = roman_to_int(level_roman)
            index = spell_indices.get(name, -1)
            if index != -1:
                # JS comparison: (i+flat) * level > (best+flat) * best_level
                rank = (index + flat) * level_int
                if rank > best_spell_rank:
                    best_spell_rank = rank
                    best_spell_name = f"{name} {level_roman}"

        self.bestspell = best_spell_name if best_spell_name else ""

    def complete_quest(self):
        """Handles quest completion and assignment. Matches JS CompleteQuest."""
        # Reset quest bar (JS: 50 + Random(100) seconds -> 50k-150k ms)
        self.QuestBar["max"] = (50 + Random(100)) * 1000
        self.QuestBar["position"] = 0

        if self.quests: # If there was a previous quest
            print(f"Quest Complete: {self.bestquest}")
            # Grant reward (JS uses Random(4))
            reward_type = Random(4)
            print("Quest Reward: ", end="")
            if reward_type == 0:
                self.win_spell()
                print("Spell!")
            elif reward_type == 1:
                self.win_equip()
                print("Equipment!")
            elif reward_type == 2:
                self.win_stat()
                print("Stat!")
            elif reward_type == 3:
                self.win_item(force_special=True) # JS WinItem doesn't force special here, but Python version did. Let's keep it interesting.
                print("Item!")
        else:
            print("No active quest to complete, assigning first quest.") # Should only happen at start

        # Assign new quest
        while len(self.quests) > 99: # Keep list size manageable (JS check)
            self.quests.pop(0)

        self.questmonster = "" # Reset quest monster flag
        self.questmonsterindex = -1

        quest_type = Random(5)
        new_quest_desc = "ERROR: Quest Gen Failed"
        char_level = self.character.get("Level", 1)

        try:
            if quest_type == 0: # Exterminate
                # Select monster near level (JS picks 1 from 5 closest)
                candidates = sorted(enumerate(MONSTERS), key=lambda m_idx: abs(m_idx[1][1] - char_level))
                num_closest = min(len(candidates), 5)
                if num_closest > 0:
                     chosen_index, chosen_monster_tuple = pick(candidates[:num_closest])
                     self.questmonsterindex = chosen_index # Store index
                     self.questmonster = chosen_monster_tuple[0] # Store original name
                     # JS uses definite plural for description
                     new_quest_desc = f"Exterminate {definite(self.questmonster, 2)}"
                else: new_quest_desc = "Find something to exterminate"

            elif quest_type == 1: # Seek Item
                item_name = self.generate_random_loot(force_special=True)
                new_quest_desc = f"Seek {definite(item_name, 1)}"

            elif quest_type == 2: # Deliver Item (JS uses BoringItem)
                item_name = pick(BORING_ITEMS) or "a Rock"
                new_quest_desc = f"Deliver this {item_name}"

            elif quest_type == 3: # Fetch Item (JS uses BoringItem)
                item_name = pick(BORING_ITEMS) or "a Twig"
                new_quest_desc = f"Fetch me {indefinite(item_name, 1)}"

            elif quest_type == 4: # Placate
                 # Select monster near level (JS picks 1 from 3 closest) - different from exterminate
                 candidates = sorted(enumerate(MONSTERS), key=lambda m_idx: abs(m_idx[1][1] - char_level))
                 num_closest = min(len(candidates), 3) # Only 3 closest for placate
                 if num_closest > 0:
                     chosen_index, chosen_monster_tuple = pick(candidates[:num_closest])
                     # Don't set questmonsterindex or questmonster for placate in JS logic
                     # self.questmonsterindex = chosen_index
                     # self.questmonster = chosen_monster_tuple[0]
                     monster_name_for_desc = chosen_monster_tuple[0]
                     new_quest_desc = f"Placate {definite(monster_name_for_desc, 2)}"
                 else: new_quest_desc = "Find someone to placate"

        except Exception as e:
            print(f"Error generating quest: {e}")
            new_quest_desc = "Do something heroic"

        self.quests.append(new_quest_desc)
        self.bestquest = new_quest_desc # Update best quest string
        print(f"New Quest: {self.bestquest}")
        # SaveGame() # JS saves after quest completion


    def interplot_cinematic(self):
        """Queue cinematic tasks before act completion. Matches JS InterplotCinematic."""
        choice = Random(3)
        if choice == 0:
            self.task_queue.extend([
                'task|1|Exhausted, you arrive at a friendly oasis in a hostile land',
                'task|2|You greet old friends and meet new allies',
                'task|2|You are privy to a council of powerful do-gooders',
                'task|1|There is much to be done. You are chosen!',
                'plot|1|Loading....' # Triggers complete_act()
            ])
        elif choice == 1:
            nemesis_level = self.character.get("Level", 1) + 3
            nemesis_name = self.generate_named_monster(nemesis_level)
            self.task_queue.append(f'task|1|Your quarry is in sight, but a mighty enemy bars your path! ({nemesis_name})')
            self.task_queue.append(f'task|4|A desperate struggle commences with {nemesis_name}')
            s = Random(3)
            num_struggles = Random(1 + self.act + 1) # 1 to act+1 struggles
            for _ in range(num_struggles):
                s = (s + 1 + Random(2)) % 3
                if s == 0: desc = f'Locked in grim combat with {nemesis_name}'
                elif s == 1: desc = f'{nemesis_name} seems to have the upper hand'
                else: desc = f'You seem to gain the advantage over {nemesis_name}'
                self.task_queue.append(f'task|2|{desc}')
            self.task_queue.extend([
                f'task|3|Victory! {nemesis_name} is slain! Exhausted, you lose consciousness',
                'task|2|You awake in a friendly place, but the road awaits',
                'plot|1|Loading....' # Triggers complete_act()
            ])
        elif choice == 2:
             nemesis2_name = self.generate_impressive_guy()
             self.task_queue.extend([
                 f"task|2|Oh sweet relief! You've reached the kind protection of {nemesis2_name}",
                 f'task|3|There is rejoicing, and an unnerving encounter with {nemesis2_name} in private',
                 f'task|2|You forget your {pick(BORING_ITEMS)} and go back to get it',
                 "task|2|What's this!? You overhear something shocking!",
                 f'task|2|Could {nemesis2_name} be a dirty double-dealer?',
                 'task|3|Who can possibly be trusted with this news!? -- Oh yes, of course',
                 'plot|1|Loading....' # Triggers complete_act()
             ])

    def complete_act(self):
        """Handles act completion. Matches JS CompleteAct."""
        print(f"Act Complete: {self.bestplot}")
        self.act += 1
        # JS uses 60*60*(1+5*Act) seconds for plot duration
        self.PlotBar["max"] = 60 * 60 * (1 + 5 * self.act)
        self.PlotBar["position"] = 0
        self.bestplot = f"Act {int_to_roman(self.act)}" # Update best plot string

        # Grant rewards (JS gives item and equip after Act 1)
        if self.act > 1:
            self.win_item()
            self.win_equip()
        # Brag('a') # Skip online

    def generate_monster_encounter_task(self):
        """Generate a monster encounter and set it as the current task. Matches JS MonsterTask."""
        char_level = self.character.get("Level", 1)
        target_level = char_level
        # Adjust target level randomly (JS logic)
        for _ in range(target_level): # Loop 'level' times
             if odds(2, 5):
                 target_level += rand_sign()
        target_level = max(1, target_level) # Ensure level is at least 1

        monster_tuple = None
        monster_index = -1
        monster_name = ""
        base_monster_level = 0
        loot = "*"
        is_npc = False
        definite_article = False # Flag for specific named NPCs

        # Use quest monster sometimes (JS odds(1,4))
        if self.questmonster and odds(1, 4):
            monster_index = self.questmonsterindex
            if 0 <= monster_index < len(MONSTERS):
                monster_tuple = MONSTERS[monster_index]
                monster_name = monster_tuple[0]
                base_monster_level = monster_tuple[1]
                loot = monster_tuple[2]
            else:
                 print(f"Warning: Invalid questmonsterindex {monster_index}")
                 self.questmonster = "" # Clear invalid quest monster
                 self.questmonsterindex = -1

        # Use NPC sometimes (JS odds(1,25))
        elif odds(1, 25):
            is_npc = True
            base_monster_level = target_level # NPC level matches target level
            race_name = pick(list(RACES.keys()))
            if odds(1, 2):
                klass_name = pick(list(KLASSES.keys()))
                monster_name = f"passing {race_name} {klass_name}"
            else:
                # Generate a named NPC
                title = pick_low(TITLES) # Bias towards lower titles
                npc_name = generate_name()
                monster_name = f"{title} {npc_name} the {race_name}"
                definite_article = True
            loot = "*" # NPCs drop generic loot

        # Pick a standard monster based on level proximity
        if not monster_tuple and not is_npc:
            candidates = sorted(enumerate(MONSTERS), key=lambda m_idx: abs(m_idx[1][1] - target_level))
            num_closest = min(len(candidates), 5) # JS checks 5
            if num_closest > 0:
                chosen_index, monster_tuple = pick(candidates[:num_closest])
                monster_name = monster_tuple[0]
                base_monster_level = monster_tuple[1]
                loot = monster_tuple[2]
            else: # Fallback if MONSTERS is empty or filtering fails
                 print("Error: Could not select a monster!")
                 self.set_new_task("Looking for trouble", 3*1000, "exploring") # Fallback task
                 return

        # Apply Monster Modifiers (based on level difference)
        level_diff = target_level - base_monster_level
        modified_monster_name = monster_name # Start with base name
        effective_monster_level = base_monster_level

        # Logic mirroring JS Sick/Young/Big/Special prefixes using MONSTER_MODS
        mod_prefix = ""
        mod_suffix = ""
        mod_applied = False

        if level_diff <= -10:
            modified_monster_name = "imaginary " + monster_name
            mod_applied = True
            # Effective level likely 0 for imaginary, but let's keep base for duration calc?
            # JS doesn't explicitly change level for imaginary.
        elif -10 < level_diff < 0:
            # Apply Sick or Young modifier (JS picks randomly)
            mod_choice = Random(2)
            if mod_choice == 0 : # Apply Sick (using MONSTER_MODS logic)
                # Find appropriate negative mod
                possible_mods = [m for m in MONSTER_MODS if m[0] < 0 and abs(m[0]) <= abs(level_diff)]
                if possible_mods:
                     mod = pick(possible_mods)
                     mod_pattern = mod[1]
                     effective_monster_level += mod[0]
                     modified_monster_name = mod_pattern.replace("*", monster_name)
                     mod_applied = True
                     # print(f"Applied Sick Mod: {mod}, LevelDiff: {level_diff}")
            else: # Apply Young
                 possible_mods = [m for m in MONSTER_MODS if m[0] < 0 and abs(m[0]) <= abs(level_diff)]
                 if possible_mods:
                     mod = pick(possible_mods)
                     mod_pattern = mod[1]
                     effective_monster_level += mod[0]
                     modified_monster_name = mod_pattern.replace("*", monster_name) # JS uses specific Young() func, reuse mods here.
                     mod_applied = True
                     # print(f"Applied Young Mod: {mod}, LevelDiff: {level_diff}")

        elif level_diff >= 10:
            modified_monster_name = "messianic " + monster_name
            mod_applied = True
            # JS doesn't explicitly change level for messianic
        elif 0 < level_diff < 10:
            # Apply Big or Special modifier (JS picks randomly)
            mod_choice = Random(2)
            if mod_choice == 0 : # Apply Big
                possible_mods = [m for m in MONSTER_MODS if m[0] > 0 and m[0] <= level_diff]
                if possible_mods:
                     mod = pick(possible_mods)
                     mod_pattern = mod[1]
                     effective_monster_level += mod[0]
                     modified_monster_name = mod_pattern.replace("*", monster_name)
                     mod_applied = True
                     # print(f"Applied Big Mod: {mod}, LevelDiff: {level_diff}")
            else: # Apply Special
                 possible_mods = [m for m in MONSTER_MODS if m[0] > 0 and m[0] <= level_diff]
                 if possible_mods:
                     mod = pick(possible_mods)
                     mod_pattern = mod[1]
                     effective_monster_level += mod[0]
                     modified_monster_name = mod_pattern.replace("*", monster_name)
                     mod_applied = True
                     # print(f"Applied Special Mod: {mod}, LevelDiff: {level_diff}")

        effective_monster_level = max(0, effective_monster_level) # Ensure non-negative

        # Determine Quantity (JS logic)
        qty = 1
        if level_diff > 10 and effective_monster_level > 0: # Significantly stronger character
             qty = math.floor((target_level + Random(effective_monster_level)) / effective_monster_level)
             qty = max(1, qty)
             # Recalculate effective level per monster if qty > 1? JS seems to use original target_level.
             # Let's recalculate for duration scaling:
             # effective_monster_level = max(1, target_level // qty) # ??? This seems off. JS logic is murky here.
             # Stick closer to JS: keep effective_monster_level as modified base level.
             # total_encounter_level = effective_monster_level * qty # For duration scaling

        # Format description string
        if definite_article: # Specific named NPC
             task_desc_monster = modified_monster_name
        else:
             task_desc_monster = indefinite(modified_monster_name, qty)


        # Calculate Task Duration (JS uses 2 * InvLabel * Level * 1000 / CharLevel)
        # InvLabel seems to be 3? Let's use a base time + scaling
        # Base duration relative to character level (e.g., 5 seconds per level?)
        base_duration_per_level = 3000 # 3 seconds
        # Scale based on relative level difference
        # Use total encounter level? Let's use modified level * qty
        total_encounter_level = max(1, effective_monster_level * qty)
        relative_difficulty = total_encounter_level / max(1, char_level)
        # Dampen the scaling factor
        scale_factor = math.pow(relative_difficulty, 0.6) if relative_difficulty > 0 else 1
        import random
        duration_ms = int((base_duration_per_level * scale_factor * random.uniform(0.8, 1.2)))
        duration_ms = max(1000, min(duration_ms, 120 * 1000)) # Clamp 1s to 120s


        # Set Task
        self.task = f"kill|{monster_name}|{base_monster_level}|{loot}" # Store original info
        # Store modified info for potential later use (e.g., display)
        self.character["current_monster_info"] = {
            "name_orig": monster_name,
            "name_mod": modified_monster_name, # The name with prefixes/suffixes
            "level_eff": effective_monster_level,
            "quantity": qty
        }
        self.set_new_task(f"Executing {task_desc_monster}", duration_ms, self.task)

    def generate_named_monster(self, level):
        """Generates a named monster string for cinematics. Matches JS NamedMonster."""
        # Find closest monster name
        candidates = sorted(MONSTERS, key=lambda m: abs(m[1] - level))
        if not candidates: return "a Grue"
        base_name = candidates[0][0]
        return f"{generate_name()} the {base_name}"

    def generate_impressive_guy(self):
        """Generates an impressive NPC name string. Matches JS ImpressiveGuy."""
        if Random(2) == 0:
            # Title of the Plural Race
            title = pick(IMPRESSIVE_TITLES)
            race = pick(list(RACES.keys()))
            return f"the {title} of the {plural(race)}"
        else:
             # Title Name of Place
             title = pick(IMPRESSIVE_TITLES)
             name = generate_name()
             place = generate_name()
             return f"{title} {name} of {place}"

    def win_equip(self):
        """Generate and equip a new item. Matches JS WinEquip."""
        slot_index = Random(len(EQUIPMENT_SLOTS))
        slot_name = EQUIPMENT_SLOTS[slot_index]

        char_level = self.character.get("Level", 1)
        base_items = []
        good_mods, bad_mods = [], []

        # Select appropriate item lists based on slot (JS logic)
        if slot_index == 0: # Weapon
            base_items, good_mods, bad_mods = WEAPONS, OFFENSE_ATTRIB, OFFENSE_BAD
        elif slot_index == 1: # Shield
             base_items, good_mods, bad_mods = SHIELDS, DEFENSE_ATTRIB, DEFENSE_BAD
        else: # Other Armor slots
             base_items, good_mods, bad_mods = ARMORS, DEFENSE_ATTRIB, DEFENSE_BAD

        if not base_items:
             print(f"Warning: No base items defined for slot '{slot_name}'")
             return

        # --- Select Base Item --- (JS LPick logic: pick 1 from 5 closest)
        sorted_bases = sorted(base_items, key=lambda item: abs(item[1] - char_level))
        candidates = sorted_bases[:min(len(sorted_bases), 5)]
        if not candidates: candidates = base_items # Fallback
        base_item_tuple = pick(candidates)

        item_name = base_item_tuple[0]
        base_value = base_item_tuple[1]

        # --- Apply Modifiers --- (JS logic)
        level_diff = char_level - base_value # This is 'plus' in JS
        mods_to_use = good_mods if level_diff >= 0 else bad_mods # Use good if diff is 0 too
        mod_count = 0
        max_mods = 2
        applied_mod_names = []

        temp_level_diff = level_diff # Work with temp diff

        while mod_count < max_mods and temp_level_diff != 0:
             # Find mods that fit (absolute value <= remaining diff, and sign matches)
             possible_mods = []
             for mod_name, mod_value in mods_to_use:
                  # Check sign match: both pos, both neg, or mod_value is 0
                  sign_match = (mod_value >= 0 and temp_level_diff >= 0) or (mod_value <= 0 and temp_level_diff <= 0)
                  if abs(mod_value) <= abs(temp_level_diff) and sign_match and mod_name not in applied_mod_names:
                       possible_mods.append((mod_name, mod_value))

             if not possible_mods: break # No suitable mods left

             mod_tuple = pick(possible_mods)
             mod_name, mod_value = mod_tuple

             item_name = f"{mod_name} {item_name}"
             applied_mod_names.append(mod_name)
             temp_level_diff -= mod_value
             mod_count += 1

        # Add numeric prefix if difference still remains
        final_diff = temp_level_diff # Remaining difference
        if final_diff != 0:
             prefix = f"+{final_diff}" if final_diff > 0 else str(final_diff)
             item_name = f"{prefix} {item_name}"

        # --- Equip Item ---
        self.character["Equipment"][slot_name] = item_name
        self.bestequip = item_name # Update best equip tracker
        if slot_index > 0: # JS adds slot name for non-weapons
             self.bestequip += f" {slot_name}"
        print(f"Equipped: {item_name} in slot {slot_name}")
        # Update bestequip string
        self.update_best_equip(slot_name, item_name)

    def update_best_equip(self, slot_name, item_name):
        """Updates the bestequip string."""
        self.bestequip = item_name
        # JS adds slot name for non-weapons - find index
        if slot_name != EQUIPMENT_SLOTS[0]:
             self.bestequip += f" {slot_name}"


    def generate_random_loot(self, force_special=False):
        """Generate a random boring or special item name. Matches JS SpecialItem/InterestingItem/BoringItem."""
        if force_special or odds(1, 5): # Force or 1 in 5 chance for special
             attrib = pick(ITEM_ATTRIB) or "Plain"
             special = pick(SPECIALS) or "Thingy"
             of_part = pick(ITEM_OFS) or "Average"
             return f"{attrib} {special} of {of_part}"
        else:
             return pick(BORING_ITEMS) or "Chunk of Dirt"

    def win_item(self, force_special=False):
         """Adds a random item to inventory, potentially favoring existing items. JS WinItem logic."""
         # JS logic: If inv length > Random(999), add existing item, else add new special item.
         if len(self.character["Inventory"]) > 1 and Random(999) < len(self.character["Inventory"]) -1 : # Exclude Gold count
             # Pick an existing item (excluding Gold)
             existing_items = [name for name in self.character["Inventory"] if name != "Gold"]
             if existing_items:
                 item_to_add = pick(existing_items)
                 self.add_inventory_item(item_to_add, 1)
             else: # Fallback if only Gold exists
                 item_to_add = self.generate_random_loot(force_special=True)
                 self.add_inventory_item(item_to_add, 1)
         else:
             # Add a new special item
             item_to_add = self.generate_random_loot(force_special=True)
             self.add_inventory_item(item_to_add, 1)


    def add_inventory_item(self, item_name, quantity=1):
        """Add or remove an item from the inventory, updating gold separately."""
        if not item_name: return

        # Use "Gold" key consistent with JS save format
        target_name = "Gold" if item_name == "Gold Piece" else item_name

        # Update Inventory dictionary
        current_qty = self.character["Inventory"].get(target_name, 0)
        new_qty = max(0, current_qty + quantity)

        log_action = "Added" if quantity > 0 else "Removed"
        log_qty = abs(quantity)

        if new_qty > 0:
            self.character["Inventory"][target_name] = new_qty
            # Only log if quantity actually changed or item was added
            if new_qty != current_qty:
                 print(f"Inventory: {log_action} {log_qty}x {target_name} (now {new_qty})")
        elif target_name in self.character["Inventory"]: # Remove if quantity drops to 0 or less
             del self.character["Inventory"][target_name]
             print(f"Inventory: Removed {log_qty}x {target_name} (now 0)")

        # Update Encumbrance Bar position immediately after inventory change
        self.EncumBar["position"] = self.calculate_encumbrance()
        self._update_progress_bar_hints() # Update hints

    def calculate_encumbrance(self):
        """Calculate current encumbrance based on inventory item count (excluding gold)."""
        total_items = 0
        # Ensure inventory exists and is iterable
        inventory = self.character.get("Inventory", {})
        if isinstance(inventory, dict):
            for name, qty in inventory.items():
                if name != "Gold": # Check against "Gold" key
                    total_items += qty
        return total_items

    def set_paused(self, paused):
        """Set the game's paused state."""
        if self.paused != paused:
            self.paused = paused
            self.state_updated.emit("Pause State Changed")
            print(f"Game {'paused' if paused else 'resumed'}")

    def is_paused(self):
        """Return whether the game is currently paused."""
        return self.paused

    def calculate_equip_price(self):
        """Calculate the cost of buying new equipment based on level. Matches JS EquipPrice."""
        level = self.character.get("Level", 1)
        if level <= 0: level = 1
        return 5 * level * level + 10 * level + 20

    # --- Getters for UI ---
    def get_state(self):
        """Return a dictionary representing the current game state for UI updates."""
        # This dictionary structure is simplified for the UI needs.
        # It draws data from the internal `character` dict and the web-like state variables.
        return {
            "character": self.character, # Keep sending this for ease of access in UI
            "plot_acts": self.plot_acts,
            "quests": self.quests, # List of strings
            "task_description": self.kill, # Use self.kill for UI task description
            "task_progress": self.TaskBar["position"],
            "task_max": self.TaskBar["max"],
            "xp_progress": self.ExpBar["position"],
            "xp_max": self.ExpBar["max"],
            "quest_description": self.bestquest,
            "quest_progress": self.QuestBar["position"],
            "quest_max": self.QuestBar["max"],
            "plot_progress": self.PlotBar["position"],
            "plot_max": self.PlotBar["max"],
            "encumbrance": self.EncumBar["position"],
            "encumbrance_max": self.EncumBar["max"],
            "current_act": self.act,  # Add this line
            "bestplot": self.bestplot,  # Add this line
            "act": self.act,  # Add this for compatibility

            # Pass hint data for UI
            "hints": {
                 "ExpBar": self.ExpBar.get("hint", ""),
                 "EncumBar": self.EncumBar.get("hint", ""),
                 "PlotBar": self.PlotBar.get("hint", ""),
                 "QuestBar": self.QuestBar.get("hint", ""),
                 "TaskBar": self.TaskBar.get("hint", ""),
            },
            "paused": self.paused
        }

    def _create_save_dict(self):
         """Creates the dictionary matching savegame_scheme.json"""
         # Recalculate best stats/spells/equipment just before saving
         self.update_best_stat()
         self.update_best_spell()
         # bestequip is updated during win_equip

         save_dict = {
             "Traits": {
                 "Name": self.character.get("Name", ""),
                 "Race": self.character.get("Race", ""),
                 "Class": self.character.get("Class", ""),
                 "Level": self.character.get("Level", 0)
             },
             "dna": self.dna,
             "seed": randseed(), # Save the *current* RNG state
             "birthday": self.birthday,
             "birthstamp": self.birthstamp,
             "Stats": {
                  # Order matters for web version? Use scheme order.
                  "seed": self.character["Stats"].get("seed", []), # Seed associated with these stats
                  "STR": self.character["Stats"].get("STR", 0),
                  "best": self.character["Stats"].get("best", ""),
                  "CON": self.character["Stats"].get("CON", 0),
                  "DEX": self.character["Stats"].get("DEX", 0),
                  "INT": self.character["Stats"].get("INT", 0),
                  "WIS": self.character["Stats"].get("WIS", 0),
                  "CHA": self.character["Stats"].get("CHA", 0),
                  "HP Max": self.character["Stats"].get("HP Max", 0),
                  "MP Max": self.character["Stats"].get("MP Max", 0)
             },
             "beststat": self.beststat,
             "task": self.task,
             "tasks": self.tasks,
             "elapsed": int(self.elapsed), # Should be integer seconds
             "bestequip": self.bestequip,
             "Equips": self.character.get("Equipment", {}),
             "Inventory": [], # Convert dict to list of [name, qty] lists
             "Spells": [], # Convert dict to list of [name, level] lists
             "act": self.act,
             "bestplot": self.bestplot,
             "Quests": self.quests, # Already a list of strings
             "questmonster": self.questmonster,
             "kill": self.kill,
             "ExpBar": self.ExpBar.copy(),
             "EncumBar": self.EncumBar.copy(),
             "PlotBar": self.PlotBar.copy(),
             "QuestBar": self.QuestBar.copy(),
             "TaskBar": self.TaskBar.copy(),
             "queue": self.task_queue, # Save the task queue
             "date": get_current_timestamp_iso(),
             "stamp": get_current_timestamp_ms(),
             "saveName": self.saveName,
             "bestspell": self.bestspell,
             "bestquest": self.bestquest,
             "questmonsterindex": self.questmonsterindex
         }

         # Convert Inventory
         # Ensure Gold is first if present
         inv_list = []
         if "Gold" in self.character["Inventory"]:
             inv_list.append(["Gold", self.character["Inventory"]["Gold"]])
         # Add other items sorted alphabetically
         other_items = sorted([item for item in self.character["Inventory"].items() if item[0] != "Gold"])
         inv_list.extend(other_items)
         save_dict["Inventory"] = inv_list


         # Convert Spells sorted alphabetically
         spell_list = sorted(self.character.get("Spells", {}).items())
         save_dict["Spells"] = [[name, level] for name, level in spell_list]

         # Clean up floats in progress bars for saving? JSON handles floats fine.
         # Ensure int values are ints.
         for bar_data in [save_dict["ExpBar"], save_dict["EncumBar"], save_dict["PlotBar"], save_dict["QuestBar"], save_dict["TaskBar"]]:
             bar_data["position"] = bar_data["position"] # Keep as float/int as is
             bar_data["max"] = bar_data["max"]
             bar_data["percent"] = int(bar_data["percent"])
             bar_data["remaining"] = bar_data["remaining"] # Keep as float/int
             bar_data["time"] = str(bar_data.get("time","")) # Ensure time is string
             bar_data["hint"] = str(bar_data.get("hint","")) # Ensure hint is string


         return save_dict


    def get_state_for_saving(self):
        """Return a dictionary representing the current game state for saving, matching savegame_scheme.json."""
        return self._create_save_dict()


    def apply_loaded_state(self, loaded_state):
        """Apply a loaded state (dictionary parsed from JSON) to the game logic."""

        # Store act and bestplot
        self.act = loaded_state.get('act', 0)
        self.bestplot = loaded_state.get('bestplot', '')
        
        # Validation: Check if essential keys exist
        required_top_keys = ["Traits", "Stats", "Equips", "Inventory", "Spells", "ExpBar"]
        if not all(key in loaded_state for key in required_top_keys):
            raise ValueError("Loaded state is missing essential keys. Invalid save file.")

        try:
            # Reset internal state before applying
            # self.reset_state() # Don't reset, overlay loaded data

            # --- Core Attributes ---
            self.dna = loaded_state.get("dna", [])
            self.seed = loaded_state.get("seed", [])
            randseed(self.seed) # Set RNG state
            self.birthday = loaded_state.get("birthday", get_current_timestamp_iso())
            self.birthstamp = loaded_state.get("birthstamp", get_current_timestamp_ms())
            self.task = loaded_state.get("task", "")
            self.tasks = loaded_state.get("tasks", 0)
            self.elapsed = loaded_state.get("elapsed", 0)
            self.act = loaded_state.get("act", 0)
            self.kill = loaded_state.get("kill", "Loaded Game")
            self.saveName = loaded_state.get("saveName", loaded_state.get("Traits", {}).get("Name", "Unknown"))
            self.questmonster = loaded_state.get("questmonster", "")
            self.questmonsterindex = loaded_state.get("questmonsterindex", -1)

            # --- Character Dictionary ---
            traits = loaded_state.get("Traits", {})
            stats = loaded_state.get("Stats", {})
            equips = loaded_state.get("Equips", {})
            inventory_list = loaded_state.get("Inventory", [])
            spells_list = loaded_state.get("Spells", [])

            self.character["Name"] = traits.get("Name", "Unknown")
            self.character["Race"] = traits.get("Race", "Human")
            self.character["Class"] = traits.get("Class", "Fighter")
            self.character["Level"] = traits.get("Level", 1)

            # Ensure all expected stat keys exist
            self.character["Stats"] = {
                "seed": stats.get("seed", []),
                "STR": stats.get("STR", 0),
                "best": stats.get("best", ""),
                "CON": stats.get("CON", 0),
                "DEX": stats.get("DEX", 0),
                "INT": stats.get("INT", 0),
                "WIS": stats.get("WIS", 0),
                "CHA": stats.get("CHA", 0),
                "HP Max": stats.get("HP Max", 0),
                "MP Max": stats.get("MP Max", 0)
            }
            self.beststat = loaded_state.get("beststat", "") # Use saved beststat string

            # Load Equipment - ensure all slots are present
            self.character["Equipment"] = {slot: equips.get(slot, "") for slot in EQUIPMENT_SLOTS}
            self.bestequip = loaded_state.get("bestequip", "") # Use saved bestequip string

            # Load Inventory from list format
            self.character["Inventory"] = {}
            for item_entry in inventory_list:
                if isinstance(item_entry, list) and len(item_entry) == 2:
                    name, qty = item_entry
                    self.character["Inventory"][name] = int(qty) # Ensure qty is int

            # Load Spells from list format
            self.character["Spells"] = {}
            for spell_entry in spells_list:
                if isinstance(spell_entry, list) and len(spell_entry) == 2:
                     name, level = spell_entry
                     self.character["Spells"][name] = level
            self.bestspell = loaded_state.get("bestspell", "") # Use saved bestspell string

            # --- Progress Bars ---
            self.ExpBar = loaded_state.get("ExpBar", self.ExpBar)
            self.EncumBar = loaded_state.get("EncumBar", self.EncumBar)
            self.PlotBar = loaded_state.get("PlotBar", self.PlotBar)
            self.QuestBar = loaded_state.get("QuestBar", self.QuestBar)
            self.TaskBar = loaded_state.get("TaskBar", self.TaskBar)
            # Ensure max values are reasonable
            self.ExpBar["max"] = max(1, self.ExpBar.get("max", 1))
            self.EncumBar["max"] = max(1, self.EncumBar.get("max", 1))
            self.PlotBar["max"] = max(1, self.PlotBar.get("max", 1))
            self.QuestBar["max"] = max(1, self.QuestBar.get("max", 1))
            self.TaskBar["max"] = max(1, self.TaskBar.get("max", 1))


            # --- Lists/Queues ---
            self.quests = loaded_state.get("Quests", []) # List of strings
            self.bestquest = loaded_state.get("bestquest", "") # Use saved bestquest string
            self.task_queue = loaded_state.get("queue", []) # Restore task queue

            # Set plot description based on act number
            self.bestplot = f"Act {int_to_roman(self.act)}" if self.act > 0 else "Prologue"


            # --- Final Checks and Updates ---
            # Recalculate dependent values that might not be saved correctly
            self.EncumBar["max"] = BASE_ENCUMBRANCE + self.character["Stats"].get("STR", 10)
            # Don't recalculate XP max here, trust the save file. Level up handles it.
            # self.xp_max = calculate_level_up_time(self.character.get("Level", 1))
            self.EncumBar["position"] = self.calculate_encumbrance() # Recalculate current encumbrance

            self._update_progress_bar_hints() # Update hints based on loaded values

            self.game_loaded = True
            self.last_tick_time = time.monotonic() * 1000 # Reset timer on load
            self.state_updated.emit("Game Loaded")

        except KeyError as e:
            print(f"Error applying loaded state: Missing key {e}")
            self.reset_state()
            self.game_loaded = False
            raise ValueError(f"Invalid save file: Missing key {e}") from e
        except Exception as e:
            print(f"Error applying loaded state: {e}")
            # Consider resetting state if loading fails critically
            self.reset_state()
            self.game_loaded = False
            raise ValueError(f"Failed to apply loaded state: {e}") from e


# END OF FILE: game_logic.py