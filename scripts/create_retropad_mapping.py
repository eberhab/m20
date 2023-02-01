#!/usr/bin/env python

import os
from typing import Union, List

header = '<?xml version="1.0"?><mameconfig version="10"><system name="m20"><input>'  #<keyboard tag=":kbd:m20" enabled="1" />
footer = '</input></system></mameconfig>'

# Define M20 Keyboard
# MAME 'KEYCODE_*': [Port, Mask, M20 key]
kbd = {
    'ESC': ['LINE0', 1, 'RESET'],
    'LALT': ['LINE0', 2, '<  >'],
    'A': ['LINE0', 4, 'a  A'],
    'B': ['LINE0', 8, 'b  B'],
    'C': ['LINE0', 16, 'c  C'],
    'D': ['LINE0', 32, 'd  D'],
    'E': ['LINE0', 64, 'e  E'],
    'F': ['LINE0', 128, 'f  F'],
    'G': ['LINE1', 1, 'g  G'],
    'H': ['LINE1', 2, 'h  H'],
    'I': ['LINE1', 4, 'i  I'],
    'J': ['LINE1', 8, 'j  J'],
    'K': ['LINE1', 16, 'k  K'],
    'L': ['LINE1', 32, 'l  L'],
    'M': ['LINE1', 64, ',  ?'],
    'N': ['LINE1', 128, 'n  N'],
    'O': ['LINE2', 1, 'o  O'],
    'P': ['LINE2', 2, 'p  P'],
    'Q': ['LINE2', 4, 'q  Q'],
    'R': ['LINE2', 8, 'r  R'],
    'S': ['LINE2', 16, 's  S'],
    'T': ['LINE2', 32, 't  T'],
    'U': ['LINE2', 64, 'u  U'],
    'V': ['LINE2', 128, 'v  V'],
    'W': ['LINE3', 1, 'z  Z'],
    'X': ['LINE3', 2, 'x  X'],
    'Y': ['LINE3', 4, 'y  Y'],
    'Z': ['LINE3', 8, 'w  W'],
    '0': ['LINE3', 16, 'à 0'],
    '1': ['LINE3', 32, '£ 1'],
    '2': ['LINE3', 64, 'é 2'],
    '3': ['LINE3', 128, '"  3'],
    '4': ['LINE4', 1, "'  4"],
    '5': ['LINE4', 2, '(  5'],
    '6': ['LINE4', 4, '_  6'],
    '7': ['LINE4', 8, 'è 7'],
    '8': ['LINE4', 16, '^  8'],
    '9': ['LINE4', 32, 'ç 9'],
    'MINUS': ['LINE4', 64, ')  °'],
    'EQUALS': ['LINE4', 128, '-  +'],
    'OPENBRACE': ['LINE5', 1, 'ì ='],
    'CLOSEBRACE': ['LINE5', 2, '$  &'],
    'COLON': ['LINE5', 4, 'm  M'],
    'QUOTE': ['LINE5', 8, 'ù %'],
    'TILDE': ['LINE5', 16, '*  §'],
    'COMMA': ['LINE5', 32, ';  .'],
    'STOP': ['LINE5', 64, ':  /'],
    'SLASH': ['LINE5', 128, 'ò !'],
    'SPACE': ['LINE6', 1, 'Space'],
    'ENTER': ['LINE6', 2, 'Enter'],
    'BACKSLASH': ['LINE6', 4, 'S1'],
    'BACKSPACE': ['LINE6', 8, 'S2'],
    'DEL_PAD': ['LINE6', 16, 'Keypad .'],
    '0_PAD': ['LINE6', 32, 'Keypad 0'],
    'ENTER_PAD': ['LINE6', 64, 'Keypad 00'],
    '1_PAD': ['LINE6', 128, 'Keypad 1'],
    '2_PAD': ['LINE7', 1, 'Keypad 2'],
    '3_PAD': ['LINE7', 2, 'Keypad 3'],
    '4_PAD': ['LINE7', 4, 'Keypad 4'],
    '5_PAD': ['LINE7', 8, 'Keypad 5'],
    '6_PAD': ['LINE7', 16, 'Keypad 6'],
    '7_PAD': ['LINE7', 32, 'Keypad 7'],
    '8_PAD': ['LINE7', 64, 'Keypad 8'],
    '9_PAD': ['LINE7', 128, 'Keypad 9'],
    'PLUS_PAD': ['LINE8', 1, 'Keypad +'],
    'MINUS_PAD': ['LINE8', 2, 'Keypad -'],
    'ASTERISK': ['LINE8', 4, 'Keypad *'],
    'SLASH_PAD': ['LINE8', 8, 'Keypad /'],
    'TAB': ['MODIFIERS', 16, 'COMMAND'],
    'LCONTROL': ['MODIFIERS', 32, 'CTRL'],
    'RSHIFT': ['MODIFIERS', 64, 'R SHIFT'],
    'LSHIFT': ['MODIFIERS', 128, 'L SHIFT']
}

