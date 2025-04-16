import sys
import time
import math
import webbrowser
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QProgressBar, QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QDialog, QLineEdit, QRadioButton, QMessageBox, QListWidget,
    QListWidgetItem, QAbstractItemView, QSizePolicy, QSpacerItem, QMenuBar,
    QMenu, QFileDialog, QTextEdit, QStyleFactory
)
from PySide6.QtCore import Qt, QTimer, QSize, QUrl
from PySide6.QtGui import QIcon, QPalette, QDesktopServices, QAction # For styling and icons

import game # Import the non-GUI logic

# --- Constants ---
TICK_INTERVAL_MS = 50  # Match clock.js interval
SAVE_INTERVAL_SEC = 60 # Auto-save every minute
REPOSITORY_URL = "https://github.com/fernicar/PQ_TINS_Edition"
STYLE_THEMES = ['Windows', 'windowsvista', 'windows11', 'Fusion']
STYLE_SELECTED_THEME = STYLE_THEMES[3]  # Fusion style by default
COLOR_SCHEMES = ['Auto', 'Light', 'Dark']
DEFAULT_COLOR_SCHEME = COLOR_SCHEMES[0]  # Auto by default

# --- Helper Functions ---

def find_most_recent_pqw_file():
    """Find the most recent .pqw file in the savegame directory."""
    save_files = list(game.SAVE_DIR.glob("*.pqw"))
    if not save_files: return None
    # Sort by modification time, newest first
    save_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return save_files[0].name

# --- Main Application Window ---

