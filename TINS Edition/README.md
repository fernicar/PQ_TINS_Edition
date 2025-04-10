<!-- Zero Source Specification v1.0 -->
# Progress Quest (Zero Source Edition)

<!-- ZS:COMPLEXITY:MEDIUM -->
<!-- ZS:PLATFORM:WINDOWS -->
<!-- ZS:LANGUAGE:OBJECT_PASCAL -->
<!-- ZS:FRAMEWORK:DELPHI_VCL -->

## Description

Progress Quest is a satirical "zero-player" role-playing game. The user creates a character, and the game plays itself automatically. The character progresses through levels, undertakes quests, acquires items, and navigates plot acts without any user interaction beyond the initial setup and occasional viewing. The core gameplay loop involves watching progress bars fill up and reading humorous, procedurally generated status updates. It parodies common tropes found in fantasy RPGs and MMORPGs.

This application should replicate the original Progress Quest experience, including its single-player offline mode and optional multiplayer interactions with a central server (historically `progressquest.com`).

## Functionality

### Core Gameplay Loop (Automatic)

1.  **Character Progression:** The character automatically performs actions (tasks) over time. These tasks contribute to experience gain, quest completion, and plot advancement.
2.  **Task Execution:** The current task (e.g., "Executing kobold", "Heading to market") is displayed in the status bar, along with a progress bar showing time until completion. Task durations vary based on character level and task type.
3.  **Experience and Leveling:**
    *   A progress bar tracks experience points (XP), represented as time.
    *   Completing tasks (especially combat) grants XP.
    *   When the XP bar fills, the character levels up.
    *   Leveling up increases HP/MP maximums, grants stat points, and potentially a new spell. The XP required for the next level increases significantly.
4.  **Quest System:**
    *   Characters automatically undertake quests (e.g., "Exterminate the rats", "Seek the Holy Grail", "Deliver this boring item").
    *   Quest progress is tracked by a progress bar. Completing tasks advances quest progress.
    *   Completing a quest grants a reward (new spell, equipment, stat point, or item) and assigns a new quest.
5.  **Plot Development:**
    *   The game features multiple "Acts" (e.g., "Prologue", "Act I", "Act II", ... represented by Roman numerals).
    *   Plot progress is tracked by a progress bar, advanced by completing tasks.
    *   Completing an Act triggers a (simulated) cinematic/narrative transition and potentially grants rewards. Plot progression requires significantly more time than quests.
6.  **Combat (Simulated):**
    *   Characters automatically "fight" monsters appropriate to their level. Monsters are procedurally generated or drawn from quest targets.
    *   Monster names can include various modifiers (e.g., "Greater", "Undead", "Baby", "Giant", "Were-", "Rex").
    *   Combat resolution is time-based (filling the task progress bar).
    *   Defeating monsters can yield loot (generic items, special items, gold).
7.  **Economy and Inventory:**
    *   Characters automatically collect gold pieces and items.
    *   An inventory list displays items and quantities.
    *   An encumbrance bar tracks inventory load relative to character Strength (STR). Gold does not contribute to encumbrance.
    *   When encumbrance is high, the character automatically "heads to market" to sell items (oldest items first, excluding gold).
    *   Characters automatically attempt to "buy better equipment" when they have sufficient gold.
8.  **Equipment:** Characters automatically equip the best items they find for various slots (Weapon, Shield, Helm, Armor, etc.).

### User Interface

The main application window should have the following layout:

```
+-----------------------------------------------------------------------------+
| [ Character Sheet Panel ] | [ Equipment/Inventory Panel ] | [ Plot/Quest Panel ] |
|                           |                               |                      |
| - Traits (Name, Race,     | - Equipment List (Slot: Item) | - Plot Acts List     |
|   Class, Level) ListView  | - Eq. Progress Bar (Hidden?)  | - Plot Progress Bar  |
| - Stats (STR, CON, etc.)  |                               |                      |
|   ListView                | - Inventory Label             | - Quests Label       |
| - Exp. Label              | - Inventory List (Item: Qty)  | - Quests List        |
| - Experience Progress Bar | - Encumbrance Label           | - Quest Progress Bar |
| - Spell Book Label        | - Encumbrance Progress Bar    |                      |
| - Spells List (Name: Lvl) |                               |                      |
|                           |                               |                      |
+-----------------------------------------------------------------------------+
| [ Status Bar (Current Task...) ]                                            |
+-----------------------------------------------------------------------------+
| [ Task Progress Bar ]                                                       |
+-----------------------------------------------------------------------------+
```

