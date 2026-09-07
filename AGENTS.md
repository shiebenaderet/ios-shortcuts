# Working on this repo

Reference for anyone — human or agent — generating `.shortcut` files here.
Everything below was verified against real Apple-written shortcuts. **Keep it
updated**: when you verify a new action or encoding, add it, and when something
turns out wrong, correct it rather than leaving both versions.

## Build

```sh
python3 forge/build.py        # signs into dist/, draws icons/, rewrites both catalogs
```

Define shortcuts in `forge/shortcuts.py`. `forge/glyphs.py` holds 508 icon glyph
names. Signing uses macOS's `shortcuts sign --mode anyone`, so **this only builds
on a Mac**.

## The cardinal rule: everything fails silently

Nothing in this format reports an error. A wrong key, a wrong wrapper, an
out-of-range integer, a missing list — each yields an empty value, or an empty
shortcut, and never a message. `shortcuts sign` will happily sign a plist that
Shortcuts cannot load.

**So do not reason about the format — read it.** The reliable loop:

1. Build a shortcut and import it (`open dist/Name.shortcut`)
2. In Shortcuts: **Share → Copy iCloud Link**
3. Read what Apple actually stored:

```sh
curl -s https://www.icloud.com/shortcuts/api/records/<id> | python3 -c "..."
# fields.shortcut.value.downloadURL, with ${f} replaced, is the raw plist
```

Diffing that against your source shows exactly what was accepted, rewritten, or
dropped. Four debugging rounds were spent guessing at one action's encoding;
one capture then settled four actions at once.

**When the unknown is "which spelling," test them side by side.** One shortcut
with three candidate key names and a Show Result listing all three outputs
resolves in a single run what three sequential guesses would not.

For an action with no visible output, give each candidate a *distinguishable side
effect* instead — three Speak Text variants each saying a different word
identified its input key by ear in one run.

A probe can only rank spellings you supply. If every candidate comes back empty,
suspect the **identifier**, not the key: a wrong key still leaves a real action
that runs and returns nothing, but a wrong identifier means no action at all. Only
a capture settles that.

## File format

A `.shortcut` is a binary plist. Signed output is an `AEA1` container.
`shortcuts sign` **requires the input file to end in `.shortcut`** — a `.plist`
extension is rejected with a misleading "isn't in the correct format".

### Top-level keys

| Key | Value |
|---|---|
| `WFWorkflowClientVersion` | `"5037.0.17"` |
| `WFWorkflowMinimumClientVersion` | `1113` (int) |
| `WFWorkflowMinimumClientVersionString` | `"1113"` |
| `WFWorkflowIcon` | `{WFWorkflowIconStartColor, WFWorkflowIconGlyphNumber}` |
| `WFWorkflowTypes` | `["ActionExtension"]` for share sheet; also `WFWorkflowTypeShowInSearch`, `Watch` |
| `WFWorkflowInputContentItemClasses` | accepted share-sheet types |
| `WFWorkflowNoInputBehavior` | `{"Name": "WFWorkflowNoInputBehaviorGetClipboard", "Parameters": {}}` |
| `WFWorkflowActions` | the action list |
| `WFWorkflowOutputContentItemClasses`, `WFWorkflowImportQuestions`, `WFQuickActionSurfaces` | `[]` |
| `WFWorkflowHasOutputFallback`, `WFWorkflowHasShortcutInputVariables` | bools |

**`WFWorkflowMinimumClientVersion` is a feature gate, not a label.** Declare a
version older than an action you use and that action is silently skipped, passing
an empty value downstream. Never invent it.

A `.shortcut` file has **no name field** — the filename becomes the shortcut's
name on import. (iCloud links carry the name in the CloudKit record instead.)

### Three serialization shapes

Getting these confused is the single most common bug, and they look alike.

**1. Bare attachment** — only inside a text action's `attachmentsByRange`:

```python
{"Type": "ExtensionInput"}
{"Type": "ActionOutput", "OutputUUID": uuid, "OutputName": "Text"}
{"Type": "CurrentDate"}
```

**2. `WFTextTokenAttachment`** — when a whole parameter *is* one attachment:

```python
{"Value": <bare attachment>, "WFSerializationType": "WFTextTokenAttachment"}
```

**3. `WFTextTokenString`** — text with attachments embedded at character offsets:

```python
{"Value": {"string": "https://example.com/￼",
           "attachmentsByRange": {"{20, 1}": <bare attachment>}},
 "WFSerializationType": "WFTextTokenString"}
```

The placeholder character is `U+FFFC`; the range is `{offset, 1}` counting
characters from zero. A stray space before an attachment shifts every offset.

