# iOS Shortcuts

A growing collection of iOS Shortcuts.

**[➜ Install page](https://shiebenaderet.github.io/ios-shortcuts/)** — tap-to-install from any iPhone.

Each shortcut installs via an iCloud link (iOS only accepts signed shortcuts, so downloading files from this repo won't work — use the links).

## Catalog

| Shortcut | What it does | Install |
|---|---|---|
| [View Archived](#view-archived) | Opens the newest archive.today snapshot of any webpage | [iCloud link](https://www.icloud.com/shortcuts/52aa5c15de554744956390e0f6287ccc) |

---

## View Archived

Opens the newest [archive.today](https://archive.ph) snapshot of any webpage, straight from the Safari share sheet or a copied link.

**How it works** — receives a URL (share sheet, or clipboard if run directly) and opens:

```
https://archive.ph/newest/<your URL>
```

- `/newest/` jumps to the most recent snapshot.
- If the page has never been archived, archive.today offers to save one on the spot.
- archive.ph, archive.is, and archive.md are mirrors — swap the domain if one is slow.
- Occasional CAPTCHAs on mobile/VPN connections are normal.

**Rebuild it yourself**

1. New shortcut → enable **Show in Share Sheet** (accept URLs and Safari web pages; "If there's no input" → **Get Clipboard**).
2. **Text** action: `https://archive.ph/newest/` followed by the *Shortcut Input* variable.
3. **Open URLs** action.

**Variant** — Wayback Machine version: same shortcut with `https://web.archive.org/web/` as the prefix.

---

<!-- Template for new entries:

## Shortcut Name

One-line description.

**How it works** — ...

**Rebuild it yourself**

1. ...

Then add a row to the Catalog table above.
-->

## Publishing a shortcut

iOS only installs *signed* shortcuts, so distribution always runs through an iCloud
link — a `.shortcut` file committed here can't be installed from GitHub.

1. On iPhone or iPad: **Shortcuts** app → long-press the shortcut → **Share** →
   **Copy iCloud Link**. (iCloud Drive must be on; the first share signs the shortcut.)
2. Paste the resulting `https://www.icloud.com/shortcuts/...` URL into **both** places:
   - the `Install` cell of the Catalog table above
   - the matching `<a class="row" href="...">` in `index.html`
3. Commit and push. GitHub Pages redeploys in about a minute.

Editing a shortcut and re-sharing it produces a **new** link — the old link keeps
serving the old version, so replace it in both spots each time.

## Repo files

- `index.html` — the install page, served by GitHub Pages from `main` at the repo root
- `icon-1024.png` / `icon.svg` — catalog icon, also usable as a custom Home Screen icon

## License

[MIT](LICENSE) — rebuild instructions and page source are free to copy.
