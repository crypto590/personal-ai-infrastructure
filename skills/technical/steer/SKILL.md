---
name: steer
description: macOS GUI automation CLI for agents. Provides eyes and hands on the local Mac via screenshots, OCR, accessibility tree traversal, mouse/keyboard control, and window management.
key_info: "Binary at ~/.claude/apps/steer/.build/debug/steer. Requires Accessibility + Screen Recording permissions in System Settings > Privacy & Security. Always focus app first, then observe, then act."
metadata:
  last_reviewed: 2026-03-17
  review_cycle: 90
---

# Steer — macOS GUI Automation

Steer is a Swift CLI that gives agents direct control over the macOS GUI. It uses native Apple APIs: `AXUIElement` for accessibility, `CGEvent` for input, `CGWindowListCreateImage` for screenshots, and Vision framework for OCR.

## Binary Location

```
~/.claude/apps/steer/.build/debug/steer
```

Add to PATH or invoke with full path. To install system-wide:
```bash
cp ~/.claude/apps/steer/.build/debug/steer /usr/local/bin/steer
```

## Required Permissions

Before first use, grant both permissions in System Settings > Privacy & Security:
- **Accessibility** — required for reading UI elements and controlling apps
- **Screen Recording** — required for taking screenshots

Running `steer see` will trigger the Accessibility permission prompt automatically. The tool will print a message if permissions are missing.

## Core Commands

### see — Capture screenshot + element map
```bash
steer see                          # frontmost app
steer see --app Safari             # specific app
steer see --screen 0               # full screen capture (screen index from 'steer screens')
steer see --ocr                    # fall back to OCR if AX tree is empty (Electron apps)
steer see --role button            # filter to buttons only
steer see --json                   # machine-readable JSON output
```
Output: snapshot ID, screenshot path, list of elements with IDs like B1, T2, S3.

### ocr — Extract text via Vision framework
```bash
steer ocr                          # OCR frontmost app
steer ocr --store                  # save results as snapshot so click --on works
steer ocr --app "Slack" --store    # OCR specific app and store
steer ocr --screen 0 --store       # OCR full screen and store
steer ocr --confidence 0.7         # raise minimum confidence threshold
steer ocr --json                   # JSON output
```
Use `--store` whenever you need to click on OCR-detected text by label. This assigns stable IDs (O1, O2, ...) to each text region.

### click — Click elements or coordinates
```bash
steer click --on B1                # click by element ID from last snapshot
steer click --on "Save"            # click by label text (partial match)
steer click --x 400 --y 300        # click by absolute coordinates
steer click --on B1 --double       # double-click
steer click --on B1 --right        # right-click
steer click --x 400 --y 300 --screen 1   # coordinates relative to screen 1
steer click --on B1 --modifier cmd       # click with Cmd held
```

### type — Type text
```bash
steer type "Hello world"           # type into currently focused element
steer type "search query" --into T1   # click T1 to focus, then type
steer type "new text" --into T1 --clear  # clear field first (Cmd+A, Delete), then type
```

### hotkey — Keyboard shortcuts
```bash
steer hotkey cmd+s                 # save
steer hotkey cmd+shift+n           # new window (app-dependent)
steer hotkey return                # press Enter
steer hotkey escape                # press Escape
steer hotkey tab                   # press Tab
steer hotkey cmd+tab               # switch apps
steer hotkey cmd+w                 # close tab/window
steer hotkey cmd+q                 # quit app
```
Supported modifiers: `cmd`, `shift`, `alt`/`option`, `ctrl`
Supported keys: `return`, `enter`, `tab`, `space`, `delete`, `backspace`, `escape`, `esc`, arrow keys (`left`, `right`, `up`, `down`), function keys (`f1`-`f12`), `home`, `end`, `pageup`, `pagedown`, `forwarddelete`, plus all alphanumeric keys.

### scroll — Scroll content
```bash
steer scroll down                  # scroll down 3 lines (default)
steer scroll up 5                  # scroll up 5 lines
steer scroll left 2
steer scroll right 2
```

### drag — Drag and drop
```bash
steer drag --from B1 --to B2                        # drag between elements
steer drag --from-x 100 --from-y 200 --to-x 400 --to-y 200   # drag by coordinates
steer drag --from "item" --to "folder" --steps 30   # more intermediate points = smoother
```

### focus — Inspect focused element
```bash
steer focus                        # show focused element in frontmost app
steer focus --app Terminal         # show focused element in specific app
steer focus --json
```

### find — Search elements in last snapshot
```bash
steer find "Save"                  # partial match (case-insensitive)
steer find "Save" --exact          # exact match only
steer find "button" --snapshot abc123   # search specific snapshot
```

### apps — List and manage running apps
```bash
steer apps                         # list all running apps (* = active)
steer apps list                    # same as above
steer apps launch Safari           # launch an app
steer apps activate Terminal       # bring app to foreground
```

### screens — List displays
```bash
steer screens                      # list all connected displays
steer screens --json               # JSON with index, resolution, origin, scale factor
```
Use the index values from this output with `--screen` in other commands.

### window — Manage windows
```bash
steer window list Safari           # list Safari windows with positions
steer window move Safari --x 0 --y 0         # move to top-left
steer window resize Safari --width 1200 --height 800
steer window minimize Safari
steer window restore Safari
steer window fullscreen Safari     # toggle fullscreen
steer window close Safari          # close frontmost window
```

