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

        # --- Check for existing save files ---
        # Look for the most recent save file and load it, or create a new character if none found
        most_recent_save = self.find_most_recent_save()
        if most_recent_save:
            print(f"Found save file: {most_recent_save}")
            self.load_game_from_path(most_recent_save)
        else:
            print("No save files found. Starting new character creation.")
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
        self.plots_list = self._create_list_view(["Act"]) # QListView doesn't show headers by default
        layout3.addWidget(self.plots_list)
        self.plot_bar = self._create_progress_bar()
        layout3.addWidget(self.plot_bar)
        layout3.addWidget(self._create_label("Quests", header=True))
        self.quests_list = self._create_list_view(["Quest"]) # QListView doesn't show headers by default
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

        # Initialize backup path
        backup_path = self.save_file_path.replace(SAVE_FILE_EXT, BACKUP_FILE_EXT) if self.save_file_path else None

        # Create backup
        if os.path.exists(self.save_file_path):
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


    def find_most_recent_save(self):
        """Find the most recent .pq save file in the current directory."""
        save_files = [f for f in os.listdir() if f.endswith(SAVE_FILE_EXT)]
        if not save_files:
            return None

        # Sort by modification time, newest first
        save_files.sort(key=lambda f: os.path.getmtime(f), reverse=True)
        return save_files[0]

    def load_game_from_path(self, file_path):
        """Load a game from a specific file path."""
        if not file_path or not os.path.exists(file_path):
            print(f"Error: Save file not found at {file_path}")
            return False

        try:
            with open(file_path, 'rb') as f:
                compressed_data = f.read()
            decompressed_data = zlib.decompress(compressed_data)
            loaded_state = pickle.loads(decompressed_data)

            # Apply the loaded state to the game logic
            self.game_logic.apply_loaded_state(loaded_state)

            self.save_file_path = file_path # Update save path
            self.setWindowTitle(f"Progress Quest - {self.game_logic.character['Name']}")
            self.update_ui() # Force immediate UI update
            self.timer.start(TIMER_INTERVAL_MS)
            print("Game loaded successfully.")
            return True
        except FileNotFoundError:
            print(f"Error: Save file not found at {file_path}")
        except (zlib.error, pickle.UnpicklingError, EOFError) as e:
            print(f"Error loading game data: Invalid or corrupt file. {e}")
        except Exception as e:
            print(f"An unexpected error occurred during loading: {e}")
        return False

    def load_game(self):
        """Show a file dialog to select and load a game."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Progress Quest Game", "", f"Progress Quest Files (*{SAVE_FILE_EXT})")
        if file_path:
            return self.load_game_from_path(file_path)
        else:
            print("Load cancelled.")
            return False


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
        window.load_game_from_path(game_file_to_load)
    #else:
    #    # If not loading from command line, the character creation
    #    # called from __init__ takes precedence.
    #    pass # Normal startup flow handled in __init__

    window.show()
    sys.exit(app.exec())