# Define RetroPad
# 'Button': 'JOYCODE_1_*'
pad = {
    'A': 'BUTTON1',
    'B': 'BUTTON2',
    'X': 'BUTTON3',
    'Y': 'BUTTON4',
    'L1': 'BUTTON5',
    'R1': 'BUTTON6',
    'L2': 'RZAXIS_NEG_SWITCH',
    'R2': 'ZAXIS_NEG_SWITCH',
    'L3': 'BUTTON9',
    'R3': 'BUTTON10',
    'SELECT': 'SELECT',
    'START': 'START',
    'UP': 'HAT1UP',
    'LEFT': 'HAT1LEFT',
    'RIGHT': 'HAT1RIGHT',
    'DOWN': 'HAT1DOWN',
    'A-UP': 'YAXIS_UP_SWITCH',
    'A-LEFT': 'XAXIS_LEFT_SWITCH',
    'A-RIGHT': 'XAXIS_RIGHT_SWITCH',
    'A-DOWN': 'YAXIS_DOWN_SWITCH'
}

def getpad(btn: str, id: Union[List, int] = 1):
    # Get RetroPad button config-name for a aingle pad (pad 1)
    # or a given list of pad IDs 
    # getpad('A', 1)
    # getpad('A', [1, 2])
    global pad
    if isinstance(id, list):
        return ' OR '.join([f'JOYCODE_{i}_{pad[btn]}' for i in id])
    else:
        return f'JOYCODE_{id}_{pad[btn]}'


def validate():
    # Validate the given mapping config for all games for existing keys
    global config, kbd, pad
    for game, cfg in config.items():
        if isinstance(cfg, str):
            continue
        for key in cfg.keys():
            assert not key.islower(), f'{game}: Key "{key}" is lowercase. Only uppercase allowed.'
            assert key in kbd.keys(), f'{game}: Key "{key}" is not an M20 keyboard key.'
        for key in cfg.values():
            keys = key if isinstance(key, list) else [key]
            for key in keys:
                assert not key.islower(), f'{game}: Btn "{key}" is lowercase. Only uppercase allowed.'
                assert key in pad.keys(), f'{game}: Btn "{key}" is not a RetroPad button.'


def port_cfg(kbd_key, pad_btn):
    # Compile a config entry for a single key
    # port_cfg('0', 'DOWN')
    global kbd, pad
    port = kbd[kbd_key][0]
    mask = kbd[kbd_key][1]
    kbd_key = 'KEYCODE_' + kbd_key
    s = f'<port tag=":kbd:m20:{port}" type="KEYBOARD" mask="{mask}" defvalue="0">'
    s += '<newseq type="standard">'
    if isinstance(pad_btn, list):
        s += ' OR '.join([kbd_key] + [getpad(b) for b in pad_btn])
    else:
        s += ' OR '.join([kbd_key, getpad(pad_btn)])  # getpad(pad_btn, [1, 2])
    s += '</newseq></port>'
    return s

