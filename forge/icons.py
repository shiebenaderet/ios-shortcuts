"""Install-page icons, drawn to match each shortcut's glyph and colour.

The Shortcuts app renders its own icon from WFWorkflowIconGlyphNumber, which we
can set but cannot read the artwork for. These SVGs approximate the same symbol
so the web page and the app agree.

Shapes are deliberately blunt: solid, high-contrast, no fine detail, because
they render at roughly 52px on the install page.
"""

# White symbol on the shortcut's own colour, on a 512x512 canvas.
SYMBOLS = {
    "archive": """
      <rect x="96"  y="132" width="320" height="76"  rx="20"/>
      <rect x="124" y="228" width="264" height="188" rx="20"/>
      <rect x="212" y="286" width="88"  height="30"  rx="15" fill="{bg}"/>""",
    "uploadArrow": """
      <rect x="236" y="196" width="40" height="150" rx="14"/>
      <path d="M256 120 L346 226 L166 226 Z"/>
      <path d="M132 336 h40 v52 h168 v-52 h40 v72 a20 20 0 0 1 -20 20
               H152 a20 20 0 0 1 -20 -20 Z"/>""",
    "newspaper": """
      <rect x="92" y="140" width="328" height="240" rx="24"/>
      <rect x="120" y="172" width="128" height="80" rx="10" fill="{bg}"/>
      <rect x="268" y="172" width="124" height="16" rx="8"  fill="{bg}"/>
      <rect x="268" y="204" width="124" height="16" rx="8"  fill="{bg}"/>
      <rect x="268" y="236" width="90"  height="16" rx="8"  fill="{bg}"/>
      <rect x="120" y="284" width="272" height="16" rx="8"  fill="{bg}"/>
      <rect x="120" y="316" width="208" height="16" rx="8"  fill="{bg}"/>""",
    # Two comma-shaped marks: a disc with a wedge falling from it.
    "doubleQuote": """
      <circle cx="186" cy="212" r="52"/>
      <path d="M134 212 L134 300 L206 246 Z"/>
      <circle cx="330" cy="212" r="52"/>
      <path d="M278 212 L278 300 L350 246 Z"/>""",
}

TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" \
role="img" aria-label="{label}">
  <rect width="512" height="512" rx="114" fill="{bg}"/>
  <g fill="#FFFFFF">{symbol}
  </g>
</svg>
"""


def hex_of(signed_rgba):
    """Undo the signed 32-bit packing to get #RRGGBB back."""
    value = signed_rgba + (1 << 32) if signed_rgba < 0 else signed_rgba
    return "#%06X" % (value >> 8)


def render(glyph_name, signed_rgba, label):
    bg = hex_of(signed_rgba)
    symbol = SYMBOLS[glyph_name].format(bg=bg)
    return TEMPLATE.format(bg=bg, symbol=symbol, label=label)
