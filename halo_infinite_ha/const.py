""" Contants for Halo Infinite integration"""

DOMAIN = "halo_infinite_ha"
CONF_LIST = "ranked_inputs"
API_VERSION = "0.3.8"

CSR = "csr"
KDR = "k/d"
CROSSPLAY = "crossplay"
CONTROLLER = "controller"
MNK = "mnk"
SENSOR_TYPES = {CSR: "CSR", KDR: "K/D"}
PLAYLISTS = [CROSSPLAY, CONTROLLER, MNK]
SOLO_TYPES = [CONTROLLER, MNK]

ICONS = {
    CONTROLLER: "mdi:microsoft-xbox-controller",
    CROSSPLAY: "mdi:arrow-top-left-bottom-right",
    CSR: "mdi:chevron-triple-up",
    KDR: "mdi:fencing",
    "increase": "mdi:arrow-up-bold",
    "decrease": "mdi:arrow-down-bold",
    "same": "mdi:arrow-up-down-bold",
}