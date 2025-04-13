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
    *   Uses the web version savegame format (`.pqw` files).
    *   Window position and size remembered using `QSettings`.
*   **Dark Mode UI:** Built with PySide6, featuring a default dark theme for comfortable viewing during long progress sessions.
*   **Offline Focus:** This version does *not* include the original's multiplayer features (server communication, bragging, realm selection).

## Screenshots

**Main Window:**
`[Screenshot showing the three main panels: Character, Equipment/Inventory, Plot/Quests, and the bottom status/task bars]`
![app_capture0](https://github.com/fernicar/PQ_TINS_Edition/blob/main/images/app_capture0.png)

**Character Creation:**
`[Screenshot showing the character creation dialog with name, race/class selection, and stats]`
![app_capture1](https://github.com/fernicar/PQ_TINS_Edition/blob/main/images/app_capture1.png)

## Getting Started

### Prerequisites

*   Python 3.8 or higher recommended.
*   `pip` (Python package installer).

### Installation & Running

1.  **Clone or Download:**
    ```bash
    git clone https://github.com/fernicar/PQ_TINS_Edition.git
    cd PQ_TINS_Edition
    ```

2.  **Install Dependencies:**
    ```bash
    pip install PySide6
    ```

3.  **Run the Game:**
    ```bash
    python main.py
    ```

## Technology Stack

*   **Language:** Python 3
*   **GUI Framework:** PySide6 (The official Qt for Python project)
*   **Serialization:** `pickle` (for saving Python object state)
*   **Compression:** `zlib` (for compressing save files)
*   **Settings:** `QSettings` (for window geometry and last file path)

## File Structure

*   `main.py`: The main application file, setting up the PySide6 UI (`MainWindow`), managing the game timer, handling saving/loading, and connecting the UI to the game logic.
*   `game.py`: Core game logic including character creation, state management, save/load functionality, and game progression mechanics.
*   `resources/`: Directory containing theme files (dark_theme.qss, default_theme.qss)

## Saving and Loading

*   The game automatically attempts to load the most recent `.pqw` file found on startup.
*   If no save is found, it prompts for new character creation.
*   The game state is saved automatically:
    * Every minute during gameplay
    * When closing the application
    * When creating a new character
    * Manually through `File -> Save Game`
*   Save files use the `.pqw` format with the character's name (e.g., `CharacterName.pqw`)
*   Window size and position are saved using `QSettings`

## Technical Details

*   **Python:** Port of the original web version (HTML/JavaScript) logic to Python
*   **UI:** Built with PySide6, using QSS for styling and QSettings for window geometry
*   **Game Loop:** Uses QTimer with 50ms interval (matches original clock.js)
*   **Auto-Save:** Occurs every 60 seconds during gameplay
*   **Theme System:** 
    * Uses QSS stylesheets stored in `resources/` directory
    * Default dark theme is automatically created if missing
*   **Save Format:** Uses JSON format with base64 encoding
*   **State Management:**
    * Maintains PRNG state for consistent random generation
    * Tracks character stats, inventory, spells, quests, and plot progression
    * Automatically calculates "best" stats/spells/equipment

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/fernicar/PQ_TINS_Edition/issues) if you want to contribute.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/fernicar/PQ_TINS_Edition/blob/main/LICENSE) file for details.

## Acknowledgments

*   Special thanks to ScuffedEpoch for the [TINS](https://github.com/ScuffedEpoch/TINS) methodology and the initial example.
*   Thanks to Eric Fredricksen and the original [Progress Quest Web](https://bitbucket.org/grumdrig/pq-web) project contributors for the original game – you are a legend.
*   Thanks to the PySide6 development team and community for their libraries and documentation.
*   *(Your mention of AI assistants and VS Code extensions is fine here too if you wish to keep it)*
    *   Thanks to the AI assistants used during development for their contributions.
    *   Augment extension for VS Code.
    *   Tested LLM Gemini-1.5-pro from Google AI Studio.
