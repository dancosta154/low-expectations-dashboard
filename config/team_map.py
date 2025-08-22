# app/config/team_map.py

# ESPN Team ID to internal team key mapping
TEAM_ID_MAP = {
    1: "seahawks",  # Arizona Cardinals (Dan Costa)
    2: "numbnuts",  # Numbnutsss (Greg Costa)
    3: "stamford",  # Stamford Mackie (Scott Mackie)
    4: "cmb3dan",  # CMB 3-Dan (Dan S)
    5: "devonta",  # Chasing Joe (Joe Costa)  [was DeVonta Hurts You]
    6: "bumcrumbs",  # Bum Crumbs (Phat Johnson)
    7: "mitchell",  # Team Mitchell (Timothy Mitchell)
    8: "metzler",  # The Arm of the Armadillos (Andrew Flaherty) [was Paul Metzler...]
    9: "kenney",  # Team Kenney (Brian Kenney)
    10: "mahoms",  # Justin Time (Connor Flaherty) [was Me And My Mahomies]
}

# ESPN Owner UUID to owner name mapping (based on the UUIDs seen in your dashboard)
OWNER_UUID_MAP = {
    "{AF006F6B-9B81-4A84-B095-9071460336CF}": "Dan Costa",
    "{8C478935-D2DF-4937-BB1D-218E38E699A7}": "Greg Costa", 
    "{8265642-4B76-4353-961E-565FC38C63DB}": "Scott Mackie",
    "{145F0780-1FAE-4E55-8715-C78F7553A8F1}": "Dan S",
    "{39A92573-7DF4-4244-90DA-BFCDDB2973BB}": "Joe Costa",
    "{B073C55B-C009-46F0-95AA-0B20D243D8CA}": "Phat Johnson",
    "{4C1E58FF-3F1C-4091-9034-3918B5BA5031}": "Timothy Mitchell",
    "{EBF01626-4DE0-405A-B016-264DE0205AE1}": "Andrew Flaherty",
    # Add more mappings as needed based on actual UUIDs from your league
}

# Team name to owner mapping (for display purposes)
TEAM_TO_OWNER_MAP = {
    "seahawks": "Dan Costa",
    "numbnuts": "Greg Costa", 
    "stamford": "Scott Mackie",
    "cmb3dan": "Dan S",
    "devonta": "Joe Costa",
    "bumcrumbs": "Phat Johnson",
    "mitchell": "Timothy Mitchell", 
    "metzler": "Andrew Flaherty",
    "kenney": "Brian Kenney",
    "mahoms": "Connor Flaherty",
}

# Players who were kept in 2023 and cannot be kept again in 2024
# (they've already been kept for 1 season, max is 2 seasons total)
SEASONS_KEPT_OVERRIDES = {
    2976212: 1,  # Stefon Diggs
    3918298: 1,  # Josh Allen
    3116406: 1,  # Tyreek Hill
    4241389: 1,  # CeeDee Lamb
    4429795: 1,  # Jahmyr Gibbs
    4569618: 1,  # Garrett Wilson
    4239996: 1,  # Travis Etienne Jr.
    3054850: 1,  # Alvin Kamara
    4427366: 1,  # Breece Hall
    3045147: 1,  # James Conner
    4430737: 1,  # Kyren Williams
    4036378: 1,  # Jordan Love
    4426515: 1,  # Puka Nacua
    4430027: 1,  # Sam LaPorta
    4035676: 1,  # Zack Moss (found as "zack moss")
    4430878: 1,  # Jaxon Smith-Njigba
    4258173: 1,  # Nico Collins
    4428557: 1,  # Tyjae Spears
    4429084: 1,  # Anthony Richardson
    4429160: 1,  # De'Von Achane
    4428331: 1,  # Rashee Rice
    4569987: 1,  # Jaylen Warren
}