*   **Panels:** Three main vertical panels.
*   **ListViews:** Used extensively to display character traits, stats, equipped items, inventory, known spells (with Roman numeral levels), plot acts, and quests. ListViews should be read-only, typically with columns for Category/Value or Item/Quantity. Plot/Quest lists should indicate completed items (e.g., checkmark icon, strikethrough).
*   **Progress Bars:** Visualize progress for the current Task, overall Experience, current Quest, current Plot Act, and Inventory Encumbrance. Hints should show details (e.g., "X/Y XP", "N% complete", "N seconds remaining").
*   **Status Bar:** Displays the character's current action or status messages.
*   **Window Title:** Should display "Progress Quest - [Character Name]" or similar.

### Character Creation

*   A dedicated dialog/form allows new character creation.
*   **Inputs:** Character Name (text input, max 30 chars), Race (Radio button selection from predefined list), Class (Radio button selection from predefined list).
*   **Stat Rolling:**
    *   Display stats: STR, CON, DEX, INT, WIS, CHA.
    *   Stats are rolled using a 3d6 method (sum of three 6-sided dice).
    *   "Roll" button generates new stats for all attributes.
    *   "Unroll" button reverts to the previous set of stats (maintains a history of recent rolls).
    *   Display the total points rolled. Visual feedback for exceptionally high/low rolls (e.g., color change).
*   **Name Generation:** A '?' button generates a random fantasy-style name.
*   **Account Info (Multiplayer):** If creating a character for a multiplayer realm requiring authentication, fields for Account and Password should be visible.
*   **Confirmation:** "Sold!" (OK) button confirms character creation, "Cancel" aborts.

### Game Management

*   **Startup Screen:** An initial screen presents options:
    *   New Game (Single Player)
    *   New Game (Multiplayer)
    *   Load Game
    *   Exit
    *   Link to `progressquest.com`.
*   **Saving:**
    *   The game state should be saved automatically periodically and upon closing the application.
    *   Save files use the `.pq` extension (e.g., `CharacterName.pq`).
    *   Save data should be compressed using ZLib.
    *   Optionally create a backup (`.bak`) of the previous save file when saving.
*   **Loading:** Allows loading a game state from a `.pq` file selected via a standard file open dialog.
*   **Minimizing:** Option to minimize the application to the system tray. Clicking the tray icon restores the window.
*   **Character Sheet Export:** Optional feature (e.g., via Ctrl+A or command-line flag) to display or export a plain text summary of the character sheet.

### Multiplayer Features

*   **Realm Selection:** If "New Game (Multiplayer)" is chosen, a dialog allows selecting a game "Realm" (server) from a list fetched from a central server (`progressquest.com/list.php`). Realms may have descriptions and specific requirements (e.g., password/access code, account needed for creation). Some realms might be directories leading to sub-realms.
*   **Account Login:** A separate login dialog may appear (or integrated into realm selection/creation) for realms requiring authentication (Username/Password). Supports optional proxy server configuration (Server/Port).
*   **Server Communication ("Bragging"):**
    *   Periodically (e.g., on level up, act completion) send character progress data (level, stats, best item/spell, current act, etc.) to a designated server URL (e.g., `progressquest.com/knoram.php`).
    *   Uses HTTP GET requests.
    *   Parameters are URL-encoded.
    *   Includes a basic checksum (`p=` parameter) generated using an LFSR algorithm based on other parameters and a secret passkey received on character creation.
    *   Handles server responses (e.g., displaying messages).
*   **Guilds:** Ability to set a guild affiliation (text input). This information is included in server communication.
*   **Motto:** Ability to set a character motto (text input), included in server communication.

## Technical Implementation

### Architecture

