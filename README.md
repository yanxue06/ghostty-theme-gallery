# ghostty-theme-gallery

Browse all 463 themes Ghostty ships with, rendered as actual terminals. Pick one, copy the config line.

**[Open the gallery →](https://yanxue06.github.io/ghostty-theme-gallery/)**

`ghostty +list-themes` gives you a TUI preview one theme at a time. This shows you all of them at once, side by side, so you can compare instead of cycling.

## What it does

- **463 themes as live previews.** Every card is a miniature terminal rendering the same prompt in that theme's real palette — not a swatch row, the actual thing you'll look at all day.
- **Filter by dark, light, or contrast.** 385 dark, 78 light, classified by computing WCAG relative luminance on each background. There's also a `contrast ≥ 7:1` filter for anyone who has to squint.
- **A full inspector.** Click any theme to see it large, exercising every field a Ghostty theme defines: background, foreground, cursor, cursor text, selection background, selection foreground, and all 16 ANSI slots — plus its foreground/background contrast ratio.
- **A pair builder.** Assign one theme to light and another to dark, and it emits the `theme = light:X,dark:Y` line that flips with your OS appearance. This is the part of Ghostty's theme syntax people miss most often.

No build step, no dependencies, no network calls. One HTML file with the palettes inlined — it works offline and from `file://`.

## Applying a theme

One line, in this file:

```
~/.config/ghostty/config
```

```ini
theme = TokyoNight Storm
```

Or a pair that follows your system appearance:

```ini
theme = light:Rose Pine Dawn,dark:Rose Pine Moon
```

Reload with `⌘⇧,`.

### If you use cmux

[cmux](https://github.com/manaflow-ai/cmux) embeds Ghostty, and it ships a CLI that does all of this for you:

```bash
cmux themes                      # current light/dark + the config path in use
cmux themes set "TokyoNight Storm"
cmux reload-config               # reloads Ghostty + cmux.json, refreshes panes in place
cmux config doctor               # validates cmux.json and prints why it failed
```

Four things cost me an hour, so they're worth writing down:

- **A theme change needs a reload.** Ghostty reads its config at startup, so editing the file does nothing to an already-running app — and nothing warns you. `cmux reload-config` refreshes panes in place; no restart.
- **cmux keeps its own Ghostty config.** `cmux themes` reports the active path, which is `~/Library/Application Support/com.cmuxterm.app/config.ghostty`, not the `~/.config/ghostty/config` that standalone Ghostty reads. Setting both is harmless if you use both apps.
- **The terminal theme is not a `cmux.json` key.** `browser.theme` in that file is the embedded web browser and only takes `system`/`light`/`dark`.
- **The chrome is separate.** A theme alone leaves the sidebar and tabs light:
  ```json
  { "app": { "appearance": "dark" } }
  ```

A malformed `cmux.json` is discarded **whole**, silently, with no error in the UI — one smart quote from a text editor makes every setting in it appear to do nothing. `cmux config doctor` catches it. On macOS, also worth turning the cause off: `defaults write -g NSAutomaticQuoteSubstitutionEnabled -bool false`.

## Keeping it current

Ghostty syncs its theme set from upstream weekly, so this snapshot drifts. To re-extract from your own install:

```bash
python3 scripts/extract.py                 # auto-detects Ghostty.app, cmux.app, or ~/.config/ghostty/themes
python3 scripts/extract.py /path/to/themes # or point it somewhere
```

It rewrites the palette array inside `index.html` in place and reports anything it skipped. Themes missing a background, a foreground, or any of the 16 ANSI slots are skipped rather than half-rendered — at the version here (Ghostty's set as bundled in cmux 0.64.17), nothing was skipped.

## Credits

The themes are not mine. Ghostty's built-in set is [synced from **mbadolato/iTerm2-Color-Schemes**](https://ghostty.org/docs/features/theme), which is where new themes should be contributed — Ghostty picks them up automatically. Every palette here is that project's work; this repo only reads and displays it.

The gallery code is MIT. See [LICENSE](LICENSE).
