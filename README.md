# iOS Shortcuts

A growing collection of iOS Shortcuts.

**[➜ Install page](https://shiebenaderet.github.io/ios-shortcuts/)** — tap-to-install from any iPhone.

Each shortcut is a signed `.shortcut` file committed to this repo. iOS only
installs *signed* shortcuts, but a signed file served over the web is fine —
tap an Install link on an iPhone and Shortcuts opens with an Add preview.

## Catalog

<!-- CATALOG:START -->
| Shortcut | What it does | Install |
|---|---|---|
| [View Archived](#view-archived) | Opens the newest archive.today snapshot of any webpage | [Install](dist/View%20Archived.shortcut) |
| [Save to Wayback](#save-to-wayback) | Archives the current page in the Wayback Machine | [Install](dist/Save%20to%20Wayback.shortcut) |
| [Plain Text View](#plain-text-view) | Opens the page as clean text, stripped of nav and ads | [Install](dist/Plain%20Text%20View.shortcut) |
| [Cite This Page](#cite-this-page) | Copies an MLA, APA or Chicago citation for the current page | [Install](dist/Cite%20This%20Page.shortcut) |
<!-- CATALOG:END -->

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

## Save to Wayback

Archives the current page in the Wayback Machine, from the share sheet or a
copied link. The write counterpart to View Archived: preserve a source *before*
it disappears rather than hoping someone already did.

**How it works** — opens `https://web.archive.org/save/` plus the page URL.

---

## Plain Text View

Opens the page as clean text with nav, ads and chrome stripped, via
[r.jina.ai](https://r.jina.ai). Useful for pasting into a handout or reading
without the furniture.

**How it works** — opens `https://r.jina.ai/` plus the page URL.

**Note** — this routes the URL through a third-party service. Fine for public
pages; don't use it on anything private.

---

## Cite This Page

Copies a citation for the current page to the clipboard and shows it, from the
share sheet or a copied link.

**How it works** — reads the page's name, then builds:

```
"<Page title>." <URL>. Accessed <date>.
```

**Style picker** — running it offers MLA, APA or Chicago and copies that format.

**Known limitations**

- The site name is dropped rather than used as MLA's container: the title is
  split on `" | "` and only the first part kept. Using the second part needs Get
  Item from List set to Last Item, whose encoding isn't captured yet.
- Titles that separate with a dash rather than a pipe keep their suffix.

---

<!-- Template for new entries:

## Shortcut Name

One-line description.

**How it works** — ...

**Rebuild it yourself**

1. ...

Then add a row to the Catalog table above.
-->

## Adding a shortcut

Shortcuts are generated, not hand-built. Define one in `forge/shortcuts.py`,
then:

```sh
python3 forge/build.py
git commit -am "Add <name>" && git push
```

`build.py` writes a signed file to `dist/` and rewrites the catalog table above
and the matching rows in `index.html`, so the two can't drift apart. Signing uses
macOS's `shortcuts sign --mode anyone`, which is the same signing mode behind an
iCloud share link.

The filename becomes the shortcut's name on import — a `.shortcut` file carries
no name field of its own.

### Encoding notes

Two mistakes that fail *silently*, both found by diffing generated output against
a real Apple-written shortcut:

- Attachments inside a text action's `attachmentsByRange` are **bare** dicts. The
  `{"Value": …, "WFSerializationType": "WFTextTokenAttachment"}` wrapper applies
  only when an entire parameter is one attachment.
- **Input parameter names are per-action, not conventional.** Get Name and Get Item
  from List take `WFInput`; Split Text takes `text`; Format Date takes `WFDate` as a
  `WFTextTokenString`. A wrong key is ignored and the action emits nothing.
- **There is no runtime "inherit the previous action's output."** That is an editor
  convenience that writes the parameter for you, so every generated action must
  name its input explicitly.
- `WFWorkflowMinimumClientVersion` is a **feature gate**. Declare a version older
  than an action you use and that action is quietly skipped, passing an empty
  value downstream. Pin it to a value read from a genuine shortcut.

`Format Date` with `WFDateFormatStyle: "Custom"` returns empty and is currently
avoided; raw date tokens work.

## Repo files

- `index.html` — the install page, served by GitHub Pages from `main` at the repo root
- `forge/` — shortcut definitions, the build script, and a glyph-name table
- `dist/` — generated signed `.shortcut` files (build output, but committed so the page can serve them)
- `icon-1024.png` / `icon.svg` — catalog icon, also usable as a custom Home Screen icon

## License

[MIT](LICENSE) — rebuild instructions and page source are free to copy.
