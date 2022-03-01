""" Contants for Halo Infinite integration"""

DOMAIN = "halo_infinite_ha"
CONF_LIST = "ranked_inputs"
API_VERSION = "0.3.9"

CSR = "csr"
KDR = "k/d"
MATCH = "match"
CROSSPLAY = "crossplay"
CONTROLLER = "controller"
MNK = "mnk"
CTF = "CTF"
SLAYER = "Slayer"
ODDBALL = "Oddball"
STRONGHOLDS = "Strongholds"
SENSOR_TYPES = {CSR: "CSR", KDR: "K/D", MATCH: "Match"}
PLAYLISTS = [CROSSPLAY, CONTROLLER, MNK]
SOLO_TYPES = [CONTROLLER, MNK]
GAME_MODES = [CTF, SLAYER, ODDBALL, STRONGHOLDS]
ICONS = {
    CONTROLLER: "mdi:microsoft-xbox-controller",
    CROSSPLAY: "mdi:arrow-top-left-bottom-right",
    CSR: "mdi:chevron-triple-up",
    KDR: "mdi:fencing",
    MATCH: "mdi:scoreboard",
    CTF: "mdi:flag-variant",
    SLAYER: "mdi:pistol",
    ODDBALL: "mdi:skull",
    STRONGHOLDS: "mdi:map-clock",
    "left": "mdi:exit-run",
    "increase": "mdi:arrow-up-bold",
    "decrease": "mdi:arrow-down-bold",
    "same": "mdi:arrow-up-down-bold",
}