*   **Platform:** Native Windows Desktop GUI Application.
*   **Language:** Object Pascal (compatible with Delphi).
*   **Framework:** Delphi Visual Component Library (VCL) or a compatible framework (Lazarus LCL).
*   **Core Logic:** Primarily driven by a central timer (`TTimer`) that simulates the passage of time and triggers game events (task completion, XP gain, quest/plot progress).
*   **Modularity:** Separate units/modules for main game logic, character creation, configuration data, web communication, compression, startup/login/server selection forms.

### Data Structures

*   **Character State:**
    *   `Traits`: Name (String), Race (String), Class (String), Level (Integer).
    *   `Stats`: STR, CON, DEX, INT, WIS, CHA (Integers). HPMax, MPMax (Integers).
    *   `Experience`: Current XP (Integer, time-based), XP for next level (Integer, time-based).
    *   `Equipment`: A collection (e.g., list or dictionary) mapping equipment slots (String: Weapon, Shield, Helm, Hauberk, Brassairs, Vambraces, Gauntlets, Gambeson, Cuisses, Greaves, Sollerets) to item descriptions (String, e.g., "+2 Vorpal Hackbarm"). Track the "best" item for server reporting.
    *   `Inventory`: A collection (e.g., list or dictionary) mapping item names (String) to quantities (Integer). Gold stored as a specific item ("Gold Piece"). Item names can be complex (e.g., "Astral Fleece of Suffering").
    *   `Spells`: A collection (e.g., list or dictionary) mapping spell names (String) to spell levels (String, Roman numeral representation).
    *   `Quests`: A list of completed/current quest descriptions (String). Track progress (Integer/Percentage) for the current quest. Store reference to target monster/item if applicable.
    *   `Plot`: A list of completed/current plot act names (String, e.g., "Act VII"). Track progress (Integer/Percentage) for the current act.
    *   `Game State`: Current task description (String), task progress (Integer), task duration (Integer), encumbrance (Integer), max encumbrance (Integer). Multiplayer info: HostName, HostAddr, Login, Password, Passkey, Guild, Motto.
*   **Configuration Data (Crucial - Must be embedded or loadable):**
    *   `Weapons`: List of (Name: String, BaseValue: Integer).
    *   `Armors`: List of (Name: String, BaseValue: Integer).
    *   `Shields`: List of (Name: String, BaseValue: Integer).
    *   `OffenseAttrib`: List of (ModifierName: String, Bonus: Integer).
    *   `DefenseAttrib`: List of (ModifierName: String, Bonus: Integer).
    *   `OffenseBad`: List of (ModifierName: String, Penalty: Integer).
    *   `DefenseBad`: List of (ModifierName: String, Penalty: Integer).
    *   `Spells`: List of spell names (String).
    *   `BoringItems`: List of mundane item names (String).
    *   `Specials`: List of special item base names (String).
    *   `ItemAttrib`: List of special item prefixes (String).
    *   `ItemOfs`: List of special item suffixes (String, "of X").
    *   `Monsters`: List of (Name: String, Level: Integer, LootItem: String). '*' loot indicates generic drop.
    *   `MonsterMods`: List of (LevelAdjustment: Integer, Pattern: String). '*' in pattern is placeholder for base monster name.
    *   `Races`: List of (Name: String, StatBonuses: String).
    *   `Classes`: List of (Name: String, StatBonuses: String).
    *   `Titles`: List of standard titles (String).
    *   `ImpressiveTitles`: List of impressive titles (String).

### Algorithms

*   **Game Loop (Timer-based):**
    1.  Calculate elapsed time since last tick.
    2.  Increment current task progress.
    3.  If task complete:
        *   Resolve task outcome (grant XP, loot, potentially complete quest/plot step).
        *   Dequeue next queued task OR Determine next task based on game state (encumbrance -> market, low gold -> killing fields, sufficient gold -> buy equipment, otherwise -> killing fields).
        *   Start new task, resetting task progress bar.
    4.  If combat task completed:
        *   Increment XP bar. Check for Level Up.
        *   Increment Quest progress bar. Check for Quest Completion.
        *   Increment Plot progress bar. Check for Act Completion.
    5.  Update UI elements (progress bars, status text).