class MainWindow(QMainWindow):
    def __init__(self, game_state):
        super().__init__()
        # Set object name for CSS styling
        self.setObjectName("MainWindow")
        self.game_state = game_state
        self.last_tick_time = time.monotonic() * 1000 # ms
        self.save_countdown = SAVE_INTERVAL_SEC * (1000 / TICK_INTERVAL_MS) # Ticks until save

        # Initialize tracking variables for UI updates
        self._previous_act = self.game_state.get("act", 0)

        self.setWindowTitle(f"Progress Quest - {self.game_state['Traits']['Name']}")
        # self.setWindowIcon(QIcon("path/to/icon.ico")) # Optional

        self._init_ui()
        self._create_menu_bar()
        self.update_ui() # Initial UI population

        # Setup timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(TICK_INTERVAL_MS)

    def _create_menu_bar(self):
        """Create the menu bar with File, View, and Help menus."""
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("&File")

        # New Character action
        new_char_action = QAction("&New Character", self)
        new_char_action.triggered.connect(self._new_character)
        file_menu.addAction(new_char_action)

        # Load .pqw File action
        load_game_action = QAction("&Load .pqw File", self)
        load_game_action.triggered.connect(self._load_game)
        file_menu.addAction(load_game_action)

        # Save .pqw File action
        save_game_action = QAction("&Save .pqw File", self)
        save_game_action.triggered.connect(self._save_game)
        file_menu.addAction(save_game_action)

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View Menu
        view_menu = menu_bar.addMenu("&View")
        
        # Color Scheme submenu
        color_scheme_menu = view_menu.addMenu("&Color Scheme")
        
        # Add color scheme options
        self.color_scheme_actions = []
        
        for scheme_name in COLOR_SCHEMES:
            action = QAction(scheme_name, self)
            action.setCheckable(True)
            action.setData(COLOR_SCHEMES.index(scheme_name))  # 0=Auto, 1=Light, 2=Dark
            action.triggered.connect(lambda checked, a=action: self._on_color_scheme_selected(checked, a.data()))
            color_scheme_menu.addAction(action)
            self.color_scheme_actions.append(action)
            # Set Auto as checked by default
            if scheme_name == 'Auto':
                action.setChecked(True)
        
        # Style submenu
        style_menu = view_menu.addMenu("&Style")
        
        # Add style options
        self.style_actions = []
        
        for style_name in STYLE_THEMES:
            action = QAction(style_name, self)
            action.setCheckable(True)
            action.triggered.connect(lambda checked, s=style_name: self._on_style_changed(s))
            style_menu.addAction(action)
            self.style_actions.append(action)

        # Help Menu
        help_menu = menu_bar.addMenu("&Help")

        # Visit Repository action
        visit_repo_action = QAction("&Visit Repository", self)
        visit_repo_action.triggered.connect(self._visit_repository)
        help_menu.addAction(visit_repo_action)

        # About action
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _new_character(self):
        """Show the New Character dialog."""
        dialog = NewCharacterDialog(self)
        if dialog.exec():
            game.save_game(self.game_state) # Save current game before switching

            # Load the new character
            new_filename = f"{dialog.new_game_state['Traits']['Name']}.pqw"
            new_game_state = game.load_game(new_filename)
            if new_game_state:
                self.game_state = new_game_state
                self.setWindowTitle(f"Progress Quest - {self.game_state['Traits']['Name']}")
                self.update_ui()
            else: QMessageBox.critical(self, "Load Error", f"Failed to load new character: {new_filename}")

    def _load_game(self):
        """Show a file dialog to load a game."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Progress Quest Save File",
            str(game.SAVE_DIR),  # Start in the savegame directory
            "Progress Quest Save Files (*.pqw);;All Files (*.*)"
        )

        if file_path:
            file_path = Path(file_path) # Convert to Path object
            if not file_path.exists(): # Check if the file exists
                QMessageBox.critical(self, "File Error", f"File not found: {file_path}")
                return

            # Get just the filename for loading
            filename = file_path.name

            # If the file is not in the savegame directory, read its content and save it there
            if file_path.parent != game.SAVE_DIR:
                try:
                    # Read the file content
                    with open(file_path, 'r') as source_file: file_content = source_file.read()

                    # Save to the savegame directory
                    dest_path = game.SAVE_DIR / filename
                    with open(dest_path, 'w') as dest_file: dest_file.write(file_content)

                    QMessageBox.information( self, "File Copied",
                        f"File '{filename}' has been copied to the savegame directory."
                    )
                except Exception as e:
                    QMessageBox.critical(self, "Copy Error", f"Failed to copy file: {e}")
                    return

            # Save current game before loading new one
            game.save_game(self.game_state)

            # Load the selected game
            new_game_state = game.load_game(filename)
            if new_game_state:
                self.game_state = new_game_state
                self.setWindowTitle(f"Progress Quest - {self.game_state['Traits']['Name']}")
                self.update_ui()
            else: QMessageBox.critical(self, "Load Error", f"Failed to Load .pqw File: {filename}")

    def _save_game(self):
        """Save the current game state."""
        if game.save_game(self.game_state): QMessageBox.information(self, "Save .pqw File", "PQW File saved successfully.")
        else: QMessageBox.critical(self, "Save Error", "Failed to Save .pqw File.")

    def _visit_repository(self):
        """Open the repository URL in the default browser."""
        QDesktopServices.openUrl(QUrl(REPOSITORY_URL))

    def _show_about(self):
        """Show the About dialog."""
        dialog = AboutDialog(self)
        dialog.exec()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        # Set main layout spacing and margins for a modern look
        main_layout.setSpacing(4) # Slightly increase spacing
        main_layout.setContentsMargins(6, 6, 6, 6) # Add some margin around the edges

        # Set window to a reasonable size that fits all panels
        self.resize(900, 700) # Starting size that accommodates all panels

        # Make the central widget expand to fill the window
        central_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        top_hbox = QHBoxLayout()
        main_layout.addLayout(top_hbox)

        # == Left Column (Izquierda) ==
        left_vbox = QVBoxLayout()
        top_hbox.addLayout(left_vbox)
        left_vbox.setSpacing(2) # Fine-tune spacing

        # Character Sheet Group
        char_group = QGroupBox("Character Sheet")
        char_layout = QVBoxLayout(char_group)
        char_layout.setSpacing(2)  # Reduce spacing
        char_layout.setContentsMargins(0, 0, 0, 0)  # Reduce margins
        self.traits_table = QTableWidget(len(game.TRAITS), 2)
        self.traits_table.setHorizontalHeaderLabels(["Trait", "Value"])
        self.traits_table.verticalHeader().setVisible(False)
        self.traits_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.traits_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.traits_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # Disable selection
        self.traits_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.traits_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # Make rows more compact
        self.traits_table.verticalHeader().setDefaultSectionSize(20)
        # Reduce header height
        self.traits_table.horizontalHeader().setFixedHeight(20)
        # Populate fixed trait labels
        for i, trait_name in enumerate(game.TRAITS):
            item = QTableWidgetItem("  " + trait_name)  # Add left indentation
            self.traits_table.setItem(i, 0, item)
        # Calculate exact height needed for Character Sheet (rows + header + borders)
        exact_height = (self.traits_table.rowHeight(0) * len(game.TRAITS)) + self.traits_table.horizontalHeader().height() + 2
        self.traits_table.setFixedHeight(exact_height)
        # Disable scrollbars completely
        self.traits_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.traits_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        char_layout.addWidget(self.traits_table)

        # Stats Group (within Character Sheet layout)
        stats_group = QGroupBox("Stats") # No title needed if visually distinct
        stats_layout = QVBoxLayout(stats_group)
        stats_layout.setSpacing(2)  # Reduce spacing
        stats_layout.setContentsMargins(0, 0, 0, 0)  # Reduce margins
        self.stats_table = QTableWidget(len(game.STATS), 2)
        self.stats_table.setHorizontalHeaderLabels(["Stat", "Value"])
        self.stats_table.verticalHeader().setVisible(False)
        self.stats_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.stats_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.stats_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # Disable selection
        self.stats_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.stats_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # Make rows more compact
        self.stats_table.verticalHeader().setDefaultSectionSize(20)
        # Reduce header height
        self.stats_table.horizontalHeader().setFixedHeight(20)
         # Populate fixed stat labels
        for i, stat_name in enumerate(game.STATS):
            item = QTableWidgetItem("  " + stat_name)  # Add left indentation
            self.stats_table.setItem(i, 0, item)
        # Calculate exact height needed for Stats (rows + header + borders)
        exact_height = (self.stats_table.rowHeight(0) * len(game.STATS)) + self.stats_table.horizontalHeader().height() + 2
        self.stats_table.setFixedHeight(exact_height)
        # Disable scrollbars completely
        self.stats_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.stats_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        char_layout.addWidget(self.stats_table) # Add stats table to char_layout

        left_vbox.addWidget(char_group)


        # Experience Bar
        exp_label = QLabel("Experience")
        left_vbox.addWidget(exp_label)
        self.exp_bar = QProgressBar()
        self.exp_bar.setFormat("%p%") # Show percentage by default
        self.exp_bar.setTextVisible(True)
        left_vbox.addWidget(self.exp_bar)

        # Spell Book Group
        spell_group = QGroupBox("Spell Book")
        spell_layout = QVBoxLayout(spell_group)
        spell_layout.setSpacing(2)  # Reduce spacing
        spell_layout.setContentsMargins(0, 0, 0, 0)  # Reduce margins
        self.spells_table = QTableWidget(0, 2) # Rows added dynamically
        self.spells_table.setHorizontalHeaderLabels(["Spell", "Level"])
        self.spells_table.verticalHeader().setVisible(False)
        self.spells_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.spells_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.spells_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # Disable selection
        self.spells_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.spells_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # Allow Spell Book to expand
        self.spells_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # Reduce header height
        self.spells_table.horizontalHeader().setFixedHeight(20)
        # Make rows more compact
        self.spells_table.verticalHeader().setDefaultSectionSize(20)
        spell_layout.addWidget(self.spells_table)
        left_vbox.addWidget(spell_group, 1) # Give it a stretch factor to expand
        # No stretch at the end to allow panel to fill space

        # == Center Column (Centro) ==
        center_vbox = QVBoxLayout()
        top_hbox.addLayout(center_vbox)
        center_vbox.setSpacing(2)

        # Equipment Group
        equip_group = QGroupBox("Equipment")
        equip_layout = QVBoxLayout(equip_group)
        equip_layout.setSpacing(2)  # Reduce spacing
        equip_layout.setContentsMargins(0, 0, 0, 0)  # Reduce margins
        self.equips_table = QTableWidget(len(game.EQUIPS), 2)
        self.equips_table.setHorizontalHeaderLabels(["Slot", "Item"])
        self.equips_table.verticalHeader().setVisible(False)
        self.equips_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.equips_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.equips_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # Disable selection
        self.equips_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.equips_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # Make rows more compact
        self.equips_table.verticalHeader().setDefaultSectionSize(20)
        # Reduce header height
        self.equips_table.horizontalHeader().setFixedHeight(20)
        # Populate fixed equip slot labels
        for i, equip_name in enumerate(game.EQUIPS):
            item = QTableWidgetItem("  " + equip_name)  # Add left indentation
            self.equips_table.setItem(i, 0, item)
        # Calculate exact height needed for Equipment (rows + header + borders)
        exact_height = (self.equips_table.rowHeight(0) * len(game.EQUIPS)) + self.equips_table.horizontalHeader().height() + 2
        self.equips_table.setFixedHeight(exact_height)
        # Disable scrollbars completely
        self.equips_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.equips_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        equip_layout.addWidget(self.equips_table)
        center_vbox.addWidget(equip_group)

        # Inventory Group
        inv_group = QGroupBox("Inventory")
        inv_layout = QVBoxLayout(inv_group)
        inv_layout.setSpacing(2)  # Reduce spacing
        inv_layout.setContentsMargins(0, 0, 0, 0)  # Reduce margins
        self.inventory_table = QTableWidget(0, 2) # Dynamic rows
        self.inventory_table.setHorizontalHeaderLabels(["Item", "Qty"])
        self.inventory_table.verticalHeader().setVisible(False)
        self.inventory_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.inventory_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.inventory_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # Disable selection
        self.inventory_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.inventory_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # Allow Inventory to expand
        self.inventory_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # Reduce header height
        self.inventory_table.horizontalHeader().setFixedHeight(20)
        # Make rows more compact
        self.inventory_table.verticalHeader().setDefaultSectionSize(20)
        inv_layout.addWidget(self.inventory_table)
        center_vbox.addWidget(inv_group, 1) # Give it a stretch factor to expand

        # Encumbrance Bar
        encum_label = QLabel("Encumbrance")
        center_vbox.addWidget(encum_label)
        self.encum_bar = QProgressBar()
        self.encum_bar.setFormat("%v/%m cubits") # Show value/max
        self.encum_bar.setTextVisible(True)
        center_vbox.addWidget(self.encum_bar)
        # No stretch at the end to allow panels to fill space

        # == Right Column (Derecha) ==
        right_vbox = QVBoxLayout()
        top_hbox.addLayout(right_vbox)
        right_vbox.setSpacing(2)

        # Plot Development Group
        plot_group = QGroupBox("Plot Development")
        plot_layout = QVBoxLayout(plot_group)
        plot_layout.setSpacing(2)  # Reduce spacing
        plot_layout.setContentsMargins(0, 0, 0, 0)  # Reduce margins
        self.plots_list = QListWidget() # Simpler than table for single column
        # Disable selection
        self.plots_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.plots_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.plots_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        plot_layout.addWidget(self.plots_list)
        right_vbox.addWidget(plot_group, 1) # Give it a stretch factor to expand

        # Plot Bar
        self.plot_bar = QProgressBar()
        self.plot_bar.setFormat("%p%")
        self.plot_bar.setTextVisible(True)
        right_vbox.addWidget(self.plot_bar)

        # Quests Group
        quest_group = QGroupBox("Quests")
        quest_layout = QVBoxLayout(quest_group)
        quest_layout.setSpacing(2)  # Reduce spacing
        quest_layout.setContentsMargins(0, 0, 0, 0)  # Reduce margins
        self.quests_list = QListWidget()
        # Disable selection
        self.quests_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.quests_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.quests_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        quest_layout.addWidget(self.quests_list)
        right_vbox.addWidget(quest_group, 2) # Give it a larger stretch factor to expand more

        # Quest Bar
        self.quest_bar = QProgressBar()
        self.quest_bar.setFormat("%p% complete")
        self.quest_bar.setTextVisible(True)
        right_vbox.addWidget(self.quest_bar)
        # No stretch at the end to allow panels to fill space

        # == Bottom Area ==
        self.kill_label = QLabel("Loading...")
        self.kill_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.kill_label.setStyleSheet("font-weight: bold;")
        main_layout.addWidget(self.kill_label)

        self.task_bar = QProgressBar()
        self.task_bar.setFormat("%p%")
        self.task_bar.setTextVisible(True)
        main_layout.addWidget(self.task_bar)

        # --- Set Column Widths ---
        # Adjust stretch factors for better space utilization
        # These values determine how the available width is distributed
        # between the three columns
        top_hbox.setStretchFactor(left_vbox, 20) # Left column (Character, Stats, Spells)
        top_hbox.setStretchFactor(center_vbox, 27) # Center column (Equipment, Inventory)
        top_hbox.setStretchFactor(right_vbox, 20) # Right column (Plot, Quests) - give more space


    def _tick(self):
        current_time = time.monotonic() * 1000
        elapsed = current_time - self.last_tick_time
        # Clamp elapsed time to avoid large jumps if paused/lagged
        elapsed = max(0, min(elapsed, 200)) # Clamp between 0 and 200ms
        self.last_tick_time = current_time

        game.process_tick(self.game_state, elapsed)
        self.update_ui()

        # Auto-save
        self.save_countdown -= 1
        if self.save_countdown <= 0:
            game.save_game(self.game_state)
            self.save_countdown = SAVE_INTERVAL_SEC * (1000 / TICK_INTERVAL_MS)


    def update_ui(self):
        # Update Traits Table
        for i, trait_name in enumerate(game.TRAITS):
            value = game.get_trait(self.game_state, trait_name)
            item = self.traits_table.item(i, 1)
            if item: item.setText("  " + str(value))  # Add left indentation
            else:
                item = QTableWidgetItem("  " + str(value))  # Add left indentation
                self.traits_table.setItem(i, 1, item)

        # Update Stats Table
        for i, stat_name in enumerate(game.STATS):
            value = game.get_stat(self.game_state, stat_name)
            item = self.stats_table.item(i, 1)
            if item: item.setText("  " + str(value))  # Add left indentation
            else:
                item = QTableWidgetItem("  " + str(value))  # Add left indentation
                self.stats_table.setItem(i, 1, item)

        # Update Progress Bars
        for bar_id, bar_widget in [("Exp", self.exp_bar), ("Encum", self.encum_bar),
                                   ("Plot", self.plot_bar), ("Quest", self.quest_bar),
                                   ("Task", self.task_bar)]:
            bar_data = self.game_state.get(f"{bar_id}Bar", {})
            bar_widget.setMaximum(bar_data.get("max", 1))
            bar_widget.setValue(int(bar_data.get("position", 0))) # Use int for progress bar value
            bar_widget.setToolTip(bar_data.get("hint", ""))
            # Custom format for different bars
            if bar_id == "Encum": # Encumbrance bar shows current/max cubits
                bar_widget.setFormat(f"{int(bar_data.get('position', 0))}/{int(bar_data.get('max', 1))} cubits")
            elif bar_id == "Quest": # Quest bar shows percentage complete
                bar_widget.setFormat(f"{bar_data.get('percent', 0)}% complete")
            elif bar_id == "Exp": # Experience bar shows hint text + percentage
                hint = bar_data.get('hint', '')
                if hint: # Extract the XP needed part from the hint
                    xp_needed = hint.split(' XP needed')[0]
                    bar_widget.setFormat(f"{xp_needed} XP needed - {bar_data.get('percent', 0)}%")
                else: bar_widget.setFormat(f"{bar_data.get('percent', 0)}%")
            elif bar_id == "Plot":
                # Plot bar shows hint text + percentage
                hint = bar_data.get('hint', '')
                if hint: bar_widget.setFormat(f"{hint} - {bar_data.get('percent', 0)}%")
                else: bar_widget.setFormat(f"{bar_data.get('percent', 0)}%")
            else: # Task uses percentage only
                bar_widget.setFormat(f"{bar_data.get('percent', 0)}%")


        # Update Spells Table
        spells = self.game_state.get("Spells", [])
        self.spells_table.setRowCount(len(spells))
        for i, (name, level) in enumerate(spells):
            item_name = self.spells_table.item(i, 0)
            item_level = self.spells_table.item(i, 1)
            if not item_name:
                item_name = QTableWidgetItem()
                self.spells_table.setItem(i, 0, item_name)
            if not item_level:
                item_level = QTableWidgetItem()
                item_level.setTextAlignment(Qt.AlignmentFlag.AlignCenter) # Center Roman numerals
                self.spells_table.setItem(i, 1, item_level)
            item_name.setText("  " + name)  # Add left indentation
            item_level.setText(level)  # Keep centered Roman numerals as is

        # Update Equipment Table
        for i, equip_slot in enumerate(game.EQUIPS):
            item_name = game.get_equip(self.game_state, equip_slot)
            item_widget = self.equips_table.item(i, 1)
            if item_widget: item_widget.setText("  " + item_name)  # Add left indentation
            else:
                item = QTableWidgetItem("  " + item_name)  # Add left indentation
                self.equips_table.setItem(i, 1, item)

        # Update Inventory Table
        inventory = self.game_state.get("Inventory", [])
        self.inventory_table.setRowCount(len(inventory))
        for i, (name, qty) in enumerate(inventory):
            item_name = self.inventory_table.item(i, 0)
            item_qty = self.inventory_table.item(i, 1)
            if not item_name:
                item_name = QTableWidgetItem()
                self.inventory_table.setItem(i, 0, item_name)
            if not item_qty:
                item_qty = QTableWidgetItem()
                item_qty.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter) # Right align with indentation
                self.inventory_table.setItem(i, 1, item_qty)
            item_name.setText("  " + name)  # Add left indentation
            item_qty.setText(str(qty) + "  ")  # Add right indentation

        # Update Plots List (Show all acts up to current, like in web version)
        self.plots_list.clear()
        current_act = self.game_state.get("act", 0)

        # Add all acts from Prologue (act 0) to current act (max 99 acts)
        for i in range(max(0, current_act-99), current_act + 1):
            if i == 0: act_str = "Prologue"
            else: # Convert act number to Roman numeral
                act_str = f"Act {game.to_roman(i)}"

            # Add icon based on status
            if i < current_act:  # Completed act
                item = QListWidgetItem("  ✓  " + act_str)  # Checkmark for completed
            elif i == current_act:  # Current act
                item = QListWidgetItem("  ►  " + act_str)  # Triangle for current
            else:  # Future act (shouldn't happen normally)
                item = QListWidgetItem("     " + act_str)  # Just indentation

            self.plots_list.addItem(item)

        # Only scroll to the bottom when a new act is added
        current_act = self.game_state.get("act", 0)
        previous_act = getattr(self, "_previous_act", 0)
        if current_act > previous_act:
            self.plots_list.scrollToBottom()
            self._previous_act = current_act

        # Update Quests List
        quests = self.game_state.get("Quests", [])
        old_quest_count = self.quests_list.count()
        self.quests_list.clear()

        # Get current quest progress
        quest_bar_data = self.game_state.get("QuestBar", {})
        quest_percent = quest_bar_data.get("percent", 0)  # Used below for quest completion status

        for i, quest_desc in enumerate(quests):
            # Add icon based on status
            if i < len(quests) - 1:  # Completed quests
                item = QListWidgetItem("  ✓  " + quest_desc)  # Checkmark for completed
            else:  # Current quest
                item = QListWidgetItem("  ►   " + quest_desc)  # Triangle for current

            self.quests_list.addItem(item)

        # Only scroll to bottom if new quests were added
        if len(quests) > old_quest_count:
            self.plots_list.scrollToBottom() # Show latest act
            self.quests_list.scrollToBottom() # Show latest quest

        # Update Kill Label
        self.kill_label.setText(self.game_state.get("kill", ""))

    def closeEvent(self, event):
        """Handle window closing."""
        self.timer.stop()
        # Automatically save on close
        saved = game.save_game(self.game_state)
        if not saved:
             # Optional: Ask user if they want to quit anyway if save failed
             reply = QMessageBox.warning(self, "Save Failed",
                                         "Could not save the game. Quit anyway?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)
             if reply == QMessageBox.StandardButton.No:
                  event.ignore()
                  self.timer.start(TICK_INTERVAL_MS) # Restart timer if not quitting
                  return

        event.accept() # Proceed with closing
        # After closing, we might want to show the roster again
        # This requires more application structure (e.g., a central controller)
        # For now, just exit.
        QApplication.instance().quit()

    def _on_color_scheme_selected(self, checked: bool, scheme_index: int):
        """Handles color scheme selection."""
        if not checked: return

        # Apply the selected color scheme
        app = QApplication.instance()
        app.styleHints().setColorScheme(Qt.ColorScheme(scheme_index))

        # Update actions
        for action in self.color_scheme_actions:
            action.setChecked(action.data() == scheme_index)

    def _on_style_changed(self, style_name: str):
        """Handles style selection."""
        try:
            # Apply the selected style
            app = QApplication.instance()
            app.setStyle(QStyleFactory.create(style_name))

            # Update global style theme
            global STYLE_SELECTED_THEME
            STYLE_SELECTED_THEME = style_name

            # Update actions
            for action in self.style_actions:
                action.setChecked(action.text() == style_name)

        except Exception as e:
            QMessageBox.critical(self, "Style Error", f"Error applying {style_name} style: {str(e)}")

# --- About Dialog ---

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Progress Quest TINS Edition")
        self.setModal(True)
        self.resize(600, 400)

        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("Progress Quest TINS Edition")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # License text
        license_text = QTextEdit()
        license_text.setReadOnly(True)

        # The license file
        license_content = """MIT License

