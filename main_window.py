# START OF FILE: main_window.py
# File: main_window.py
import sys
import os
# import pickle # No longer needed
import time
import base64
import json # Use json for loading
from collections import OrderedDict # To preserve order when loading JSON

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QListView, QProgressBar, QStatusBar, QSizePolicy, QSplitter,
    QFileDialog, QMessageBox
)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon, QAction, QFont, QPalette, QColor
from PySide6.QtCore import Qt, QTimer, Slot, QPoint, QSettings, QSize, QUrl # Added QUrl for file dialog

from config_data import (
    DARK_STYLESHEET, EQUIPMENT_SLOTS, rough_time, int_to_roman,
    plural, definite, indefinite,
    SAVE_FILE_EXT, BACKUP_FILE_EXT, # Use new constants
    TIMER_INTERVAL_MS, SAVEGAME_FOLDER # Use new constants
)
from game_logic import GameLogic
from character_dialog import NewCharacterDialog
# from decode import decode_pqw_file # We'll handle decoding directly

# Define application and organization names for QSettings
APP_NAME = "ProgressQuestPy"
ORG_NAME = "ThereIsNoSource.org"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(flags=Qt.WindowType.FramelessWindowHint)  # Start frameless
        
        # Set window background color immediately
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAutoFillBackground(True)
        
        # Force dark background on the central widget
        central_widget = QWidget()
        central_widget.setAutoFillBackground(True)
        central_widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setCentralWidget(central_widget)
        
        # Hide window during setup
        self.hide()
        
        self.setWindowTitle("Progress Quest (TINS Edition)")
        self.setGeometry(100, 100, 900, 700)

        # --- Ensure Savegame Folder Exists ---
        os.makedirs(SAVEGAME_FOLDER, exist_ok=True)

        # Load settings (e.g., window position, last save file)
        self.settings = QSettings(ORG_NAME, APP_NAME)

        self.game_logic = GameLogic()
        self.game_logic.state_updated.connect(self.update_ui)

        self.save_file_path = None

        self.setup_ui()
        self.create_actions()
        self.create_menus()

        # --- Game Timer ---
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.game_logic.tick)
        self.timer.setInterval(TIMER_INTERVAL_MS)

        # --- Restore Geometry and State ---
        self.restore_geometry_and_state()

        # Remove frameless hint and show window properly
        self.setWindowFlags(Qt.WindowType.Window)
        QTimer.singleShot(0, self.show)  # Show on next event loop iteration

        # --- Initial Game Load or Creation ---
        # Try loading last opened file first
        last_file = self.settings.value("Files/lastOpened", None)
        loaded = False
        if last_file and os.path.exists(last_file):
             loaded = self.load_game_from_path(last_file)

        # If last file load failed or no last file, try finding most recent
        if not loaded:
            most_recent_save = self.find_most_recent_save()
            if most_recent_save:
                loaded = self.load_game_from_path(most_recent_save)

        # If still not loaded, prompt for new character
        if not loaded:
            print("No valid save files found or loaded. Starting new character creation.")
            # Delay character creation until after window is shown
            QTimer.singleShot(100, self.create_new_character)
            # self.create_new_character() # This might block showing the window initially
        else:
             # If loaded successfully, make sure pause state is correct
             QTimer.singleShot(50, lambda: self.set_paused(self.game_logic.is_paused()))


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
        self.traits_list = self._create_list_view()
        layout1.addWidget(self.traits_list, 1) # Add stretch factor
        self.stats_list = self._create_list_view()
        layout1.addWidget(self.stats_list, 2) # More stretch for stats
        layout1.addWidget(self._create_label("Experience"))
        self.exp_bar = self._create_progress_bar()
        layout1.addWidget(self.exp_bar)
        layout1.addWidget(self._create_label("Spell Book", header=True))
        self.spells_list = self._create_list_view()
        layout1.addWidget(self.spells_list, 3) # Most stretch for spells
        self.splitter.addWidget(panel1)

        # Panel 2: Equipment & Inventory
        panel2 = QWidget()
        layout2 = QVBoxLayout(panel2)
        layout2.setContentsMargins(0,0,0,0); layout2.setSpacing(3)
        layout2.addWidget(self._create_label("Equipment", header=True))
        self.equips_list = self._create_list_view()
        layout2.addWidget(self.equips_list, 2) # Stretch factor
        layout2.addWidget(self._create_label("Inventory", header=True))
        self.inventory_list = self._create_list_view()
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
        self.plots_list = self._create_list_view()
        layout3.addWidget(self.plots_list, 1) # Stretch factor
        self.plot_bar = self._create_progress_bar()
        layout3.addWidget(self.plot_bar)
        layout3.addWidget(self._create_label("Quests", header=True))
        self.quests_list = self._create_list_view()
        layout3.addWidget(self.quests_list, 2) # More stretch for quests
        self.quest_bar = self._create_progress_bar()
        layout3.addWidget(self.quest_bar)
        self.splitter.addWidget(panel3)

        main_layout.addWidget(self.splitter, 1) # Give splitter vertical stretch

        # --- Bottom Bars ---
        bottom_layout = QVBoxLayout()
        bottom_layout.setSpacing(2)
        self.kill_label = QLabel("Welcome to Progress Quest!") # Renamed from status_bar_label
        self.kill_label.setObjectName("KillLabel") # For styling if needed
        self.kill_label.setStyleSheet("font-size: 9pt; color: #e0e0e0; padding: 2px;") # Slightly larger
        self.kill_label.setAlignment(Qt.AlignmentFlag.AlignCenter) # Center align
        bottom_layout.addWidget(self.kill_label)

        self.task_bar = self._create_progress_bar()
        bottom_layout.addWidget(self.task_bar)
        main_layout.addLayout(bottom_layout) # Add bottom layout below splitter


        # --- Models for ListViews ---
        # Use simple models, formatting done in _update_model
        self.traits_model = QStandardItemModel()
        self.stats_model = QStandardItemModel()
        self.equips_model = QStandardItemModel()
        self.inventory_model = QStandardItemModel()
        self.spells_model = QStandardItemModel()
        self.plots_model = QStandardItemModel()
        self.quests_model = QStandardItemModel()

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

        # Pause toggle action
        self.pause_action = QAction("&Pause Game", self)
        self.pause_action.setCheckable(True)
        # Initial state set after loading/creating game
        self.pause_action.triggered.connect(self.toggle_pause)
        self.pause_action.setEnabled(False) # Enabled only when game is loaded/created

        self.exit_action = QAction("E&xit", self)
        self.exit_action.triggered.connect(self.close)

    def create_menus(self):
        """Create the main menu bar."""
        self.menuBar().setStyleSheet(DARK_STYLESHEET) # Style menubar too
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.load_action)
        file_menu.addAction(self.save_action)
        file_menu.addSeparator()
        file_menu.addAction(self.pause_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

    # --- UI Helper Methods ---
    def _create_label(self, text, header=False):
        label = QLabel(text)
        if header:
            label.setObjectName("HeaderLabel") # For specific styling
        return label

    def _create_list_view(self): # Removed headers arg
        view = QListView()
        view.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        view.setSelectionMode(QListView.SelectionMode.NoSelection)
        view.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setVerticalScrollMode(QListView.ScrollMode.ScrollPerPixel)
        view.setUniformItemSizes(True)
        return view

    def _create_progress_bar(self):
        bar = QProgressBar()
        bar.setRange(0, 1000) # Base range, will be updated by _update_progress_bar
        bar.setValue(0)
        bar.setTextVisible(True)
        bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Format set dynamically by _update_progress_bar
        bar.setFormat("%p%") # Default format
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
                 if not self.save_game(): return
             elif reply == QMessageBox.StandardButton.Cancel:
                 return

        self.timer.stop()
        self.save_action.setEnabled(False)
        self.pause_action.setEnabled(False)
        self.pause_action.setChecked(True) # Reset pause action state

        dialog = NewCharacterDialog(self)
        if dialog.exec():
            char_data = dialog.get_character_data()
            if char_data:
                self.game_logic.initialize_new_character(
                    char_data["name"], char_data["race"], char_data["class"], char_data["stats"]
                )
                # Set save file path based on character name in the savegame folder
                char_name_safe = "".join(c for c in char_data["name"] if c.isalnum() or c in (' ', '_')).rstrip()
                self.save_file_path = os.path.join(SAVEGAME_FOLDER, f"{char_name_safe}{SAVE_FILE_EXT}")

                self.setWindowTitle(f"Progress Quest - {char_data['name']}")
                self.save_action.setEnabled(True)
                self.pause_action.setEnabled(True)
                print(f"Starting new game. Save file will be: {self.save_file_path}")

                # Save immediately after creation
                if self.save_game():
                     self.settings.setValue("Files/lastOpened", self.save_file_path)

                # Start timer only AFTER setting pause state
                self.set_paused(True) # Start paused
                self.timer.start() # Timer interval already set

        else:
            print("Character creation cancelled.")
            if not self.game_logic.game_loaded:
                self.close()
            else:
                 # If cancelled, resume previous game? Make sure pause state is correct.
                 self.set_paused(self.game_logic.is_paused())
                 if not self.game_logic.is_paused():
                     self.timer.start()


    def set_paused(self, paused):
        """Set the game's paused state and update UI."""
        self.game_logic.set_paused(paused) # Update logic first

        # Update UI elements
        self.pause_action.setChecked(paused)
        self.pause_action.setText("&Resume Game" if paused else "&Pause Game")

        title = self.windowTitle().replace(" [PAUSED]", "") # Remove existing tag
        if paused:
            self.setWindowTitle(f"{title} [PAUSED]")
            self.kill_label.setText("Game paused - Press 'Resume Game' in the File menu to continue")
            self.timer.stop() # Explicitly stop timer when pausing
        else:
            self.setWindowTitle(title)
            # Restore kill label from game state if available
            if self.game_logic.game_loaded:
                 self.kill_label.setText(self.game_logic.kill)
            else:
                 self.kill_label.setText("...")
            self.timer.start() # Start timer only when resuming

    def toggle_pause(self):
        """Toggle the game's paused state based on the pause action's checked state."""
        # Checkable action toggles *before* triggered signal is processed.
        # So, isChecked() reflects the state *after* the click.
        paused = self.pause_action.isChecked()
        self.set_paused(paused)

    @Slot(str)
    def update_ui(self, reason="Tick"):
        """Update all UI elements based on the current game state."""
        if not self.game_logic.game_loaded: return

        state = self.game_logic.get_state()
        char = state["character"] # Convenience accessor

        # --- Panel 1: Character Sheet ---
        # Only major updates redraw lists to reduce flicker/load
        is_major_update = reason not in ["Tick"]

        if is_major_update or reason == "Tick": # Update always for now, can optimize later
            self._update_model(self.traits_model, [
                ("Name", char.get("Name", "N/A")),
                ("Race", char.get("Race", "N/A")),
                ("Class", char.get("Class", "N/A")),
                ("Level", str(char.get("Level", 0))),
            ], bold_keys=True)

            stats_data = []
            stats_dict = char.get("Stats", {})
            # Use specific order from JS K.Stats
            for stat_name in ["STR", "CON", "DEX", "INT", "WIS", "CHA", "HP Max", "MP Max"]:
                stats_data.append((stat_name, str(stats_dict.get(stat_name, 0))))
            self._update_model(self.stats_model, stats_data, bold_keys=True)

        # Update spells only on specific events
        if reason in ["Level Up", "Quest Complete", "Game Loaded", "Character Created"]:
            # JS saves spells as [name, level_roman] list, sorted alphabetically
            spells_data_list = sorted(char.get("Spells", {}).items())
            self._update_model(self.spells_model, spells_data_list)

        self._update_progress_bar(self.exp_bar, state["xp_progress"], state["xp_max"],
                                  state["hints"]["ExpBar"])

        # --- Panel 2: Equipment & Inventory ---
        if reason in ["Equipment Bought", "Quest Complete", "Act Complete", "Game Loaded", "Character Created", "Level Up"]: # Level Up might grant equip
            equip_data = []
            equip_dict = char.get("Equipment", {})
            for slot in EQUIPMENT_SLOTS: # Use defined order
                equip_data.append((slot, equip_dict.get(slot, "")))
            self._update_model(self.equips_model, equip_data, bold_keys=True)

        if reason in ["Combat End", "Item Sold", "Quest Complete", "Act Complete", "Game Loaded", "Character Created", "Level Up"]: # Level Up might grant items
             inv_data = []
             # JS saves inventory as list, Gold first, then alphabetical
             inv_dict = char.get("Inventory", {})
             if "Gold" in inv_dict:
                  inv_data.append(("Gold", str(inv_dict["Gold"])))
             # Add other items sorted
             other_items = sorted([(name, str(qty)) for name, qty in inv_dict.items() if name != "Gold"])
             inv_data.extend(other_items)
             self._update_model(self.inventory_model, inv_data, align_value_right=True)


        self._update_progress_bar(self.encum_bar, state["encumbrance"], state["encumbrance_max"],
                                  state["hints"]["EncumBar"])

        # --- Panel 3: Plot & Quests ---
        if reason in ["Act Complete", "Game Loaded", "Character Created", "Act Transition"]:
            
            # Get current act number, ensuring we handle the loaded state correctly
            current_act = state.get("act", 0)
            
            # Create list from 0 (Prologue) to current_act (inclusive)
            plot_list = []
            for i in range(current_act + 1):
                act_name = "Prologue" if i == 0 else f"Act {int_to_roman(i)}"
                plot_list.append(act_name)
            
            plot_data = []
            current_act_idx = len(plot_list) - 1
            for i, act_name in enumerate(plot_list[-99:]): # Show last 99 acts
                prefix = "✓ " if i + max(0, len(plot_list)-99) < current_act_idx else "► "
                plot_data.append((f"{prefix}{act_name}", ""))
            self._update_model(self.plots_model, plot_data, use_formatting=False)
            if plot_data: self.plots_list.scrollToBottom()

        self._update_progress_bar(self.plot_bar, state["plot_progress"], state["plot_max"],
                                  state["hints"]["PlotBar"])


        if reason in ["Quest Complete", "Game Loaded", "Character Created"]:
            quest_list = state.get("quests", []) # Already a list of strings
            quest_data = []
            quest_count = len(quest_list)
            for i, desc in enumerate(quest_list[-15:]): # Show last 15 quests
                 current_index = i + max(0, quest_count - 15)
                 prefix = "✓ " if current_index < quest_count - 1 else "► "
                 quest_data.append((f"{prefix}{desc}", ""))
            self._update_model(self.quests_model, quest_data, use_formatting=False)
            if quest_data: self.quests_list.scrollToBottom()

        self._update_progress_bar(self.quest_bar, state["quest_progress"], state["quest_max"],
                                  state["hints"]["QuestBar"])

        # --- Bottom Bars ---
        if not self.game_logic.is_paused(): # Only update task description if not paused
            self.kill_label.setText(state["task_description"])
        self._update_progress_bar(self.task_bar, state["task_progress"], state["task_max"], state["hints"]["TaskBar"])


    def _update_model(self, model, data, use_formatting=True, bold_keys=False, align_value_right=False):
        """ Efficiently updates a QStandardItemModel for QListView display.
            Data is list of (col1_text, col2_text) tuples.
            ListView only shows col1_text formatted.
        """
        model.setRowCount(len(data)) # Adjust row count first
        bold_font = QFont()
        bold_font.setBold(True)
        normal_font = QFont() # Assume default font is normal

        for row, row_data in enumerate(data):
            item1 = model.item(row, 0)
            if item1 is None:
                item1 = QStandardItem()
                model.setItem(row, 0, item1)

            text1 = str(row_data[0])
            text2 = str(row_data[1]) if len(row_data) > 1 else ""

            # Simple formatting: "Key: Value" or just "Text"
            if use_formatting and text2:
                display_text = f"{text1}: {text2}"
            else:
                 display_text = text1

            item1.setText(display_text)
            item1.setFont(bold_font if bold_keys else normal_font)
            # Alignment only works well in QTableView, less predictable in QListView item
            # if align_value_right:
            #      item1.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)


    def _update_progress_bar(self, bar, value, maximum, text_format=None):
        """Safely update a progress bar's value, maximum, and format string."""
        # Use floats for potentially large values from game logic
        val = float(value)
        max_val = float(maximum)
        safe_maximum = max(1e-9, max_val) # Avoid division by zero

        # Update range and value
        bar.setMaximum(int(safe_maximum) if safe_maximum < sys.maxsize else 1000000) # Use large int max if needed
        bar.setValue(int(max(0.0, min(val, safe_maximum))))

        # Set format string
        if text_format:
            try:
                # Test the format string - remove complex f-string eval here
                bar.setFormat(str(text_format))
            except Exception as e:
                print(f"Warning: Invalid progress bar format string: {text_format} ({e})")
                bar.setFormat("%p%") # Fallback to percentage
        else:
            bar.setFormat("%p%")


    # --- Saving and Loading ---
    @Slot()
    def save_game(self):
        """Saves the current game state in JSON format to .pqw"""
        if not self.game_logic.game_loaded:
            print("Cannot save: Game not loaded.")
            return False
        if not self.save_file_path:
            print("Warning: No save path set. Prompting user.")
            # Use QFileDialog to get save path if it's missing
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Progress Quest Game",
                                                      SAVEGAME_FOLDER, f"PQW Files (*{SAVE_FILE_EXT})")
            if not file_path:
                print("Save cancelled by user.")
                return False
            # Ensure extension is correct
            if not file_path.endswith(SAVE_FILE_EXT):
                file_path += SAVE_FILE_EXT
            self.save_file_path = file_path

        pqw_path = self.save_file_path
        base_name = pqw_path.replace(SAVE_FILE_EXT, "")

        self.kill_label.setText("Saving game...")
        QApplication.processEvents()

        # Create backup of .pqw file
        backup_path = pqw_path.replace(SAVE_FILE_EXT, BACKUP_FILE_EXT)
        if os.path.exists(pqw_path):
            try:
                if os.path.exists(backup_path): os.remove(backup_path)
                os.rename(pqw_path, backup_path)
            except OSError as e:
                QMessageBox.warning(self, "Save Warning", f"Could not create backup file:\n{e}")

        # Save current state
        try:
            game_state_data = self.game_logic.get_state_for_saving()
            json_string = json.dumps(game_state_data, indent=None, ensure_ascii=False) # Compact JSON

            # 1. Save as .pqw file (base64 encoded JSON)
            encoded_data = base64.b64encode(json_string.encode('utf-8'))
            with open(pqw_path, 'wb') as f:
                f.write(encoded_data)

            self.kill_label.setText("Game saved.")
            QTimer.singleShot(2000, lambda: self.kill_label.setText(self.game_logic.kill if self.game_logic.game_loaded else "..."))
            self.setWindowModified(False)
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            QMessageBox.critical(self, "Save Error", f"Could not save game.\n\nError: {e}")
            # Attempt to restore backup if save failed
            if os.path.exists(backup_path):
                try:
                    if os.path.exists(pqw_path): os.remove(pqw_path)
                    os.rename(backup_path, pqw_path)
                    print("Restored backup file after save error.")
                except OSError as be:
                     print(f"Critical Error: Could not restore backup file: {be}")
            return False


    def find_most_recent_save(self):
        """Find the most recent .pqw save file in the savegame folder."""
        files_in_dir = []
        try:
            files_in_dir = [os.path.join(SAVEGAME_FOLDER, f) for f in os.listdir(SAVEGAME_FOLDER) if f.endswith(SAVE_FILE_EXT)]
        except FileNotFoundError:
            print(f"Save directory not found: {SAVEGAME_FOLDER}")
            return None

        if not files_in_dir:
            print(f"No save files found in {SAVEGAME_FOLDER}")
            return None

        # Sort by modification time, newest first
        try:
            files_in_dir.sort(key=lambda f: os.path.getmtime(f), reverse=True)
            return files_in_dir[0]
        except FileNotFoundError:
             print("Error accessing file modification times.")
             return None
        except Exception as e:
             print(f"Error sorting save files: {e}")
             return None


    def load_game_from_path(self, file_path):
        """Load a game from a specific file path .pqw."""
        if not file_path or not os.path.exists(file_path):
            print(f"Error: Save file not found at {file_path}")
            return False

        self.kill_label.setText("Loading game...")
        QApplication.processEvents()

        try:
            loaded_state = None
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == SAVE_FILE_EXT.lower():
                # Load .pqw (Base64 encoded JSON)
                with open(file_path, 'rb') as f:
                    encoded_data = f.read()
                # Handle potential padding issues during decode
                try:
                    json_string = base64.b64decode(encoded_data, validate=True).decode('utf-8')
                except base64.binascii.Error as b64_err:
                     print(f"Base64 decode error: {b64_err}. Trying to add padding.")
                     padding_needed = '=' * (4 - (len(encoded_data) % 4))
                     try:
                         json_string = base64.b64decode(encoded_data + padding_needed.encode()).decode('utf-8')
                     except Exception as pad_err:
                         raise ValueError(f"Failed to decode .pqw file even with padding: {pad_err}") from pad_err

                loaded_state = json.loads(json_string) # Use standard loads
            else:
                raise ValueError(f"Unsupported file extension: {file_ext}")

            # Apply the loaded state
            self.game_logic.apply_loaded_state(loaded_state)

            if self.game_logic.game_loaded:
                self.save_file_path = file_path
                self.setWindowTitle(f"Progress Quest - {self.game_logic.saveName}")
                self.update_ui("Game Loaded")
                self.timer.start() # Timer interval already set
                self.save_action.setEnabled(True)
                self.pause_action.setEnabled(True)
                self.settings.setValue("Files/lastOpened", self.save_file_path)
                self.kill_label.setText("Game loaded successfully.")
                # Ensure pause state is set correctly after load
                self.set_paused(self.game_logic.is_paused())
                # Restore status after 2s if not paused
                if not self.game_logic.is_paused():
                    QTimer.singleShot(2000, lambda: self.kill_label.setText(self.game_logic.kill))
                return True
            else:
                 raise ValueError("Game logic failed to apply loaded state.")

        except FileNotFoundError:
            QMessageBox.critical(self, "Load Error", f"Save file not found:\n{file_path}")
        except (json.JSONDecodeError, base64.binascii.Error, EOFError, AttributeError, KeyError, TypeError, ValueError) as e:
            print(f"Error loading game data: {e}")
            QMessageBox.critical(self, "Load Error", f"Could not load game:\nInvalid or corrupt file format.\n\nError: {e}")
            self.game_logic.reset_state()
            self.save_file_path = None
            self.setWindowTitle("Progress Quest (Zero Source Edition)")
            self.update_ui("Load Failed")
            self.save_action.setEnabled(False)
            self.pause_action.setEnabled(False)
            self.timer.stop()
        except Exception as e:
            import traceback
            print(f"An unexpected error occurred during loading: {e}")
            traceback.print_exc() # Print full traceback for unexpected errors
            QMessageBox.critical(self, "Load Error", f"An unexpected error occurred while loading:\n{e}")
            self.game_logic.reset_state()
            self.save_action.setEnabled(False)
            self.pause_action.setEnabled(False)
            self.timer.stop()

        self.kill_label.setText("Failed to load game.")
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
                 if not self.save_game(): return False
             elif reply == QMessageBox.StandardButton.Cancel:
                 return False

        start_dir = os.path.abspath(SAVEGAME_FOLDER)
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Progress Quest Game", start_dir,
                                                   f"Progress Quest Files (*{SAVE_FILE_EXT});;All Files (*)")
        if file_path:
            self.timer.stop()
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

        # Use valid defaults if settings are missing or invalid
        default_size = QSize(900, 700)
        default_pos = QPoint(100, 100)

        if size and size.isValid(): self.resize(size)
        else: self.resize(default_size)

        if pos and not pos.isNull(): self.move(pos)
        else: self.move(default_pos)

        if state: self.restoreState(state)
        if splitter_state:
             self.splitter.restoreState(splitter_state)
        else:
             total_width = self.splitter.width()
             # Give slightly more space to middle panel
             p1_w = int(total_width * 0.28)
             p2_w = int(total_width * 0.40)
             p3_w = total_width - p1_w - p2_w
             self.splitter.setSizes([p1_w, p2_w, p3_w])

    # --- Event Overrides ---
    def closeEvent(self, event):
        """Handle window close event: save settings and game."""
        self.timer.stop()
        if self.game_logic.game_loaded and self.save_file_path:
            self.save_game()
        self.save_geometry_and_state()
        event.accept()


