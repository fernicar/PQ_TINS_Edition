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
from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon, QAction, QFont, QPalette
from PySide6.QtCore import Qt, QTimer, Slot, QPoint, QSettings # Added QSettings

from config_data import (
    DARK_STYLESHEET, EQUIPMENT_SLOTS, rough_time, int_to_roman,
    plural, definite, indefinite, SAVE_FILE_EXT, BACKUP_FILE_EXT,
    TIMER_INTERVAL_MS
)
from game_logic import GameLogic
from character_dialog import NewCharacterDialog
from decode import decode_pqw_file
import json

# Define application and organization names for QSettings
APP_NAME = "ProgressQuestPy"
ORG_NAME = "ThereIsNoSource.org"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Progress Quest (TINS Edition)")
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
        layout2.addWidget(self.equips_list, 2) # Stretch factor
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

            # Use JSON serialization with double quotes instead of pickle
            # This ensures strings with apostrophes are properly formatted
            json_data = json.dumps(game_state_data, ensure_ascii=False, indent=None)
            print(f">\tGame data to be saved:\n{json_data}")
            compressed_data = zlib.compress(json_data.encode('utf-8'), level=zlib.Z_BEST_COMPRESSION)

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
        """Find the most recent .pq or .pqw save file in the settings directory or CWD."""
        # Prefer settings directory
        save_dir = os.path.dirname(self.settings.fileName())
        try:
            # Look for both .pq and .pqw files
            pq_files = [os.path.join(save_dir, f) for f in os.listdir(save_dir) if f.endswith(SAVE_FILE_EXT)]
            pqw_files = [os.path.join(save_dir, f) for f in os.listdir(save_dir) if f.lower().endswith('.pqw')]
            files_in_dir = pq_files + pqw_files
        except FileNotFoundError:
            files_in_dir = []
            print(f"Settings directory not found: {save_dir}. Checking CWD.")
            save_dir = os.getcwd() # Fallback to current working directory
            try:
                # Look for both .pq and .pqw files in CWD
                pq_files = [os.path.join(save_dir, f) for f in os.listdir(save_dir) if f.endswith(SAVE_FILE_EXT)]
                pqw_files = [os.path.join(save_dir, f) for f in os.listdir(save_dir) if f.lower().endswith('.pqw')]
                files_in_dir = pq_files + pqw_files
            except FileNotFoundError:
                print("CWD not found.")
                return None

        if not files_in_dir:
            print(f"No save files found in {save_dir}")
            return None

        # Sort by modification time, newest first
        try:
            files_in_dir.sort(key=lambda f: os.path.getmtime(f), reverse=True)

            # Prioritize .pq files over .pqw files if they have the same base name
            # This ensures we load the native format if both exist
            for file in files_in_dir:
                if file.lower().endswith('.pq'):
                    base_name = os.path.splitext(os.path.basename(file))[0]
                    pqw_equivalent = os.path.join(os.path.dirname(file), f"{base_name}.pqw")
                    if pqw_equivalent in files_in_dir:
                        # If both .pq and .pqw exist with same name, prioritize .pq
                        files_in_dir.remove(pqw_equivalent)

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
            # Check if this is a .pqw file (base64 encoded JSON)
            if file_path.lower().endswith('.pqw'):
                print(f"Detected .pqw file format, using decode_pqw_file to convert")
                # Use the decode_pqw_file function to get JSON data
                json_data = decode_pqw_file(file_path)
                if not json_data:
                    raise ValueError("Failed to decode .pqw file")

                # Parse the JSON data
                loaded_state = json.loads(json_data)
            else:
                # Standard .pq file (compressed pickle)
                with open(file_path, 'rb') as f:
                    compressed_data = f.read()

                # Decompress data
                decompressed_data = zlib.decompress(compressed_data)

                # Try to load as JSON first (new format)
                try:
                    loaded_state = json.loads(decompressed_data.decode('utf-8'))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # Fall back to pickle for backward compatibility (old format)
                    try:
                        loaded_state = pickle.loads(decompressed_data)
                    except Exception as pickle_error:
                        raise ValueError(f"Failed to load save file: {pickle_error}")

            print(f">\tGame data from {file_path} is:\n{loaded_state}.")
            # Apply the loaded state to the game logic
            self.game_logic.apply_loaded_state(loaded_state) # apply_loaded_state should set game_loaded=True

            if self.game_logic.game_loaded:
                self.save_file_path = file_path.replace('.pqw', SAVE_FILE_EXT) if file_path.lower().endswith('.pqw') else file_path
                self.setWindowTitle(f"Progress Quest - {self.game_logic.character.get('Name', 'Unknown')}")
                self.update_ui("Game Loaded") # Force immediate UI update with reason
                self.timer.start(TIMER_INTERVAL_MS)
                self.save_action.setEnabled(True) # Enable save menu item
                self.settings.setValue("Files/lastOpened", self.save_file_path) # Store as last opened
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

        file_path, _ = QFileDialog.getOpenFileName(self, "Load Progress Quest Game", start_dir,
                                                  f"Progress Quest Files (*{SAVE_FILE_EXT} *.pqw);;PQ Files (*{SAVE_FILE_EXT});;PQW Files (*.pqw)")
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
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    app.setPalette(dark_palette)
    app.setStyleSheet(DARK_STYLESHEET)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
# END OF FILE: main_window.py