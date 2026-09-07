"""Shortcut definitions.

Encoding rules learned the hard way, both silent failures:

  * Attachments inside a text action's attachmentsByRange are BARE dicts.
    The {"Value": ..., "WFSerializationType": "WFTextTokenAttachment"}
    wrapper is only for a parameter that is entirely one attachment.
  * Format Date's WFDate parameter is a WFTextTokenString containing one
    attachment -- NOT a bare WFTextTokenAttachment. Wrapping it as an
    attachment leaves the field unbound and the action outputs nothing.
  * Choose from Menu is three entries sharing a GroupingIdentifier:
    WFControlFlowMode 0 opens, 1 per case (with WFMenuItemTitle), 2 closes.
    The opening entry MUST carry WFMenuItems listing the titles -- without it
    the app shows its "One"/"Two" placeholders and ignores the case blocks.
  * Input parameter names are per-action, not conventional. Get Name and Get
    Item from List take WFInput; Split Text takes "text"; Format Date takes
    WFDate. A wrong key is ignored and the action silently emits nothing.
  * There is no runtime "inherit the previous action's output". That is an
    editor convenience which writes the parameter for you, so every action
    authored here must name its input explicitly.
  * Split Text also takes WFTextSeparator "Custom" plus WFTextCustomSeparator;
    omitting both splits on new lines.
  * Get Item from List and Split Text default to First Item and New Lines,
    so neither needs parameters for those. An unparameterised Get Item from
    List placed first implicitly receives Shortcut Input.
"""
import uuid

OBJ = "￼"  # object-replacement char an attachment binds to

# icon_color is RGBA packed into a 32-bit int, so any colour is computable:
#   rgba("#E8A62B") -> 3903204351
# icon_glyph is an opaque enum with no public table -- each value has to be
# captured by setting it in the app and reading it back off a shared record.
# The field is a SIGNED 32-bit int. A value above 2**31 makes Shortcuts fail to
# parse the icon and silently discard every action, importing an empty shortcut.
RED = -12365313             # #FF4351, captured
BLUE = 463140863            # #1B9AF7, captured
DEFAULT_GLYPH = 61440       # 0xF000, the generic default
GLYPH_CAPTURED = 61699      # 0xF103, captured -- awaiting a name


def rgba(hex_colour):
    """#RRGGBB -> the signed 32-bit int Shortcuts stores in icon_color."""
    value = int(hex_colour.lstrip("#"), 16) << 8 | 0xFF
    return value - (1 << 32) if value >= (1 << 31) else value


AMBER = rgba("#E8A62B")     # the install page's accent


def uid():
    return str(uuid.uuid4()).upper()


# --- bare attachments (go inside attachmentsByRange) ---
def r_input():
    return {"Type": "ExtensionInput"}


def r_out(u, name):
    return {"Type": "ActionOutput", "OutputUUID": u, "OutputName": name}


def r_now():
    return {"Type": "CurrentDate"}


# --- wrapped (only when a whole parameter is one attachment) ---
def attach(value):
    return {"Value": value, "WFSerializationType": "WFTextTokenAttachment"}


def text_token(parts):
    """parts: strings and bare attachment dicts, in order."""
    s, atts = "", {}
    for part in parts:
        if isinstance(part, str):
            s += part
        else:
            atts["{%d, 1}" % len(s)] = part
            s += OBJ
    return {"Value": {"string": s, "attachmentsByRange": atts},
            "WFSerializationType": "WFTextTokenString"}


def act(identifier, **params):
    return {"WFWorkflowActionIdentifier": identifier,
            "WFWorkflowActionParameters": params}


# ----------------------------------------------------------------------

def view_archived():
    u = uid()
    return [
        act("is.workflow.actions.gettext", UUID=u,
            WFTextActionText=text_token(["https://archive.ph/newest/", r_input()])),
        act("is.workflow.actions.openurl", WFInput=attach(r_out(u, "Text"))),
    ]