### clipboard — Read and write clipboard
```bash
steer clipboard read               # print clipboard text
steer clipboard write "text here"  # copy text to clipboard
steer clipboard read --type image --file /tmp/clip.png   # save clipboard image
steer clipboard write --type image --file /path/to.png   # copy image to clipboard
```

### wait — Wait for app or element
```bash
steer wait --app Safari            # wait up to 10s for Safari to launch
steer wait --for "Submit" --app Safari   # wait for element to appear
steer wait --for B3 --timeout 30   # wait up to 30s, check every 0.5s
steer wait --for "Loading" --interval 1.0
```

## Element ID Scheme

The accessibility tree assigns stable IDs based on element role:
- `B1`, `B2`, ... — Buttons
- `T1`, `T2`, ... — TextFields, TextAreas, SearchFields, ComboBoxes
- `S1`, `S2`, ... — StaticText labels
- `C1`, `C2`, ... — CheckBoxes
- `R1`, `R2`, ... — RadioButtons
- `P1`, `P2`, ... — PopUpButtons (dropdowns)
- `L1`, `L2`, ... — Links
- `M1`, `M2`, ... — MenuItems, MenuBarItems
- `TB1`, `TB2`, ... — Tabs
- `I1`, `I2`, ... — Images
- `SL1`, `SL2`, ... — Sliders
- `E1`, `E2`, ... — Other elements
- `O1`, `O2`, ... — OCR-detected text regions (from `ocr --store`)

IDs are assigned per-snapshot and may change between snapshots as the UI changes.

## Key Workflows

### Focus-First Workflow (Standard)
Always bring the target app to focus before acting on it:
```bash
steer apps activate Safari         # 1. bring to foreground
steer see --app Safari             # 2. observe — get snapshot + element map
steer click --on "Address Bar"     # 3. act — use element ID or label
steer see --app Safari             # 4. verify — confirm the expected change happened
```

### OCR Workflow (Electron / Non-native Apps)
For apps where the AX tree is empty (VS Code, Slack, Chrome, Electron apps):
```bash
steer apps activate "Slack"
steer ocr --app "Slack" --store    # capture + store as snapshot
steer click --on "Send"            # click by OCR-detected label
```

### Type Into Field Workflow
```bash
steer see --app Safari
steer type "https://example.com" --into T1 --clear   # find address bar (T1), clear, type
steer hotkey return                # confirm
```

### Multi-Screen Workflow
```bash
steer screens                      # see index 0 = main, 1 = external
steer see --screen 1               # capture the external monitor
steer ocr --screen 1 --store       # OCR the external monitor
steer click --x 400 --y 200 --screen 1   # click at coords on screen 1
```

### Observation Loop Pattern
When automating a multi-step task, alternate between observe and act:
```bash
# Step 1: Observe initial state
steer see --app "MyApp"

# Step 2: Act based on what you see
steer click --on "Next"

# Step 3: Wait if there's a transition
steer wait --for "Step 2" --app "MyApp" --timeout 5

# Step 4: Observe new state
steer see --app "MyApp"

# Step 5: Act again
steer type "user@example.com" --into T1
```

## JSON Output

Every command supports `--json` for machine-readable output. Useful when chaining commands or processing output programmatically:

```bash
steer screens --json | python3 -c "import sys,json; [print(s['index'], s['name']) for s in json.load(sys.stdin)]"
steer see --app Safari --json | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['snapshot'])"
```

## Snapshot Storage

Snapshots (screenshots + element JSON) are stored in the system temp directory:
```
/tmp/steer/<snapId>.png    # screenshot
/tmp/steer/<snapId>.json   # element list
```

They persist across CLI invocations within the same session. The `find` command always searches the latest snapshot if no `--snapshot` flag is given.

## Common Patterns for Agents

### Pattern: Find and click a button
```bash
steer see --app "Safari"
steer click --on "Done"            # will search current snapshot by label
```

### Pattern: Fill a form
```bash
steer see --app "MyApp"
steer type "John" --into "First Name" --clear
steer type "Doe" --into "Last Name" --clear
steer type "john@example.com" --into "Email" --clear
steer click --on "Submit"
```

### Pattern: Verify an action worked
```bash
steer click --on "Save"
steer see --app "TextEdit"         # take new snapshot
steer find "Saved"                 # check if "Saved" indicator appeared
```

### Pattern: Navigate menus
```bash
steer apps activate "Finder"
steer hotkey cmd+shift+h           # go to Home folder
```

### Pattern: Copy and paste
```bash
steer click --on T1                # focus a text field
steer hotkey cmd+a                 # select all
steer hotkey cmd+c                 # copy
steer clipboard read               # verify clipboard content
```

## Troubleshooting

**"No snapshot" error**: Run `steer see` or `steer ocr --store` first.

**"App not found" error**: Check exact app name with `steer apps`. Use the name as it appears in the list.

**Empty element list from `see`**: The app may be Electron-based. Use `steer see --ocr` or `steer ocr --store` instead.

**Clicks landing in wrong position**: On Retina displays, coordinates are in logical points. Use `steer screens` to check scale factor. When using `--screen N` with `--x/--y`, the tool automatically converts from screenshot pixel coords to global logical coords.

**Permission errors**: Go to System Settings > Privacy & Security > Accessibility and add the terminal app running steer (Terminal, iTerm2, or the Claude Code process).
