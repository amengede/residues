#---- Image Assets ----#

#region object types
OBJECT_TYPE_FIRE_SPELL = 2
OBJECT_TYPE_ICE_SPELL = 3
OBJECT_TYPE_LOGO = 4
OBJECT_TYPE_RESTRICTED = 5
OBJECT_TYPE_ADA_ATTACK = 6
OBJECT_TYPE_ADA_HURT = 7
OBJECT_TYPE_ADA_IDLE = 8
OBJECT_TYPE_ADA_DEAD = 9
OBJECT_TYPE_ADA_LOW_HEALTH = 10
OBJECT_TYPE_ALICE_DEAD = 11
OBJECT_TYPE_ALICE_HURT = 12
OBJECT_TYPE_ALICE_IDLE = 13
OBJECT_TYPE_ALICE_ATTACK = 14
OBJECT_TYPE_ALICE_LOW_HEALTH = 15
OBJECT_TYPE_ARROW = 16
OBJECT_TYPE_BABBAGE_ATTACK = 17
OBJECT_TYPE_BABBAGE_DEAD = 18
OBJECT_TYPE_BABBAGE_HURT = 19
OBJECT_TYPE_BABBAGE_IDLE = 20
OBJECT_TYPE_BABBAGE_LOW_HEALTH = 24
OBJECT_TYPE_BLANK_PAGE = 25
OBJECT_TYPE_CONSOLE = 26
OBJECT_TYPE_DEMON_ATTACK = 27
OBJECT_TYPE_DEMON_DEAD = 28
OBJECT_TYPE_DEMON_HURT = 29
OBJECT_TYPE_DEMON_IDLE = 30
OBJECT_TYPE_GEAR = 31
OBJECT_TYPE_GHOST_ARCHER_ATTACK = 32
OBJECT_TYPE_GHOST_ARCHER_DEAD = 33
OBJECT_TYPE_GHOST_ARCHER_HURT = 34
OBJECT_TYPE_GHOST_ARCHER_IDLE = 35
OBJECT_TYPE_LABEL_QUIT = 36
OBJECT_TYPE_LABEL_RESIDUES = 37
OBJECT_TYPE_LABEL_START = 38
OBJECT_TYPE_LIGHTNING_BOLT = 39
OBJECT_TYPE_MAGE_ATTACK = 40
OBJECT_TYPE_MAGE_DEAD = 41
OBJECT_TYPE_MAGE_HURT = 42
OBJECT_TYPE_MAGE_IDLE = 43
OBJECT_TYPE_NPC_A_PORTRAIT = 44
OBJECT_TYPE_NPC_B_PORTRAIT = 45
OBJECT_TYPE_NPC_OVERWORLD_DOWN = 46
OBJECT_TYPE_NPC_OVERWORLD_LEFT_RIGHT = 47
OBJECT_TYPE_NPC_OVERWORLD_UP = 48
OBJECT_TYPE_OVERWORLD_BUILDING = 49
OBJECT_TYPE_OVERWORLD_GRASS = 50
OBJECT_TYPE_OVERWORLD_PATH = 51
OBJECT_TYPE_OVERWORLD_PUZZLE = 52
OBJECT_TYPE_OVERWORLD_TREE = 53
OBJECT_TYPE_PC_OVERWORLD_DOWN = 54
OBJECT_TYPE_PC_OVERWORLD_LEFT_RIGHT = 55
OBJECT_TYPE_PC_OVERWORLD_UP = 56
OBJECT_TYPE_TITLE_SCREEN = 57
OBJECT_TYPE_COUNT = 58
#endregion
#region animation types
ANIMATION_TYPE_IDLE = 0
#endregion
#region image descriptors
IMAGE_DESCRIPTORS = {
	OBJECT_TYPE_ADA_ATTACK: {
		"filename": "img/ada_attack.png",
		"scale": 0.25,
        "flip": True,
	},
	OBJECT_TYPE_ADA_HURT: {
		"filename": "img/ada_hurt.png",
		"scale": 0.25,
        "flip": True,
	},
	OBJECT_TYPE_ADA_IDLE: {
		"filename": "img/ada_idle.png",
		"scale": 0.25,
        "flip": True,
	},
	OBJECT_TYPE_ADA_DEAD: {
		"filename": "img/ada_dead.png",
		"scale": 0.25,
        "flip": True,
	},
	OBJECT_TYPE_ADA_LOW_HEALTH: {
		"filename": "img/ada_low_health.png",
		"scale": 0.25,
        "flip": True,
	},
	OBJECT_TYPE_ALICE_DEAD: {
		"filename": "img/alice_dead.png",
		"scale": 0.25,
        "flip": True,
	},
	OBJECT_TYPE_ALICE_HURT: {
		"filename": "img/alice_hurt.png",
		"scale": 0.25,
        "flip": True,
	},
	OBJECT_TYPE_ALICE_IDLE: {
		"filename": "img/alice_idle.png",
		"scale": 0.25,
        "flip": True,
	},
	OBJECT_TYPE_ALICE_ATTACK: {
		"filename": "img/alice_attack.png",
		"scale": 0.25,
        "flip": True,
	},
	OBJECT_TYPE_ALICE_LOW_HEALTH: {
		"filename": "img/alice_low_health.png",
		"scale": 0.25,
        "flip": True,
	},
	OBJECT_TYPE_ARROW: {
		"filename": "img/arrow.png",
		"scale": 0.25,
        "flip": True,
        "angle": 90,
	},
	OBJECT_TYPE_BABBAGE_ATTACK: {
		"filename": "img/babbage_attack.png",
		"scale": 0.25,
        "flip": True,
	},
	OBJECT_TYPE_BABBAGE_DEAD: {
		"filename": "img/babbage_dead.png",
		"scale": 0.25,
        "flip": True,
	},
	OBJECT_TYPE_BABBAGE_HURT: {
		"filename": "img/babbage_hurt.png",
		"scale": 0.25,
        "flip": True,
	},
    OBJECT_TYPE_BABBAGE_IDLE: {
		"filename": "img/babbage_idle.png",
		"scale": 0.25,
        "flip": True,
	},
	OBJECT_TYPE_BABBAGE_LOW_HEALTH: {
		"filename": "img/babbage_low_health.png",
		"scale": 0.25,
        "flip": True,
	},
	OBJECT_TYPE_BLANK_PAGE: {
		"filename": "img/blank_page.png",
		"scale": 8.0,
	},
	OBJECT_TYPE_CONSOLE: {
		"filename": "img/console.png",
		"scale": 0.25,
	},
    OBJECT_TYPE_DEMON_ATTACK: {
		"filename": "img/demon_attack.png",
		"scale": 0.25,
	},
	OBJECT_TYPE_DEMON_DEAD: {
		"filename": "img/demon_dead.png",
		"scale": 0.25,
	},
	OBJECT_TYPE_DEMON_HURT: {
		"filename": "img/demon_hurt.png",
		"scale": 0.25,
	},
	OBJECT_TYPE_DEMON_IDLE: {
		"filename": "img/demon_idle.png",
		"scale": 0.2,
	},
    OBJECT_TYPE_GEAR: {
		"filename": "img/gear.png",
		"scale": 1.0,
	},
	OBJECT_TYPE_GHOST_ARCHER_ATTACK: {
		"filename": "img/ghost_archer_attack.png",
		"scale": 0.25,
	},
	OBJECT_TYPE_GHOST_ARCHER_DEAD: {
		"filename": "img/ghost_archer_dead.png",
		"scale": 0.25,
	},
	OBJECT_TYPE_GHOST_ARCHER_HURT: {
		"filename": "img/ghost_archer_hurt.png",
		"scale": 0.25,
	},
    OBJECT_TYPE_GHOST_ARCHER_IDLE: {
		"filename": "img/ghost_archer_idle.png",
		"scale": 0.25,
	},
	OBJECT_TYPE_LABEL_QUIT: {
		"filename": "img/label_quit.png",
		"scale": 100/432,
	},
	OBJECT_TYPE_LABEL_RESIDUES: {
		"filename": "img/label_residues.png",
		"scale": 0.3,
	},
	OBJECT_TYPE_LABEL_START: {
		"filename": "img/label_start.png",
		"scale": 100/464,
	},
    OBJECT_TYPE_LIGHTNING_BOLT: {
		"filename": "img/lightning_bolt.png",
		"scale": 0.25,
        "angle": -90
	},
	OBJECT_TYPE_MAGE_ATTACK: {
		"filename": "img/mage_attack.png",
		"scale": 0.25,
	},
	OBJECT_TYPE_MAGE_DEAD: {
		"filename": "img/mage_dead.png",
		"scale": 0.25,
	},
	OBJECT_TYPE_MAGE_HURT: {
		"filename": "img/mage_hurt.png",
		"scale": 0.25,
	},
    OBJECT_TYPE_MAGE_IDLE: {
		"filename": "img/mage_idle.png",
		"scale": 0.25,
	},
	OBJECT_TYPE_NPC_A_PORTRAIT: {
		"filename": "img/npc_a_portrait.png",
		"scale": 1.0,
	},
	OBJECT_TYPE_NPC_B_PORTRAIT: {
		"filename": "img/npc_b_portrait.png",
		"scale": 1.0,
	},
	OBJECT_TYPE_NPC_OVERWORLD_DOWN: {
		"filename": "img/npc_overworld_down.png",
		"scale": 0.25,
	},
    OBJECT_TYPE_NPC_OVERWORLD_LEFT_RIGHT: {
		"filename": "img/npc_overworld_left_right.png",
		"scale": 0.25,
	},
	OBJECT_TYPE_NPC_OVERWORLD_UP: {
		"filename": "img/npc_overworld_up.png",
		"scale": 0.25,
	},
	OBJECT_TYPE_OVERWORLD_BUILDING: {
		"filename": "img/overworld_building.png",
		"scale": 0.5,
	},
	OBJECT_TYPE_OVERWORLD_GRASS: {
		"filename": "img/overworld_grass.png",
		"scale": 0.125,
	},
    OBJECT_TYPE_OVERWORLD_PATH: {
		"filename": "img/overworld_path.png",
		"scale": 0.25,
	},
	OBJECT_TYPE_OVERWORLD_PUZZLE: {
		"filename": "img/overworld_puzzle.png",
		"scale": 0.25,
	},
	OBJECT_TYPE_OVERWORLD_TREE: {
		"filename": "img/overworld_tree.png",
		"scale": 0.25,
	},
    OBJECT_TYPE_PC_OVERWORLD_DOWN: {
		"filename": "img/pc_overworld_down.png",
		"scale": 0.25,
	},
	OBJECT_TYPE_PC_OVERWORLD_LEFT_RIGHT: {
		"filename": "img/pc_overworld_left_right.png",
		"scale": 0.25,
	},
	OBJECT_TYPE_PC_OVERWORLD_UP: {
		"filename": "img/pc_overworld_up.png",
		"scale": 0.25,
	},
	OBJECT_TYPE_TITLE_SCREEN: {
		"filename": "img/title_screen.png",
		"scale": 0.55,
	},
}
#endregion
#region animation descriptors
ANIMATION_DESCRIPTORS = {
	OBJECT_TYPE_FIRE_SPELL: {
		ANIMATION_TYPE_IDLE: {
			"filename": "img/fire_spell/idle",
			"image_count": 121,
			"scale": 0.25,
            "base_frame": 1,
		},
	},
	OBJECT_TYPE_ICE_SPELL: {
		ANIMATION_TYPE_IDLE: {
			"filename": "img/ice_spell/idle",
			"image_count": 78,
			"scale": 0.25,
            "base_frame": 1,
		},
	},
	OBJECT_TYPE_LOGO: {
		ANIMATION_TYPE_IDLE: {
			"filename": "img/logo/idle",
			"image_count": 152,
			"scale": 0.5,
            "base_frame": 0
		},
	},
}
#endregion
