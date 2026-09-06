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
    The opening entry carries no list of items; the cases define them.
  * Split Text takes WFTextSeparator "Custom" plus WFTextCustomSeparator.
  * Get Item from List and Split Text default to First Item and New Lines,
    so neither needs parameters for those. An unparameterised Get Item from
    List placed first implicitly receives Shortcut Input.
"""
import uuid

OBJ = "￼"  # object-replacement char an attachment binds to

RED = 4282601983       # verified palette value
DEFAULT_GLYPH = 61440  # 0xF000, the generic default


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

    Get Item from List runs first with no parameters, so it receives Shortcut
    Input implicitly and collapses it to one item -- some sites' share sheets
    offer both a Safari web page and a URL, which otherwise doubles everything.
    """
    first, name, split, short, d_mla, d_us, group = (
        uid(), uid(), uid(), uid(), uid(), uid(), uid())
    url = r_out(first, "Item")
    title = r_out(short, "Item")
    mla_date = r_out(d_mla, "Formatted Date")
    us_date = r_out(d_us, "Formatted Date")

    def fmt(u, pattern):
        return act("is.workflow.actions.format.date", UUID=u,
                   WFDate=text_token([r_now()]),
                   WFDateFormatStyle="Custom", WFDateFormat=pattern)

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
        act("is.workflow.actions.getitemfromlist", UUID=first),
        act("is.workflow.actions.getitemname", UUID=name, WFInput=attach(url)),
        # Most page titles append the site name: "Headline | Snopes.com".
        # Splitting on " | " and keeping the first part drops it without
        # needing a separate trim, since the spaces go with the separator.
        act("is.workflow.actions.text.split", UUID=split,
            WFTextSeparator="Custom", WFTextCustomSeparator=" | "),
        act("is.workflow.actions.getitemfromlist", UUID=short),
        fmt(d_mla, "d MMMM yyyy"),
        fmt(d_us, "MMMM d, yyyy"),
        act("is.workflow.actions.choosefrommenu", GroupingIdentifier=group,
            WFControlFlowMode=0),
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
        "color": RED, "glyph": DEFAULT_GLYPH, "input_types": WEB,
        "actions": view_archived,
    },
    "Cite This Page": {
        "description": "Copies an MLA, APA or Chicago citation for the current page",
        "color": RED, "glyph": DEFAULT_GLYPH, "input_types": WEB,
        "actions": cite_this_page,
    },
}