def create_cmd(game, cmd_file, config_path, cmd_path, target_system):
    # create a cmd launch file
    global extra_settings, rom_paths, create_controller_config
    
    rom_path = rom_paths[target_system]
    if not os.path.exists(cmd_path):
        os.makedirs(cmd_path)
    with open(cmd_file, 'w') as f:
        f.write('mame m20 ')
        if game in extra_settings.keys():
            for k, v in extra_settings[game].items():
                f.write(f'-{k} {v} ')
        if create_controller_config:
            f.write(f'-ctrlrpath {rom_path}/{config_path}/ -ctrlr {game} ')
        else:
            f.write(f'-cfg_directory {rom_path}/{config_path}/{game}/ ')
        f.write(f'-rompath {rom_path} ')
        f.write(f'-flop1 {rom_path}/{game.split("_")[0]}.zip\n')

def create(target_system: str):
    # Create config and cmd launch files for alle games
    global config, create_controller_config, create_cmd_files

    print(f"## {target_system.upper()}")
    config_path = 'cfg' # A relative directory inside the roms directory
    cmd_path = 'cmd_' + target_system # A relative local directory
    for game, cfg in config.items():
        if create_controller_config:
            # controller config
            cfg_path = config_path
            cfg_file = f'{cfg_path}/{game}.cfg'
        else:
            # system config
            cfg_path = f'{config_path}/{game}'
            cfg_file = f'{cfg_path}/m20.cfg'

        if not os.path.exists(cfg_path):
            os.makedirs(cfg_path)

        if isinstance(cfg, str):
            # This game inherits its mapping from another game
            cfg = config[cfg]

        if create_cmd_files:
            cmd_file = f'{cmd_path}/{game}.cmd'
            print(f'Writing {cfg_file} and {cmd_file} ...')
            create_cmd(game, cmd_file, config_path, cmd_path, target_system)
        else:
            print(f'Writing {cfg_file} ...')

        with open(cfg_file, 'w') as f:
            f.write(header + '\n')
            for key, btn in cfg.items():
                f.write('    ' + port_cfg(key, btn) + '\n')
            f.write(footer + '\n')


### GAME SETTINGS ###

rom_paths = {
    'retropie': '/home/pi/RetroPie/roms/m20',
    'android':  '/storage/emulated/0/RetroArch/roms/m20'
}
# Create controller config (True) or system config (False)?
create_controller_config = True
# Create cmd files pointing at rom_path along with keyboard config?
create_cmd_files = True

