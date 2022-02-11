""" Contants for Halo Infinite integration"""

DOMAIN = "halo_infinite_ha"
CURRENT = "current"
RECENT_CHANGE = "recent_change"
CROSSPLAY = "crossplay"
CONTROLLER = "controller"
MNK = "mnk"
SENSOR_TYPES = {CURRENT: "Current", RECENT_CHANGE: "Recent Change"}
PLAYLISTS = [CROSSPLAY, CONTROLLER, MNK]
SOLO_TYPES = [CONTROLLER, MNK]

ICONS = {
    CONTROLLER: "mdi:microsoft-xbox-controller",
    CROSSPLAY: "mdi:arrow-top-left-bottom-right",
    "increase": "mdi:arrow-up-bold",
    "decrease": "mdi:arrow-down-bold",
    "same": "mdi:arrow-up-down-bold",
}