Copyright (c) 2002-2024 Eric Fredricksen
Converted to Python by 2025 fernicar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

        license_text.setText(license_content)
        layout.addWidget(license_text)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

# --- New Character Dialog ---

class NewCharacterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Progress Quest - Roll One Up")
        self.setModal(True)
        self.new_game_state = None # To store the created character state
        self.rolled_stats = {}
        self.stat_seed_history = []

        self._init_ui()
        self._reroll() # Initial roll

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Name Row
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter character name")
        name_layout.addWidget(self.name_input)
        random_name_button = QPushButton("?")
        random_name_button.setFixedWidth(30)
        random_name_button.clicked.connect(self._random_name)
        name_layout.addWidget(random_name_button)
        layout.addLayout(name_layout)

        # Main Content Row (Races, Classes/Stats)
        content_layout = QHBoxLayout()
        layout.addLayout(content_layout)

        # Races Group
        races_group = QGroupBox("Race")
        self.races_layout = QVBoxLayout(races_group)
        self.race_radios = {}
        for i, (name, bonuses) in enumerate(game.RACES):
            radio = QRadioButton(name)
            self.races_layout.addWidget(radio)
            self.race_radios[name] = radio
            if i == 0: radio.setChecked(True) # Default check first race
        self.races_layout.addStretch(1)
        content_layout.addWidget(races_group)

        # Center Column (Classes + Stats)
        center_col_layout = QVBoxLayout()
        content_layout.addLayout(center_col_layout)

        # Classes Group
        classes_group = QGroupBox("Class")
        self.classes_layout = QVBoxLayout(classes_group)
        self.class_radios = {}
        for i, (name, bonuses) in enumerate(game.KLASSES):
            radio = QRadioButton(name)
            self.classes_layout.addWidget(radio)
            self.class_radios[name] = radio
            if i == 0: radio.setChecked(True) # Default check first class
        self.classes_layout.addStretch(1)
        center_col_layout.addWidget(classes_group)

        # Stats Group
        stats_group = QGroupBox("Stats")
        stats_group_layout = QVBoxLayout(stats_group)
        self.stat_labels = {}
        grid = QVBoxLayout() # Using VBox for simplicity like JS layout
        for stat_name in game.PRIME_STATS:
            row = QHBoxLayout()
            row.addWidget(QLabel(f"{stat_name}:"))
            self.stat_labels[stat_name] = QLabel("0")
            self.stat_labels[stat_name].setFixedWidth(30)
            self.stat_labels[stat_name].setAlignment(Qt.AlignmentFlag.AlignRight)
            row.addWidget(self.stat_labels[stat_name])
            row.addStretch(1)
            grid.addLayout(row)

        # Total Row
        total_row = QHBoxLayout()
        total_row.addWidget(QLabel("Total:"))
        self.stat_labels["Total"] = QLabel("0")
        self.stat_labels["Total"].setFixedWidth(30)
        self.stat_labels["Total"].setAlignment(Qt.AlignmentFlag.AlignRight)
        self.stat_labels["Total"].setStyleSheet("font-weight: bold;")
        total_row.addWidget(self.stat_labels["Total"])
        total_row.addStretch(1)
        grid.addLayout(total_row)
        grid.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)) # Spacer

        # Roll Buttons
        roll_button_layout = QHBoxLayout()
        reroll_button = QPushButton("Roll")
        reroll_button.clicked.connect(self._reroll)
        self.unroll_button = QPushButton("Unroll")
        self.unroll_button.clicked.connect(self._unroll)
        self.unroll_button.setEnabled(False)
        roll_button_layout.addStretch(1)
        roll_button_layout.addWidget(reroll_button)
        roll_button_layout.addWidget(self.unroll_button)
        roll_button_layout.addStretch(1)
        grid.addLayout(roll_button_layout)

        stats_group_layout.addLayout(grid)
        center_col_layout.addWidget(stats_group)

        # --- Bottom Buttons ---
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        sold_button = QPushButton("Sold!")
        sold_button.clicked.connect(self._accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(sold_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self._random_name() # Generate initial random name

    def _random_name(self):
        self.name_input.setText(game.generate_name())

    def _update_stat_display(self):
        if not self.rolled_stats: return
        total = 0
        for stat_name in game.PRIME_STATS:
            val = self.rolled_stats.get(stat_name, 0)
            self.stat_labels[stat_name].setText(str(val))
            total += val
        self.stat_labels["Total"].setText(str(total))

        # Color coding based on total (approximate JS colors)
        color = "white"     # Default color for normal stat totals (58-68)
        if total >= 75: color = "red" # Exceptional stats
        elif total > 68: color = "yellow" # Above average stats
        elif total <= 50: color = "grey" # Poor stats
        elif total < 58: color = "silver" # Below average stats
        self.stat_labels["Total"].setStyleSheet(f"background-color: {color}; color: black; font-weight: bold;")

    def _reroll(self):
        if self.rolled_stats: # Don't store initial empty state
            self.stat_seed_history.append(self.rolled_stats.get("seed"))
        self.rolled_stats = game.roll_stats()
        self._update_stat_display()
        self.unroll_button.setEnabled(bool(self.stat_seed_history))

    def _unroll(self):
        if not self.stat_seed_history: return
        last_seed = self.stat_seed_history.pop()
        game.set_random_state(last_seed) # Restore state before the roll
        self.rolled_stats = game.roll_stats() # Re-roll with that state
        self._update_stat_display()
        self.unroll_button.setEnabled(bool(self.stat_seed_history))

    def _get_selected_radio(self, radio_dict):
        for name, radio in radio_dict.items():
            if radio.isChecked(): return name
        return None

    def _accept(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing Name", "Please enter a character name.")
            return

        race = self._get_selected_radio(self.race_radios)
        klass = self._get_selected_radio(self.class_radios)

        if not race or not klass:
            QMessageBox.warning(self, "Selection Error", "Please select a race and class.")
            return # Should not happen with default checks

        # Check if character name already exists
        save_filename = f"{name}.pqw"
        if (game.SAVE_DIR / save_filename).exists():
             reply = QMessageBox.question(self, "Character Exists",
                                          f"A character named '{name}' already exists. Overwrite?",
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                          QMessageBox.StandardButton.No)
             if reply == QMessageBox.StandardButton.No: return

        self.new_game_state = game.create_new_character(name, race, klass, self.rolled_stats)
        # Save the newly created character immediately
        if game.save_game(self.new_game_state, save_filename):
            super().accept() # Close dialog if save successful
        else: QMessageBox.critical(self, "Save Error", f"Failed to save new character '{name}'.")


# --- Main Execution ---

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Force style for consistent look
    app.setStyle(QStyleFactory.create(STYLE_SELECTED_THEME))
    
    # Set color scheme to Auto by default
    app.styleHints().setColorScheme(Qt.ColorScheme.Unknown)  # Auto/Unknown = system default
    
    # Try to find the most recent .pqw file
    recent_file = find_most_recent_pqw_file()

    if recent_file: # Load the most recent game
        game_state = game.load_game(recent_file)
        if game_state:
            main_win = MainWindow(game_state)
            main_win.show()
        else: # If loading fails, show new character dialog
            dialog = NewCharacterDialog()
            if dialog.exec():
                # Create and show main window with new character
                main_win = MainWindow(dialog.new_game_state)
                main_win.show()
            else: sys.exit(0) # User canceled, exit application
    else: # No save files found, show new character dialog
        dialog = NewCharacterDialog()
        if dialog.exec():
            # Create and show main window with new character
            main_win = MainWindow(dialog.new_game_state)
            main_win.show()
        else: sys.exit(0) # User canceled, exit application

    sys.exit(app.exec())
