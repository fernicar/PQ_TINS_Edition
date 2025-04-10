# Progress Quest (Python/PySide6 Edition)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/fernicar/PQ_TINS_Edition/blob/main/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-PySide6-cyan.svg)](https://www.qt.io/qt-for-python)

A modern, offline, single-player implementation of the classic "zero-player" RPG, Progress Quest, built with Python and the PySide6 GUI framework. Watch your character automatically battle monsters, complete quests, level up, and acquire loot!

This version focuses on replicating the core single-player experience with a dark mode interface, inspired by the [TINS (There Is No Source)](https://github.com/ScuffedEpoch/TINS) methodology's focus on describing functionality.

## Key Features (Current Implementation)

*   **Character Creation:** Define your character's Name, Race, and Class. Roll (and re-roll) classic 3d6 stats.
*   **Automatic Gameplay Loop:** No user interaction required after character creation! The game plays itself.
    *   **Task Execution:** Watches progress bars fill as your character performs tasks like "Executing Slime", "Heading to market", or "Negotiating purchase".
    *   **Experience & Leveling:** Gain XP automatically over time. Level up to increase HP/MP, gain stat points, and potentially learn new spells.
    *   **Quest System:** Automatically accepts, progresses through, and completes randomly generated quests (Exterminate, Seek, Deliver, Fetch, Placate), earning rewards.
    *   **Plot Progression:** Advance through Acts ("Prologue", "Act I", etc.) by filling the plot progress bar over longer periods.
    *   **Simulated Combat:** Encounters appropriately (or inappropriately) leveled monsters with generated modifiers.
    *   **Economy & Inventory:** Collect gold and items (both boring and special). Automatically travels to market to sell loot when encumbered. Automatically attempts to buy better equipment when affordable.
    *   **Equipment:** Automatically generated equipment is equipped based on character level progression and quest/act rewards.
*   **Persistent State:** Game saves automatically on exit and loads the most recent save on startup.
    *   Uses `pickle` and `zlib` compression (`.pq` files).
    *   Automatic backup (`.bak`) creation on save.
    *   Window position and size remembered using `QSettings`.
*   **Dark Mode UI:** Built with PySide6, featuring a default dark theme for comfortable viewing during long progress sessions.
*   **Offline Focus:** This version does *not* include the original's multiplayer features (server communication, bragging, realm selection).

## Screenshots

**Main Window:**
`[Screenshot showing the three main panels: Character, Equipment/Inventory, Plot/Quests, and the bottom status/task bars]`
![app_capture0](https://github.com/fernicar/PQ_TINS_Edition/images/blob/main/app_capture0.png)

**Character Creation:**
`[Screenshot showing the character creation dialog with name, race/class selection, and stats]`
![app_capture1](https://github.com/fernicar/PQ_TINS_Edition/images/blob/main/app_capture1.png)

## Getting Started

### Prerequisites

*   Python 3.8 or higher recommended.
*   `pip` (Python package installer).

### Installation & Running

1.  **Clone or Download:** Get the source code files (`config_data.py`, `game_logic.py`, `character_dialog.py`, `main_window.py`).
    ```bash
    git clone https://github.com/fernicar/PQ_TINS_Edition.git
    cd PQ_TINS_Edition
    ```
    (Or download and extract the ZIP)

2.  **Create `requirements.txt`:** Create a file named `requirements.txt` in the same directory with the following content:
    ```txt
    PySide6
    ```

3.  **Install Dependencies:** Open a terminal or command prompt in the project directory and run:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Game:** Execute the main script from your terminal:
    ```bash
    python main_window.py
    ```

## Technology Stack

*   **Language:** Python 3
*   **GUI Framework:** PySide6 (The official Qt for Python project)
*   **Serialization:** `pickle` (for saving Python object state)
*   **Compression:** `zlib` (for compressing save files)
*   **Settings:** `QSettings` (for window geometry and last file path)

## File Structure

*   `config_data.py`: Holds static game data (items, monsters, spells, races, classes, etc.), helper functions (`plural`, `int_to_roman`), and the UI stylesheet.
*   `game_logic.py`: Contains the `GameLogic` class, encapsulating the character state, game rules, and the core automatic progression logic (tick loop).
*   `character_dialog.py`: Implements the `NewCharacterDialog` window for creating new characters.
*   `main_window.py`: The main application file, setting up the PySide6 UI (`MainWindow`), managing the game timer, handling saving/loading, and connecting the UI to the `GameLogic`.
*   `requirements.txt`: Lists the necessary Python packages (`PySide6`).

## Saving and Loading

*   The game automatically attempts to load the most recent save file (`.pq`) found on startup. It checks the path stored in settings first, then the application/working directory.
*   If no save is found, it prompts for new character creation.
*   The game state is saved automatically when you close the application. You can also manually save using `File -> Save Game`.
*   Save files (`.pq`) are Python `pickle` data compressed with `zlib`.
*   A backup (`.bak`) of the previous save is created automatically during the save process.
*   Window size, position, and splitter layout are saved using `QSettings` and restored on the next launch.

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/fernicar/PQ_TINS_Edition/issues) if you want to contribute.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/fernicar/PQ_TINS_Edition/blob/main/LICENSE) file for details.

## Acknowledgments

*   Special thanks to ScuffedEpoch for the [TINS](https://github.com/ScuffedEpoch/TINS) methodology and the initial example.
*   Thanks to Eric Fredricksen and the original [ProgressQuest](https://bitbucket.org/grumdrig/pq/src/master/) project contributors for the original game – you are a legend.
*   Thanks to the PySide6 development team and community for their libraries and documentation.
*   *(Your mention of AI assistants and VS Code extensions is fine here too if you wish to keep it)*
    *   Thanks to the AI assistants used during development for their contributions.
    *   Augment extension for VS Code.
    *   Tested LLM Gemini-1.5-pro from Google AI Studio.