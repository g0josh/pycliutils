#!/usr/bin/python

import os
import yaml
import subprocess
import json
import pywal
import shutil

COLOR_MAP = {'*.foreground:':'foreground','*.background:':'background','*.cursor:':'cursorColor',
        '*.cursorColor:':'cursorColor','*.color0:':'black', '*.color8:':'bright_black',
        '*.color1:':'red','*.color9:':'bright_red','*.color2:':'green',
        '*.color10:':'bright_green', '*.color3:':'yellow','*.color11:':'bright_yellow',
        '*.color4:':'blue', '*.color12:':'bright_blue', '*.color5:':'magenta',
        '*.color13:':'bright_magenta', '*.color6:':'cyan', '*.color14:':'bright_cyan',
        '*.color7:':'white','*.color15:':'bright_white'}
#ALACRITTY_CONF_PATH = os.path.expanduser('~/.config/alacritty/alacritty.yml')
ALACRITTY_CONF_PATH = None
X_COLORS_PATH = '~/.config/themes/.xcolors'
THEME_PATH = os.path.expanduser('~/.config/themes/current.theme')
PARSED_THEME_PATH = os.path.expanduser('~/.config/themes/.theme')
WALLPAPER_PATH = os.path.expanduser('~/.config/themes/walls')

def getTheme():
    global COLOR_MAP, PARSED_THEME_PATH, WALLPAPER_PATH
    with open(os.path.expanduser(THEME_PATH), 'r') as fh:
        theme = yaml.safe_load(fh)

    # get x colors and convert 
    # to human readable color keys
    _term_colors = {}
    x_colors = ""
    image_path = None
    if 'wallpaper' in theme :
        image_path = os.path.expanduser(os.path.join(WALLPAPER_PATH,theme['wallpaper']))
    if image_path is None:
        image_path = os.path.realpath(os.path.expanduser(THEME_PATH))
        image_path = os.path.basename(image_path).split('.')[0]
        image_path = os.path.join(WALLPAPER_PATH, image_path)
    if os.path.exists(image_path):
        shutil.copy2(image_path, os.path.expanduser('~/Pictures/Wallpaper'))
    else:
        raise IOError(f"{image_path} does not exist")
    if theme['terminal_colors'] == 'pywal':
        term_colors = pywal.colors.get(image_path)
        for k in ['special', 'colors']:
            for key, value in term_colors[k].items():
                x_colors += f"*.{key}: {value}\n"
                if '*.'+key+':' not in COLOR_MAP:
                    print(f"*.{key}: not in color map: {COLOR_MAP}")
                else:
                    _key = COLOR_MAP['*.'+key+':']
                    _term_colors[_key] = value
    else:
        i=0
        term_colors = theme['terminal_colors'].split()
        while i < len(term_colors):
            key = term_colors[i].strip()
            if key != '!':
                color = term_colors[i+1].strip()
                x_colors += '{} {}\n'.format(key, color)
                if key not in COLOR_MAP:
                    print(f'{key} not present in the map')
                else:
                    _term_colors[ COLOR_MAP[key]] = color
            i += 2
    x_colors += f"rofi.color-window: #a0{_term_colors['red'][1:]}, {_term_colors['background']}, {_term_colors['background']}\n"
    x_colors += f"rofi.color-normal: #00000000,	{_term_colors['background']}, #00000000, {_term_colors['background']}, {_term_colors['red']}"

    # Write x colors to a file 
    with open(os.path.expanduser(X_COLORS_PATH), 'w') as fh:
        fh.write(x_colors)

    # Convert varibles in Qtile colors to color codes
    theme['terminal_colors'] = _term_colors
    _theme = dict(theme)
    _theme['wallpaper'] = image_path
    for key, value in theme.items():
        if key == 'terminal_colors':
            continue
        if value in _term_colors:
            _theme[key] = _term_colors[value]
    with open(PARSED_THEME_PATH, 'w') as fh:
        yaml.dump(_theme, fh, default_flow_style=False)
    return _theme

def main():
    theme = getTheme()

    # appy x colors
    try:
        subprocess.call(['xrdb', '-load', os.path.expanduser(X_COLORS_PATH)])
        subprocess.call(['xrdb', '-merge', os.path.expanduser('~/.Xresources')])
    except subprocess.CalledProcessError as e:
        print(e)

    #apply alacritty colors
    if ALACRITTY_CONF_PATH is None:
        return
    with open(ALACRITTY_CONF_PATH, 'r') as fh:
        ala_conf = yaml.safe_load(fh)

    for key in theme['terminal_colors']:
        if 'ground' in key:
            ala_conf['colors']['primary'][key] = theme['terminal_colors'][key]
        elif 'bright' in key:
            ala_conf['colors']['bright'][key.split('_')[1]] = theme['terminal_colors'][key]
        else:
            ala_conf['colors']['normal'][key] = theme['terminal_colors'][key]
    with open(ALACRITTY_CONF_PATH, 'w') as fh:
        yaml.dump(ala_conf, fh, default_flow_style=False)

if __name__ == '__main__':
    main()
