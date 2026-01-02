# Tileborn ? Roadmap

This roadmap defines the steps to reach the **first playable version (v0.1)** of *Tileborn*. The focus is on **core gameplay**, **stability**, and **clear progression**, avoiding unnecessary scope creep.

---

## Phase 1 ? Foundations (DONE)

**Goal:** Have a functional technical base and clear project structure.

* [x] Logical resolution and camera system
* [x] Tile-based world
* [x] Basic HUD structure
* [x] Build mode toggle
* [x] Building placement preview
* [x] Resource system (wood, stone, food, gold)
* [x] Top bar with resources display
* [x] Hamburger menu with animated dropdown
* [x] Tooltip system for UI elements

---

## Phase 2 ? Core Gameplay Loop (v0.1 Target / IN PROGRESS)

**Goal:** Allow the player to play a simple but complete loop.

### Building & World

* [x] Place buildings only if enough resources
* [x] Deduct resources when building
* [x] Prevent building on invalid tiles
* [x] Visual feedback for invalid placement
* [x] Visual highlight when hovering tiles

* [ ] At least 3 buildings:

  * [x] House (now is just one tile, not a complete building)
  * [x] Sawmill (now is just one tile, not a complete building)
  * [ ] Storage / Warehouse

### Resources & Production

* [ ] Sawmill generates wood over time
* [ ] Houses increase population cap (i dont know if i'll do a pop cap or just something as "inhabitants needs housing" yet)
* [x] Basic resource tick/update system

### Game State

* [ ] Save game state in memory (single session)

---

## Phase 3 ? Interaction & Feedback

**Goal:** Make the game readable and pleasant to interact with.

* [ ] Click on placed buildings to show info panel
* [ ] Show building-specific data:

  * House: inhabitants
  * Sawmill: workers / production rate

* [ ] Simple sound effects (UI click, build, error)

---

## Phase 4 ? Polish for v0.1

**Goal:** Deliver a clean and stable first playable version.

* [ ] Pause menu
* [x] Save / Load placeholder (even if fake)
* [ ] Small balance pass on costs and production
* [ ] Bug fixing and cleanup
* [ ] FPS stability check

---

## Definition of v0.1 ? First Playable Version

The game is considered **playable** when:

* The player can gather resources
* Build structures
* See progression over time
* Understand what is happening without explanation

No advanced systems. No content overload, just something for the player fill that is playing a game.

---

## Post v0.1 (Future Ideas ? Not Now)


* Advanced AI / citizens behavior
* Combat or enemies
* Technology tree
* Multiple maps / biomes
* Save system
* Art polish / animations

---