# --- Main Execution ---
if __name__ == "__main__":
    # Set AppUserModelID for Windows Taskbar grouping/icon
    try:
        from ctypes import windll
        myappid = f'{ORG_NAME}.{APP_NAME}.Python.1.0' # Arbitrary string
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass # Ignore if not on Windows or ctypes not available
    except AttributeError:
         print("Could not set AppUserModelID (may be normal on non-Windows).")


    app = QApplication(sys.argv)
    app.setOrganizationName(ORG_NAME)
    app.setApplicationName(APP_NAME)

    # Create comprehensive dark palette
    dark_palette = QPalette()
    dark_color = QColor("#2b2b2b")
    disabled_color = QColor("#4a4a4a")
    text_color = QColor("#f0f0f0")
    
    # Set all color roles
    dark_palette.setColor(QPalette.ColorRole.Window, dark_color)
    dark_palette.setColor(QPalette.ColorRole.WindowText, text_color)
    dark_palette.setColor(QPalette.ColorRole.Base, dark_color)
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, dark_color)
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, dark_color)
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, text_color)
    dark_palette.setColor(QPalette.ColorRole.Text, text_color)
    dark_palette.setColor(QPalette.ColorRole.Button, dark_color)
    dark_palette.setColor(QPalette.ColorRole.ButtonText, text_color)
    dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    dark_palette.setColor(QPalette.ColorRole.Link, QColor("#0d87e4"))
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor("#3a3a3a"))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, text_color)

    # Set disabled colors
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, disabled_color)
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, disabled_color)
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, disabled_color)
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, QColor("#333333"))
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, disabled_color)

    # Apply dark theme
    app.setPalette(dark_palette)
    app.setStyleSheet(DARK_STYLESHEET)

    # Create window but don't show it immediately
    window = MainWindow()
    
    sys.exit(app.exec()) # Show the window and start the event loop
# END OF FILE: main_window.py
