"""Colors shared by the whole app (RGBA tuples, values 0-1)."""


def hex_color(value, alpha=1.0):
    value = value.lstrip('#')
    r, g, b = (int(value[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    return (r, g, b, alpha)


BG = (1, 1, 1, 1)
WHITE = (1, 1, 1, 1)
ACCENT = hex_color('#5B5FEF')          # modern indigo / purple-blue
ACCENT_SOFT = hex_color('#E9EAFF')
CARD = hex_color('#F4F5FB')
TEXT = hex_color('#1B1D2A')
MUTED = hex_color('#7A7F94')
LINE = hex_color('#E6E8F0')
DANGER = hex_color('#EF4444')
DANGER_SOFT = hex_color('#FDE8E8')

PRIORITY_COLORS = {
    'Low': hex_color('#22C55E'),
    'Medium': hex_color('#F59E0B'),
    'High': hex_color('#EF4444'),
}
