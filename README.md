# HiLo Pop

**HiLo Pop** is a Blender add-on for fast, clean **High/Low** naming and batch renaming of objects.

---

## What HiLo Pop does

### Naming on creation
The add-on adds mesh creation entries to **3D Viewport → Add → Mesh**:
- **N Plane**
- **N UV Sphere**

When creating an object you can:
- type a name — the add-on automatically ensures the **`_high`** suffix (e.g. `Rock_high`), or
- pick an existing **high-poly object** as a source — the new object name will be derived as **`*_low`** (e.g. `Rock_high → Rock_low`).

### Batch renaming (Rename Multi)
**Rename (Multi)** renames selected objects using a base name with an incrementing numeric suffix:
- `Name.001`, `Name.002`, …

### Quick High/Low suffix tools
The add-on can quickly normalize selected object names:
- **High (only name)** — set/replace the `*_high` suffix
- **Low (only name)** — set/replace the `*_low` suffix

---

## Where to find it in the UI

### Add menu entries
**3D Viewport → Add → Mesh**
- **N Plane**
- **N UV Sphere**

After running a command, a new object is created **at the 3D Cursor position** and named according to HiLo Pop rules.

### Pie menu
A **HiLo Pop** pie menu is also available and includes:
- High (only name)
- Low (only name)
- N Plane
- N UV Sphere
- Rename (Multi)

---

## Hotkey and Pie Menu

### Default hotkey
HiLo Pop supports calling its pie menu via a hotkey.  
Default hotkey: **Alt + Q**.

### How to change the hotkey
Settings are located at: **Edit → Preferences → Add-ons / Extensions → HiLo Pop**

You can:
- enable/disable the hotkey (**Enable Pie Hotkey**),
- record a new hotkey via **Record** (the add-on waits for a key press and stores Ctrl/Alt/Shift modifiers),
- reset the hotkey back to default via **Reset**.

---

## Settings

**Edit → Preferences → Add-ons / Extensions → HiLo Pop**
- **Popup Width** — dialog (popup) width when creating objects and entering names.
- **Pie Menu Hotkey** — hotkey enable/record/reset (default: Alt + Q).

---

## Installation and requirements

### Requirements
- **Blender 4.5.0+**

### Install via Extensions (from ZIP)

**Method 1 (recommended): Drag & Drop**
1) Drag and drop the add-on ZIP into the Blender window
2) Confirm installation if prompted

**Method 2: Preferences**
1) Open **Edit → Preferences**
2) Go to **Get Extensions** (if available)
3) Click **Install from Disk…** and select the add-on ZIP
4) Make sure the extension is enabled (if Blender didn’t enable it automatically)

---

## Author
Kyrivane

## License
GPL-3.0-or-later
