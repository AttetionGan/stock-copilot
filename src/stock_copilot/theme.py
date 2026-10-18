"""Per-browser appearance overrides; never mutate server-wide Streamlit config."""

THEME_LABELS = {"light": "浅色模式", "dark": "深色模式", "system": "跟随系统"}
COLOR_CONVENTIONS = {"green_up": "绿涨红跌", "red_up": "红涨绿跌"}

LIGHT = {
    "bg": "#F6F8FC", "surface": "#FFFFFF", "inset": "#F1F4FA",
    "term": "#F1F4FA", "border": "#DFE5F0", "text": "#17243B", "muted": "#586A85",
    "accent": "#365EDC", "accent-bg": "#EDF1FF", "accent-border": "#CCD6FC", "on-accent": "#FFFFFF",
    "positive-bg": "#E8F5EE", "positive-border": "#BFE1CF", "positive-text": "#167653",
    "negative-bg": "#FCEFF1", "negative-border": "#EACBD0", "negative-text": "#B9444E",
    "pending-bg": "#EDF0F6",
    "attention-bg": "#FFF4DF", "attention-border": "#E3B763", "attention-text": "#7D4C08",
}
DARK = {
    "bg": "#0C1322", "surface": "#141E30", "inset": "#101A2B",
    "term": "#1A263B", "border": "#2A3850", "text": "#E8EEF8", "muted": "#A9B7CF",
    "accent": "#A7BAFF", "accent-bg": "#233352", "accent-border": "#405584", "on-accent": "#0C1322",
    "positive-bg": "#12352C", "positive-border": "#285D48", "positive-text": "#70D7AB",
    "negative-bg": "#3B232D", "negative-border": "#6B3E4D", "negative-text": "#FCA1AA",
    "pending-bg": "#1C283B",
    "attention-bg": "#3A2C17", "attention-border": "#87622C", "attention-text": "#FFD58A",
}