*   **Monster Generation:** Select base monster near character level. Apply modifiers from `MonsterMods` based on level difference vs character, potentially combining multiple mods (e.g., Sick+Young or Big+Special). Determine quantity based on level difference. Format name (Indefinite/Definite article, pluralization).
*   **Item Generation:**
    *   *Equipment:* Select base item (Weapon/Armor/Shield) near character level. Apply `Offense/Defense Attrib` or `Offense/Defense Bad` modifiers based on level difference until the difference is accounted for or max modifiers reached. Prepend numeric bonus/penalty if difference remains.
    *   *Special Items:* Combine random `ItemAttrib` + `Special` + `ItemOfs`.
    *   *Boring Items:* Pick randomly from `BoringItems` list.
*   **Stat Rolling:** Sum of 3d6 for each stat. Store previous roll for "Unroll".
*   **Name Generation:** Combine consonant/vowel/consonant parts randomly from predefined lists. Proper-case the result.
*   **Saving/Loading:** Use component streaming to serialize/deserialize relevant form/component properties. Apply ZLib compression/decompression to the stream. Handle file I/O and backup creation.
*   **Encumbrance:** Calculate as sum of quantities of all items in inventory *except* "Gold Piece". Max encumbrance = 10 + STR stat.
*   **Multiplayer Communication (Brag):** Construct URL with parameters. Calculate LFSR checksum using parameters and passkey. Send HTTP GET request. Parse simple pipe-delimited response.
*   **LFSR Checksum:** Implement the specific Linear Feedback Shift Register algorithm used in `Main.pas -> LFSR` function for generating the `p=` parameter.
*   **Roman Numerals:** Convert integers to/from Roman numerals for spell levels and plot acts.

### Persistence

*   **Save Files:** Primary state stored in `.pq` files in the application directory or user documents. Files are ZLib compressed binary streams (likely Delphi component streams).
*   **Backup Files:** Optional `.bak` files created by renaming the previous `.pq` file.
*   **Configuration:** Game content data (items, monsters, etc.) must be embedded within the application executable or loaded from external data files packaged with the application. (Original likely embedded in DFM resources).
*   **Settings:** Application settings (like tray behavior, export options) potentially stored in Windows Registry or an INI file.

### External Dependencies

*   **Web Server:** Requires access to `http://progressquest.com` (or a compatible server) for multiplayer features (server list, character creation validation, progress reporting/bragging).
*   **Libraries:** Standard Object Pascal runtime, VCL/LCL framework, ZLib library (like `ZLibEx.pas` provided). WinInet API or similar for HTTP communication. System Tray API.

## Style Guide

*   **Visual:** Functional, somewhat dated Windows GUI aesthetic. Standard VCL/LCL controls. Emphasis on readability of text in lists and progress bars.
*   **Tone:** Humorous, satirical, parodying RPG clichés in generated text (tasks, quests, items).
*   **Layout:** Structured panel layout as described in UI section.

## Performance Goals

*   Low CPU usage when idle or minimized. Timer interval should be reasonable (e.g., 100ms as in original).
*   Efficient handling of large lists (inventory, spells) although practical limits are unlikely to be hit in normal gameplay.
*   Network requests should be handled without freezing the UI (asynchronous if possible, though original might have been blocking).

## Accessibility Requirements

*   Basic keyboard navigation for controls (Tab, Enter).
*   Adherence to system color/font settings where possible. (Likely poor accessibility in the original, aim for standard control behavior).

## Testing Scenarios

*   Character creation completes successfully (Single/Multiplayer).
*   Game loads correctly from a saved `.pq` file.
*   Game saves correctly on exit.
*   Character levels up after appropriate time/XP gain.
*   Stats, HP/MP increase on level up.
*   Spells are learned on level up.
*   Quests are assigned, progress, and complete, granting rewards.
*   Plot acts progress and complete.
*   Equipment is automatically upgraded over time.
*   Inventory fills, character goes to market, inventory clears (except gold).
*   Encumbrance bar reflects inventory status.
*   Multiplayer: Realm list fetches, character creation succeeds (if applicable), "Brag" calls are sent periodically without error.
*   Minimize to tray and restore works correctly.
*   Character sheet export produces readable text output.