# START OF FILE: character_dialog.py
# File: character_dialog.py
import sys
import random
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QGroupBox, QGridLayout, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFontMetrics
from config_data import RACES, KLASSES, DARK_STYLESHEET, generate_name

class NewCharacterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Progress Quest - New Character")
        self.setMinimumWidth(500)
        # self.setModal(True) # Make it modal

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10) # Add spacing between elements

        # --- Name ---
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        self.name_edit = QLineEdit()
        self.name_edit.setMaxLength(30)
        self.gen_name_button = QPushButton("?")
        self.gen_name_button.setFixedSize(self.gen_name_button.sizeHint().height(), self.gen_name_button.sizeHint().height()) # Square button
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
        max_width = max(fm.horizontalAdvance(race) for race in RACES.keys()) + 40 # Add padding
        self.race_combo.setMinimumWidth(max_width)
        race_layout.addWidget(self.race_combo)
        self.race_group.setLayout(race_layout)
        selection_layout.addWidget(self.race_group, 1) # Add stretch factor

        self.class_group = QGroupBox("Class")
        class_layout = QVBoxLayout()
        self.class_combo = QComboBox()
        self.class_combo.addItems(KLASSES.keys())
        max_width = max(fm.horizontalAdvance(klass) for klass in KLASSES.keys()) + 40 # Add padding
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
        stats_layout.addWidget(self.total_label, len(self.stat_order), 0)
        stats_layout.addWidget(self.total_value, len(self.stat_order), 1)

        # Add stretchable space before buttons
        stats_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding), len(self.stat_order) + 1, 0, 1, 2)

        self.roll_button = QPushButton("Roll")
        self.roll_button.setToolTip("Roll new stats (3d6 for each)")
        self.roll_button.clicked.connect(self.roll_stats)
        stats_layout.addWidget(self.roll_button, len(self.stat_order) + 2, 0, 1, 2)

        # Note: Unroll button logic requires storing previous rolls, skipped for simplicity
        # self.unroll_button = QPushButton("Unroll")
        # self.unroll_button.setEnabled(False)
        # self.unroll_button.clicked.connect(self.unroll_stats)
        # stats_layout.addWidget(self.unroll_button, len(self.stat_order) + 3, 0, 1, 2)

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
        self.name_edit.setText(generate_name())

    def roll_d6(self):
        return random.randint(1, 6)

    @Slot()
    def roll_stats(self):
        """Rolls 3d6 for each stat and updates the display."""
        total = 0
        # self.previous_stats = self.current_stats.copy() # Store for unroll if needed
        for stat_name in self.stat_order:
            roll_value = self.roll_d6() + self.roll_d6() + self.roll_d6()
            self.stat_values[stat_name].setText(str(roll_value))
            self.current_stats[stat_name] = roll_value
            total += roll_value
        self.total_value.setText(str(total))

        # Reset style, then apply new style based on total
        self.total_value.setStyleSheet("") # Reset first
        if total >= (63 + 18): self.total_value.setStyleSheet("color: #FF6B6B;") # Bright Red
        elif total > (4 * 18): self.total_value.setStyleSheet("color: #FFD966;") # Yellow
        elif total <= (63 - 18): self.total_value.setStyleSheet("color: #A0A0A0;") # Grey
        elif total < (3 * 18): self.total_value.setStyleSheet("color: #C0C0C0;") # Silver
        # else: no specific style for average rolls

        # self.unroll_button.setEnabled(bool(self.previous_stats)) # Enable if there's something to unroll

    # def unroll_stats(self): # Example if unroll was implemented
    #     if self.previous_stats:
    #         total = 0
    #         self.current_stats = self.previous_stats.copy()
    #         for stat_name in self.stat_order:
    #             val = self.current_stats.get(stat_name, 0)
    #             self.stat_values[stat_name].setText(str(val))
    #             total += val
    #         self.total_value.setText(str(total))
    #         # Reset/apply style for total_value
    #         self.previous_stats = {} # Clear previous roll after unrolling
    #         self.unroll_button.setEnabled(False)


    def get_character_data(self):
        """Returns the selected character data if dialog was accepted."""
        if self.result() == QDialog.DialogCode.Accepted:
            name_text = self.name_edit.text().strip()
            if not name_text: # Ensure name is not empty
                name_text = "Adventurer"
            return {
                "name": name_text,
                "race": self.race_combo.currentText(),
                "class": self.class_combo.currentText(),
                "stats": self.current_stats.copy() # Return a copy
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