# Streamlit 1.66.0 uses generated colors for native controls. Override the
# surfaces as well as custom cards, including popovers mounted outside .stApp.
# Plotly text/grid overrides let OS changes work without a Python rerun.
NATIVE_STYLES = """
html,body {background:var(--sc-bg);color:var(--sc-text);}
.stApp {color-scheme:inherit!important;background:var(--sc-bg)!important;color:var(--sc-text)!important;}
[data-testid="stAppViewContainer"],[data-testid="stMain"],[data-testid="stHeader"] {background:var(--sc-bg)!important;color:var(--sc-text)!important;}
[data-testid="stSidebar"],[data-testid="stSidebarContent"] {color-scheme:inherit!important;background:var(--sc-surface)!important;color:var(--sc-text)!important;}
.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp p,.stApp label,.stApp legend {color:var(--sc-text)!important;}
.stApp [data-testid="stCaptionContainer"] p {color:var(--sc-muted)!important;}
.stApp a {color:var(--sc-accent);}
.stApp a[aria-current="page"] {background:var(--sc-accent-bg)!important;color:var(--sc-accent)!important;border-radius:7px;}
[data-testid="stPageLink"] a,[data-testid="stPageLink-NavLink"] {background:transparent!important;color:var(--sc-text)!important;}
[data-testid="stPageLink"] a:hover {background:var(--sc-accent-bg)!important;}
[data-testid="stVerticalBlockBorderWrapper"],[data-testid="stForm"],[data-testid="stExpander"] {border-color:var(--sc-border)!important;}
[data-testid="stExpander"] summary {background:var(--sc-surface)!important;color:var(--sc-text)!important;}
.stApp input,.stApp textarea,[data-baseweb="input"],[data-baseweb="base-input"],[data-baseweb="textarea"],
[data-baseweb="select"] > div {background:var(--sc-surface)!important;color:var(--sc-text)!important;border-color:var(--sc-border)!important;caret-color:var(--sc-accent);}
.stApp input::placeholder,.stApp textarea::placeholder {color:var(--sc-muted)!important;}
[data-baseweb="select"] div,[data-baseweb="select"] span,[data-baseweb="select"] input {color:var(--sc-text)!important;}
.react-aria-ComboBox [role="group"],.react-aria-ComboBox button {background:var(--sc-surface)!important;color:var(--sc-text)!important;border-color:var(--sc-border)!important;}
.react-aria-ComboBox svg {color:var(--sc-text)!important;}
[data-testid="stRadioOption"] > div > div:first-child {background:var(--sc-surface)!important;border-color:var(--sc-muted)!important;}
[data-testid="stRadioOption"]:has(input:checked) > div > div:first-child {background:var(--sc-accent)!important;border-color:var(--sc-accent)!important;}
[data-testid="stRadioOption"]:has(input:checked) > div > div:first-child > div {background:var(--sc-on-accent)!important;}
.stApp hr {border-color:var(--sc-border)!important;}
[data-baseweb="radio"] > div:first-child {background:var(--sc-surface)!important;box-shadow:inset 0 0 0 1px var(--sc-muted);}
[data-baseweb="radio"]:has(input:checked) > div:first-child {background:var(--sc-accent)!important;box-shadow:none;}
[data-baseweb="radio"]:has(input:checked) > div:first-child > div {background:var(--sc-on-accent)!important;}
[data-baseweb="popover"],[data-baseweb="popover"] > div,[data-testid="stPopoverBody"],[role="listbox"],[role="option"] {background:var(--sc-surface)!important;color:var(--sc-text)!important;border-color:var(--sc-border)!important;}
[role="option"][aria-selected="true"],[role="option"]:hover {background:var(--sc-accent-bg)!important;}
[data-baseweb="popover"] p,[data-baseweb="popover"] label {color:var(--sc-text)!important;}
.stApp button {color:var(--sc-text)!important;border-color:var(--sc-border)!important;}
[data-testid="stBaseButton-secondary"],[data-testid="stBaseButton-secondaryFormSubmit"],[data-testid="stPopoverButton"] {background:var(--sc-surface)!important;}
[data-testid="stBaseButton-primary"],[data-testid="stBaseButton-primaryFormSubmit"] {background:var(--sc-accent)!important;color:var(--sc-on-accent)!important;border-color:var(--sc-accent)!important;}
[data-testid="stBaseButton-primary"] p,[data-testid="stBaseButton-primaryFormSubmit"] p {color:var(--sc-on-accent)!important;}
.stApp button:hover:not(:disabled) {border-color:var(--sc-accent)!important;}
.stApp button:disabled {opacity:.45;}
.stApp [role="alert"] {background:var(--sc-inset)!important;color:var(--sc-text)!important;border-color:var(--sc-border)!important;}
.stApp .js-plotly-plot text,.stApp .js-plotly-plot text tspan {fill:var(--sc-text)!important;}
.stApp .js-plotly-plot .main-svg {background:transparent!important;}
.stApp .js-plotly-plot .gridlayer path,.stApp .js-plotly-plot .zerolinelayer path {stroke:var(--sc-border)!important;}
.stApp .js-plotly-plot .hoverlayer .hovertext path {fill:var(--sc-surface)!important;stroke:var(--sc-border)!important;}
"""


def _palette(values, scheme, convention):
    values = dict(values)
    if convention == "red_up":
        for suffix in ("bg", "border", "text"):
            positive, negative = f"positive-{suffix}", f"negative-{suffix}"
            values[positive], values[negative] = values[negative], values[positive]
    return ":root{" + f"color-scheme:{scheme};" + "".join(f"--sc-{key}:{value};" for key, value in values.items()) + "}"


def theme_styles(mode="system", convention="green_up"):
    if mode not in THEME_LABELS:
        raise ValueError("不支持的外观模式。")
    if convention not in COLOR_CONVENTIONS:
        raise ValueError("不支持的涨跌配色。")
    if mode == "system":
        colors = _palette(LIGHT, "light", convention) + "@media(prefers-color-scheme:dark){" + _palette(DARK, "dark", convention) + "}"
    else:
        colors = _palette(DARK if mode == "dark" else LIGHT, mode, convention)
    return colors + NATIVE_STYLES