# Per game config
# Adding an underscore to the game name considers this entry an
# alias definition: e.g. "bruecke_switch" being an alternate definition
# for the game "bruecke" To be played with the Switch JoyConds
# 'game name': {'keyboard key': 'retropad button'} (All CAPS!)
config = {
    'olioids': {
        '1_PAD': 'L1',
        '2_PAD': ['DOWN', 'A-DOWN', 'R1'],
        '4_PAD': ['LEFT', 'A-LEFT'],
        '6_PAD': ['RIGHT', 'A-RIGHT'],
        '8_PAD': ['UP', 'A-UP'],
        'Z': 'START',
        'N': 'SELECT',
        'F': 'A',
        'A': 'B',
        'SPACE': 'Y',
        'ENTER': 'X'
    },
    'flakschiessen': {
        'SPACE': ['A', 'B'],
        'J': 'START'
    },
    'bruecke': {
        'ENTER': 'X',
        'SPACE': 'A',
        'J': 'START',
        '1': ['L2', 'LEFT'],
        '2': ['R2', 'UP'],
        'STOP': ['L1', 'DOWN'],
        '0': ['R1', 'RIGHT']
    },
    'bruecke_switch': {
        'ENTER': 'X',
        'SPACE': 'A',
        'J': 'START',
        '1': ['L1', 'LEFT'],
        '2': ['R1', 'UP'],
        'STOP': ['L2', 'DOWN'],
        '0': ['R2', 'RIGHT']
    },
    'mauerschiessen': {
        'SPACE': ['A', 'X'],
        '0': 'DOWN',
        '2': 'UP',
        'J': 'START'
    },
    'othello': {
        'N': ['SELECT', 'B'],
        'J': 'START',
        '0': 'Y',
        '1': 'L1',
        '3': 'L2',
        'SPACE': 'A',
        'ENTER': 'X',
        '2': ['R1', 'DOWN', 'A-DOWN'],
        '4': ['R2', 'LEFT', 'A-LEFT'],
        '6': ['RIGHT', 'A-RIGHT'],
        '8': ['UP', 'A-UP']
    },
    'othello_en': {
        'N': ['SELECT', 'B'],
        'Z': 'START',
        '0': 'Y',
        '1': 'L1',
        '3': 'L2',
        'SPACE': 'A',
        'ENTER': 'X',
        '2': ['R1', 'DOWN', 'A-DOWN'],
        '4': ['R2', 'LEFT', 'A-LEFT'],
        '6': ['RIGHT', 'A-RIGHT'],
        '8': ['UP', 'A-UP']
    },
    'zweikampf': {
        'SPACE': ['A', 'B'],
        'J': 'START',
        '0': ['RIGHT', 'A-RIGHT'],
        '2': ['LEFT', 'A-LEFT']
    },
    'heimkehr': {
        'SPACE': 'A',
        '2': ['DOWN', 'A-DOWN'],
        '4': ['LEFT', 'A-LEFT'],
        '6': ['RIGHT', 'A-RIGHT'],
        '8': ['UP', 'A-UP'],
        'J': 'START'
    },
    'heimkehr1': 'heimkehr',
    'solitario': {
        '2_PAD': ['DOWN', 'A-DOWN'],
        '4_PAD': ['LEFT', 'A-LEFT'],
        '6_PAD': ['RIGHT', 'A-RIGHT'],
        '8_PAD': ['UP', 'A-UP'],
        'SPACE': 'A',
        'Q': 'START',
        'H': 'X',
        'C': 'B'
    },
    'topodrago': {
        '2_PAD': ['DOWN', 'A-DOWN'],
        '4_PAD': ['LEFT', 'A-LEFT'],
        '6_PAD': ['RIGHT', 'A-RIGHT'],
        '8_PAD': ['UP', 'A-UP'],
        'S': 'START',
        'N': 'SELECT'
    },
    'mazedaze': {
        '2_PAD': ['DOWN', 'A-DOWN'],
        '4_PAD': ['LEFT', 'A-LEFT'],
        '6_PAD': ['RIGHT', 'A-RIGHT'],
        '8_PAD': ['UP', 'A-UP']
    },
    'micromissiles': {
        '4': ['L1', 'UP', 'A-UP'],
        '6': ['R1', 'DOWN', 'A-DOWN'],
        '1': ['L2', 'LEFT', 'A-LEFT'],
        '3': ['R2', 'RIGHT', 'A-RIGHT'],
        '8': 'A',
        'S': 'START',
        'F': 'SELECT'
    },
    '3dmuehle': {
        '1': 'L1',
        '2': 'R1',
        '3': 'L2',
        '4': 'R2',
        'COLON': ['X','Y'],
        'ENTER': 'A'
    },
    'pacman': {
        '2': ['DOWN', 'A-DOWN'],
        '4': ['LEFT', 'A-LEFT'],
        '6': ['RIGHT', 'A-RIGHT'],
        '8': ['UP', 'A-UP'],
        'SPACE': 'A',
        'J': 'START',
        'N': 'SELECT'
    }
}

# Can be any MAME cmd line args
extra_settings = {
    'mauerschiessen': {'speed': 0.5},
    'bruecke': {'speed': 0.7},
    'flakschiessen': {'speed': 0.5},
    'othello': {'speed': 1.1},
    'zweikampf': {'speed': 0.5},
    'mazedaze': {'speed': 0.5}
}

### RUN ###

validate()
for target_system in rom_paths.keys():
    create(target_system)
