# File: character_dialog.py
import sys
import random
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QGroupBox, QGridLayout, QSizePolicy
)
from PySide6.QtCore import Qt, Slot
from config_data import RACES, KLASSES, DARK_STYLESHEET, generate_name

class NewCharacterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Progress Quest - New Character")
        self.setMinimumWidth(500)

        self.layout = QVBoxLayout(self)

        # Name and Generation
        name_layout = QHBoxLayout()
        self.name_label = QLabel("Name:")
        self.name_edit = QLineEdit()
        self.name_edit.setMaxLength(30)
        self.gen_name_button = QPushButton("?")
        self.gen_name_button.setFixedSize(25, 25)
        self.gen_name_button.clicked.connect(self.generate_random_name)
        name_layout.addWidget(self.name_label)
        name_layout.addWidget(self.name_edit)
        name_layout.addWidget(self.gen_name_button)
        self.layout.addLayout(name_layout)

        # Race and Class Selection
        selection_layout = QHBoxLayout()
        self.race_group = QGroupBox("Race")
        self.race_layout = QVBoxLayout()
        self.race_combo = QComboBox()
        self.race_combo.addItems(RACES.keys())
        self.race_layout.addWidget(self.race_combo)
        self.race_group.setLayout(self.race_layout)
        selection_layout.addWidget(self.race_group)

        self.class_group = QGroupBox("Class")
        self.class_layout = QVBoxLayout()
        self.class_combo = QComboBox()
        self.class_combo.addItems(KLASSES.keys())
        self.class_layout.addWidget(self.class_combo)
        self.class_group.setLayout(self.class_layout)
        selection_layout.addWidget(self.class_group)
        self.layout.addLayout(selection_layout)

        # Stats Rolling
        self.stats_group = QGroupBox("Stats")
        self.stats_layout = QGridLayout()
        self.stat_labels = {}
        self.stat_values = {}
        self.stat_order = ["STR", "CON", "DEX", "INT", "WIS", "CHA"]
        for i, stat_name in enumerate(self.stat_order):
            self.stat_labels[stat_name] = QLabel(f"{stat_name}:")
            self.stat_values[stat_name] = QLabel("10") # Initial value
            self.stat_values[stat_name].setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.stat_values[stat_name].setMinimumWidth(30)
            self.stats_layout.addWidget(self.stat_labels[stat_name], i, 0)
            self.stats_layout.addWidget(self.stat_values[stat_name], i, 1)

        self.total_label = QLabel("Total:")
        self.total_value = QLabel("60")
        self.total_value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.stats_layout.addWidget(self.total_label, len(self.stat_order), 0)
        self.stats_layout.addWidget(self.total_value, len(self.stat_order), 1)

        self.roll_button = QPushButton("Roll")
        self.roll_button.clicked.connect(self.roll_stats)
        # self.unroll_button = QPushButton("Unroll") # Unroll is more complex, requires state saving
        # self.unroll_button.setEnabled(False)
        self.stats_layout.addWidget(self.roll_button, len(self.stat_order) + 1, 0, 1, 2)
        # self.stats_layout.addWidget(self.unroll_button, len(self.stat_order) + 2, 0, 1, 2)
        self.stats_group.setLayout(self.stats_layout)
        self.layout.addWidget(self.stats_group)

        # Dialog Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Sold!")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(button_layout)

        # Initial state
        self.generate_random_name()
        self.roll_stats()

    @Slot()
    def generate_random_name(self):
        self.name_edit.setText(generate_name())

    def roll_d6(self):
        return random.randint(1, 6)

    @Slot()
    def roll_stats(self):
        total = 0
        self.current_stats = {}
        for stat_name in self.stat_order:
            roll_value = self.roll_d6() + self.roll_d6() + self.roll_d6()
            self.stat_values[stat_name].setText(str(roll_value))
            self.current_stats[stat_name] = roll_value
            total += roll_value
        self.total_value.setText(str(total))
        # Add visual feedback for total score (optional)
        if total >= (63 + 18): self.total_value.setStyleSheet("color: red;")
        elif total > (4 * 18): self.total_value.setStyleSheet("color: yellow;")
        elif total <= (63 - 18): self.total_value.setStyleSheet("color: grey;")
        elif total < (3 * 18): self.total_value.setStyleSheet("color: silver;")
        else: self.total_value.setStyleSheet("") # Reset style


    def get_character_data(self):
        if self.result() == QDialog.DialogCode.Accepted:
            return {
                "name": self.name_edit.text(),
                "race": self.race_combo.currentText(),
                "class": self.class_combo.currentText(),
                "stats": self.current_stats
            }
        return None

# Example usage (for testing the dialog)
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLESHEET) # Apply dark theme
    dialog = NewCharacterDialog()
    if dialog.exec():
        data = dialog.get_character_data()
        print("Character Created:", data)
    else:
        print("Character creation cancelled.")
    sys.exit()