def cite_this_page():
    """Citation in a chosen style, copied to the clipboard.

    Get Item from List collapses the input to one item -- some sites' share
    sheets offer both a Safari web page and a URL, which otherwise doubles
    everything. Its input is passed explicitly: relying on the first action
    implicitly receiving Shortcut Input produced an empty chain.
    """
    first, name, nl, one_name, pipe, short, d_mla, d_us, group = (
        uid(), uid(), uid(), uid(), uid(), uid(), uid(), uid(), uid())
    url = r_out(first, "Item from List")
    title = r_out(short, "Item from List")
    mla_date = r_out(d_mla, "Formatted Date")
    us_date = r_out(d_us, "Formatted Date")

    def fmt(u, pattern):
        return act("is.workflow.actions.format.date", UUID=u,
                   WFDate=text_token([r_now()]),
                   WFDateFormatStyle="Custom", WFDateFormat=pattern)

    styles = ["MLA", "APA", "Chicago"]

    def case(label, parts):
        out = uid()
        return [
            act("is.workflow.actions.choosefrommenu", GroupingIdentifier=group,
                WFControlFlowMode=1, WFMenuItemTitle=label),
            act("is.workflow.actions.gettext", UUID=out,
                WFTextActionText=text_token(parts)),
            act("is.workflow.actions.setclipboard", WFInput=attach(r_out(out, "Text"))),
            act("is.workflow.actions.showresult",
                Text=text_token([r_out(out, "Text")])),
        ]

    return [
        # One item for the URL: some share sheets offer both a Safari web page
        # and a URL, which otherwise doubles it.
        act("is.workflow.actions.getitemfromlist", UUID=first,
            WFInput=attach(r_input())),
        # Name is read from the whole input, not the extracted item, which is
        # the bare URL and has no name. It yields one name per input item.
        act("is.workflow.actions.getitemname", UUID=name,
            WFInput=attach(r_input())),
        act("is.workflow.actions.text.split", UUID=nl,
            text=attach(r_out(name, "Name"))),
        act("is.workflow.actions.getitemfromlist", UUID=one_name,
            WFInput=attach(r_out(nl, "Split Text"))),
        # Titles usually append the site: "Headline | Snopes.com". Splitting on
        # the spaced separator drops it without needing a trim.
        act("is.workflow.actions.text.split", UUID=pipe,
            text=attach(r_out(one_name, "Item from List")),
            WFTextSeparator="Custom", WFTextCustomSeparator=" | "),
        act("is.workflow.actions.getitemfromlist", UUID=short,
            WFInput=attach(r_out(pipe, "Split Text"))),
        fmt(d_mla, "d MMMM yyyy"),
        fmt(d_us, "MMMM d, yyyy"),
        act("is.workflow.actions.choosefrommenu", GroupingIdentifier=group,
            WFControlFlowMode=0, WFMenuPrompt="Citation style",
            WFMenuItems=styles),
        *case("MLA", ['"', title, '." ', url, '. Accessed ', mla_date, '.']),
        *case("APA", [title, '. Retrieved ', us_date, ', from ', url]),
        *case("Chicago", ['"', title, '." Accessed ', us_date, '. ', url, '.']),
        act("is.workflow.actions.choosefrommenu", GroupingIdentifier=group,
            WFControlFlowMode=2, UUID=uid()),
    ]


WEB = ("WFSafariWebPageContentItem", "WFURLContentItem")

SHORTCUTS = {
    "View Archived": {
        "description": "Opens the newest archive.today snapshot of any webpage",
        "color": AMBER, "glyph": GLYPH_CAPTURED, "input_types": WEB,
        "actions": view_archived,
    },
    "Cite This Page": {
        "description": "Copies an MLA, APA or Chicago citation for the current page",
        "color": BLUE, "glyph": GLYPH_CAPTURED, "input_types": WEB,
        "actions": cite_this_page,
    },
}