Some parameters that look like plain attachments are actually shape 3 —
`Format Date`'s `WFDate` is the known example.

### Input parameters are per-action

There is **no convention** and **no runtime inheritance**. "Input defaults to the
previous action's output" is an *editor* convenience that writes the parameter for
you; an action authored here with no input parameter simply has no input.

## Verified actions

| Action | Identifier | Input key | Output name |
|---|---|---|---|
| Text | `is.workflow.actions.gettext` | `WFTextActionText` (shape 3) | `Text` |
| Open URLs | `is.workflow.actions.openurl` | `WFInput` (shape 2) | — |
| Get Name | `is.workflow.actions.getitemname` | `WFInput` (shape 2) | `Name` |
| Get Item from List | `is.workflow.actions.getitemfromlist` | `WFInput` (shape 2) | `Item from List` |
| Split Text | `is.workflow.actions.text.split` | **`text`** (shape 2) | `Split Text` |
| Format Date | `is.workflow.actions.format.date` | **`WFDate` (shape 3)** | `Formatted Date` |
| Date (current) | `is.workflow.actions.date` | — | `Date` |
| Copy to Clipboard | `is.workflow.actions.setclipboard` | `WFInput` (shape 2) | — |
| Show Result | `is.workflow.actions.showresult` | `Text` (shape 3) | — |
| Speak Text | `is.workflow.actions.speaktext` | `WFText` (shape 3) | — |
| Choose from Menu | `is.workflow.actions.choosefrommenu` | — | `Menu Result` |

Extra parameters:

- **Split Text** — `WFTextSeparator: "Custom"` with `WFTextCustomSeparator`;
  omit both to split on new lines.
- **Format Date** — `WFDateFormatStyle: "Custom"` with `WFDateFormat` (ICU
  pattern, e.g. `d MMMM yyyy`). Built-ins: Short, Medium, Long, Relative,
  RFC 2822, ISO 8601. `M` is month, `m` is minute.
- **Get Item from List** — no parameters means First Item. `WFItemSpecifier:
  "Last Item"` takes the last; `WFItemSpecifier: "Item At Index"` with
  `WFItemIndex` takes a given one (1-based). Both verified.
- **Choose from Menu** — three entries sharing a `GroupingIdentifier`:
  `WFControlFlowMode` `0` opens (and **must** carry `WFMenuItems` listing the
  titles, plus optional `WFMenuPrompt`), `1` per case with `WFMenuItemTitle`,
  `2` closes and carries the `UUID` that provides `Menu Result`.
  Without `WFMenuItems` the app shows its "One"/"Two" placeholders and ignores
  the case blocks entirely.

Magic-variable names (`OutputName`) come from the action's display name. Users can
rename them, so a captured shortcut may show a custom one.

## Icons

`WFWorkflowIconStartColor` is **RGBA packed into a signed 32-bit int**. A value
above 2³¹ makes Shortcuts fail to parse the icon and **discard every action**,
importing an empty shortcut. `forge/shortcuts.py:rgba()` handles the wrap.

`WFWorkflowIconGlyphNumber` is an opaque enum; `forge/glyphs.py` maps names to
numbers (vendored from Cherri, sourced from pfgithub/scpl, MIT). `61440` /
`0xF000` is the generic default.

## Distribution

Signed files are served from GitHub Pages and install by tapping on an iPhone —
verified. iCloud links are unnecessary, and are worse: every share mints a **new**
URL while old links keep serving the old version forever.

## Next capture

Two unknowns are blocked on one shared shortcut. To make it: new shortcut →
Shortcut Details (i) → **Show in Share Sheet** on (do this first, or Shortcut
Input is not offered) → add **Get Article from Web Page** and set its input to
the **Shortcut Input** variable → add **If** and leave the condition alone →
**Share > Copy iCloud Link**.

Wiring the input is the point: an unwired action serializes to just a UUID.

That unblocks **Read Aloud** (Get Article, then Speak Text) and fixes the
citation's container bug — a title with no `" | "` splits into one item, so
first and last match and the site repeats the headline. An If comparing the
split's item count to 1 solves it.

## Known-unverified

- `If` / `Otherwise` / `End If` — control flow, presumably shaped like Choose
  from Menu with a `GroupingIdentifier` and `WFControlFlowMode`.
- `Get Article from Web Page` — `is.workflow.actions.getarticle` produced nothing
  with `WFWebPage`, `WFInput` or `WFURL`, so either the identifier or the key is
  wrong. Needs a capture.
- `Replace Text`, `Match Text`.
- Whether arbitrary (non-palette) icon colours render exactly as specified.
