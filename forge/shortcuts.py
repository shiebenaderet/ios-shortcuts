"""Shortcut definitions.

Encoding rules learned the hard way, both silent failures:

  * Attachments inside a text action's attachmentsByRange are BARE dicts.
    The {"Value": ..., "WFSerializationType": "WFTextTokenAttachment"}
    wrapper is only for a parameter that is entirely one attachment.
  * Format Date returns empty with WFDateFormatStyle "Custom". Raw date
    tokens work; use those until the right encoding is verified.
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
    name, text = uid(), uid()
    return [
        act("is.workflow.actions.getitemname", UUID=name, WFInput=attach(r_input())),
        act("is.workflow.actions.gettext", UUID=text,
            WFTextActionText=text_token([
                '"', r_out(name, "Name"), '." ', r_input(), '. Accessed ', r_now(), '.'])),
        act("is.workflow.actions.setclipboard", WFInput=attach(r_out(text, "Text"))),
        act("is.workflow.actions.showresult", Text=text_token([r_out(text, "Text")])),
    ]


WEB = ("WFSafariWebPageContentItem", "WFURLContentItem")

SHORTCUTS = {
    "View Archived": {
        "description": "Opens the newest archive.today snapshot of any webpage",
        "color": RED, "glyph": DEFAULT_GLYPH, "input_types": WEB,
        "actions": view_archived,
    },
    "Cite This Page": {
        "description": "Copies a citation for the current page to the clipboard",
        "color": RED, "glyph": DEFAULT_GLYPH, "input_types": WEB,
        "actions": cite_this_page,
    },
}
