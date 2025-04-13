# START OF FILE: character_dialog.py
# File: character_dialog.py
import sys
# No random import needed here anymore, using game RNG

from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QGroupBox, QGridLayout, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFontMetrics, QFont
# Import RNG and config data
from config_data import RACES, KLASSES, DARK_STYLESHEET, generate_name, randseed, Random

class NewCharacterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Progress Quest - New Character")
        self.setMinimumWidth(500)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)

        # --- Name ---
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        self.name_edit = QLineEdit()
        self.name_edit.setMaxLength(30)
        self.gen_name_button = QPushButton("?")
        # Calculate button size based on font metrics
        fm_button = QFontMetrics(self.gen_name_button.font())
        button_height = fm_button.height() + 8 # Add some padding
        self.gen_name_button.setFixedSize(button_height, button_height) # Square button
        self.gen_name_button.setToolTip("Generate random name")
        self.gen_name_button.clicked.connect(self.generate_random_name)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        name_layout.addWidget(self.gen_name_button)
        self.layout.addLayout(name_layout)

        # --- Race and Class ---
        selection_layout = QHBoxLayout()
        selection_layout.setSpacing(10)

        self.race_group = QGroupBox("Race")
        race_layout = QVBoxLayout()
        self.race_combo = QComboBox()
        self.race_combo.addItems(RACES.keys())
        fm = QFontMetrics(self.race_combo.font())
        # Adjust width calculation for padding
        max_width = max(fm.horizontalAdvance(race) for race in RACES.keys()) + fm.horizontalAdvance(" ") * 4 + 30 # Ensure space for dropdown arrow + padding
        self.race_combo.setMinimumWidth(max_width)
        race_layout.addWidget(self.race_combo)
        self.race_group.setLayout(race_layout)
        selection_layout.addWidget(self.race_group, 1) # Add stretch factor

        self.class_group = QGroupBox("Class")
        class_layout = QVBoxLayout()
        self.class_combo = QComboBox()
        self.class_combo.addItems(KLASSES.keys())
        max_width = max(fm.horizontalAdvance(klass) for klass in KLASSES.keys()) + fm.horizontalAdvance(" ") * 4 + 30 # Ensure space for dropdown arrow + padding
        self.class_combo.setMinimumWidth(max_width)
        class_layout.addWidget(self.class_combo)
        self.class_group.setLayout(class_layout)
        selection_layout.addWidget(self.class_group, 1) # Add stretch factor

        self.layout.addLayout(selection_layout)

        # --- Stats ---
        self.stats_group = QGroupBox("Stats")
        stats_layout = QGridLayout()
        stats_layout.setHorizontalSpacing(15)
        stats_layout.setVerticalSpacing(5)
        self.stat_labels = {}
        self.stat_values = {}
        self.current_stats = {} # Store the actual integer values
        self.stat_seeds = []    # Store RNG seeds for unroll
        self.stat_order = ["STR", "CON", "DEX", "INT", "WIS", "CHA"]

        for i, stat_name in enumerate(self.stat_order):
            self.stat_labels[stat_name] = QLabel(f"{stat_name}:")
            self.stat_values[stat_name] = QLabel("10")
            self.stat_values[stat_name].setObjectName("StatValueLabel") # For specific styling
            self.stat_values[stat_name].setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.stat_values[stat_name].setMinimumWidth(30)
            stats_layout.addWidget(self.stat_labels[stat_name], i, 0)
            stats_layout.addWidget(self.stat_values[stat_name], i, 1)

        self.total_label = QLabel("Total:")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.total_value = QLabel("60")
        self.total_value.setObjectName("StatValueLabel")
        self.total_value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        # Make total value bold for emphasis
        total_font = self.total_value.font()
        total_font.setBold(True)
        self.total_value.setFont(total_font)
        self.total_label.setFont(total_font) # Make label bold too

        stats_layout.addWidget(self.total_label, len(self.stat_order), 0)
        stats_layout.addWidget(self.total_value, len(self.stat_order), 1)

        # Add stretchable space before buttons
        stats_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding), len(self.stat_order) + 1, 0, 1, 2)

        self.roll_button = QPushButton("Roll")
        self.roll_button.setToolTip("Roll new stats (3d6 for each)")
        self.roll_button.clicked.connect(self.roll_stats)
        stats_layout.addWidget(self.roll_button, len(self.stat_order) + 2, 0, 1, 2)

        # Unroll button logic
        self.unroll_button = QPushButton("Unroll")
        self.unroll_button.setToolTip("Revert to previous stats roll")
        self.unroll_button.setEnabled(False)
        self.unroll_button.clicked.connect(self.unroll_stats)
        stats_layout.addWidget(self.unroll_button, len(self.stat_order) + 3, 0, 1, 2)

        self.stats_group.setLayout(stats_layout)
        selection_layout.addWidget(self.stats_group, 0) # No stretch factor for stats

        # --- Dialog Buttons ---
        button_layout = QHBoxLayout()
        button_layout.addStretch() # Push buttons to the right
        self.ok_button = QPushButton("Sold!")
        self.ok_button.setDefault(True)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(button_layout)

        # --- Initial State ---
        self.generate_random_name()
        self.roll_stats() # Perform initial roll

        # Set focus to name edit initially
        self.name_edit.setFocus()
        self.name_edit.selectAll()

    @Slot()
    def generate_random_name(self):
        """Generates a random name using the game's logic."""
        self.name_edit.setText(generate_name())

    def _update_stats_display(self):
        """Helper to update labels and total from self.current_stats."""
        total = 0
        best_stat_name = None
        best_stat_value = -1
        for stat_name in self.stat_order:
            val = self.current_stats.get(stat_name, 0)
            self.stat_values[stat_name].setText(str(val))
            total += val
            if val > best_stat_value:
                best_stat_value = val
                best_stat_name = stat_name
            elif val == best_stat_value: # Handle ties? JS version seems to just take the last one.
                 best_stat_name = stat_name

        self.total_value.setText(str(total))
        self.current_stats["best"] = best_stat_name if best_stat_name else "" # Store best stat name

        # Update total color based on JS logic
        self.total_value.setStyleSheet("") # Reset first
        if total >= (63 + 18): self.total_value.setStyleSheet("background-color: red;")
        elif total > (4 * 18): self.total_value.setStyleSheet("background-color: yellow; color: black;") # Need black text on yellow
        elif total <= (63 - 18): self.total_value.setStyleSheet("background-color: grey;")
        elif total < (3 * 18): self.total_value.setStyleSheet("background-color: silver; color: black;") # Need black text on silver

        # Enable/disable unroll button
        self.unroll_button.setEnabled(bool(self.stat_seeds))

    def _roll_3d6(self):
        """Rolls 3d6 using the game's Random function."""
        return Random(6) + Random(6) + Random(6) + 3 # Random(6) gives 0-5, add 1 for each die = +3

    @Slot()
    def roll_stats(self):
        """Rolls 3d6 for each stat using game RNG and updates the display."""
        # Store current seed *before* rolling new stats
        current_seed = randseed()
        if current_seed: # Don't store initial None seed if there was one
             self.stat_seeds.append(current_seed)
             # Limit history depth if desired
             if len(self.stat_seeds) > 20:
                  self.stat_seeds.pop(0)

        new_seed = randseed() # Get the *next* seed state for these rolls
        self.current_stats["seed"] = new_seed # Store seed associated with *these* stats

        for stat_name in self.stat_order:
            roll_value = self._roll_3d6()
            self.current_stats[stat_name] = roll_value

        # HP/MP Max calculation (matches newguy.js logic)
        self.current_stats['HP Max'] = Random(8) + 1 + (self.current_stats.get("CON", 0) // 6)
        self.current_stats['MP Max'] = Random(8) + 1 + (self.current_stats.get("INT", 0) // 6)

        self._update_stats_display()

    @Slot()
    def unroll_stats(self):
        """Reverts to the previous stat roll using the saved seed."""
        if self.stat_seeds:
            # Restore the previous seed state
            previous_seed = self.stat_seeds.pop()
            randseed(previous_seed) # Set the RNG state back

            # Re-roll using the restored seed state
            self.current_stats["seed"] = previous_seed # Store seed associated with *these* stats
            for stat_name in self.stat_order:
                 roll_value = self._roll_3d6()
                 self.current_stats[stat_name] = roll_value

            # HP/MP Max calculation
            self.current_stats['HP Max'] = Random(8) + 1 + (self.current_stats.get("CON", 0) // 6)
            self.current_stats['MP Max'] = Random(8) + 1 + (self.current_stats.get("INT", 0) // 6)

            self._update_stats_display()
        else:
             self.unroll_button.setEnabled(False) # Should be disabled anyway, but be sure


    def get_character_data(self):
        """Returns the selected character data if dialog was accepted."""
        if self.result() == QDialog.DialogCode.Accepted:
            name_text = self.name_edit.text().strip()
            if not name_text: # Ensure name is not empty
                name_text = generate_name() # Generate one if empty

            # Ensure required stats are present, even if 0
            for stat in self.stat_order + ["HP Max", "MP Max", "seed", "best"]:
                 if stat not in self.current_stats:
                      self.current_stats[stat] = 0 if stat not in ["seed", "best"] else ([] if stat=="seed" else "")


            return {
                "name": name_text,
                "race": self.race_combo.currentText(),
                "class": self.class_combo.currentText(),
                "stats": self.current_stats.copy() # Return a copy, includes HP/MP/seed/best
            }
        return None

# Example usage (for testing the dialog standalone)
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLESHEET) # Apply dark theme
    dialog = NewCharacterDialog()
    if dialog.exec():
        data = dialog.get_character_data()
        if data:
            print("Character Created:", data)
        else:
            print("Character data invalid.") # Should not happen if accepted
    else:
        print("Character creation cancelled.")
    sys.exit()
# END OF FILE: character_dialog.py