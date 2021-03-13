#!/usr/bin/python

import yaml
import subprocess
import pywal
import shutil
import cv2
import argparse
from pathlib import Path
from typing import Dict

THEMES_PATH = Path('~/.config/themes').expanduser()
X_COLORS_FILENAME = '.xcolors'
PARSED_THEME_FILENAME = '.theme'
WALLPAPER_DIRNAME = 'walls'
WAL_COLORS_PATH = Path('~/.cache/wal/colors').expanduser()
ALACRITTY_CONF_PATH = Path('~/.config/alacritty/alacritty.yml').expanduser()

COLOR_MAP = {'*.foreground:': 'foreground', '*.background:': 'background', '*.cursor:': 'cursorColor',
             '*.cursorColor:': 'cursorColor', '*.color0:': 'black', '*.color8:': 'bright_black',
             '*.color1:': 'red', '*.color9:': 'bright_red', '*.color2:': 'green',
             '*.color10:': 'bright_green', '*.color3:': 'yellow', '*.color11:': 'bright_yellow',
             '*.color4:': 'blue', '*.color12:': 'bright_blue', '*.color5:': 'magenta',
             '*.color13:': 'bright_magenta', '*.color6:': 'cyan', '*.color14:': 'bright_cyan',
             '*.color7:': 'white', '*.color15:': 'bright_white'}


def getThemeNames():
    return [x.stem for x in THEMES_PATH.glob('*.theme') if x.name not in ['.theme', 'current.theme']]


def getTheme(themeName: str):
    global THEMES_PATH
    theme_path = THEMES_PATH.joinpath(f'{themeName}.theme')
    if not theme_path.exists():
        raise FileNotFoundError(theme_path)

    with open(str(theme_path), 'r') as fh:
        theme = yaml.safe_load(fh)

    return theme


def getWallpaperPath(theme: Dict, themeName: str):
    global THEMES_PATH, WALLPAPER_DIRNAME

    if 'wallpaper' in theme:
        imagePath1 = Path(THEMES_PATH.joinpath(
            WALLPAPER_DIRNAME).joinpath(theme['wallpaper']))
    else:
        imagePath1 = THEMES_PATH.joinpath(
            WALLPAPER_DIRNAME).joinpath(f'{themeName}.jpg')
        imagePath2 = THEMES_PATH.joinpath(
            WALLPAPER_DIRNAME).joinpath(f'{themeName}.png')
    if imagePath1.exists():
        imagePath = str(imagePath1)
    elif imagePath2.exists():
        imagePath = str(imagePath2)
    else:
        raise FileNotFoundError(imagePath1)

    #  Copy to Pictures and create lockscreen image
    shutil.copy2(imagePath, Path('~/Pictures/Wallpaper').expanduser())
    img = cv2.imread(imagePath)
    bImg = cv2.blur(img, (600, 600))
    bSuccess, bBuffer = cv2.imencode(".jpg", bImg)
    if bSuccess:
        bBuffer.tofile(Path('~/Pictures/BlurredWallpaper').expanduser())
    else:
        print("Error while blurring wallpaper : ", bSuccess)

    return imagePath


def processTheme(themeName: str):
    global COLOR_MAP, THEMES_PATH, PARSED_THEME_FILENAME, WALLPAPER_DIRNAME, X_COLORS_FILENAME

    theme = getTheme(themeName)
    imagePath = getWallpaperPath(theme, themeName)

    # Get the colors from pywal or custom colors from theme file
    termColors = {}
    xColors = ""

    if theme['terminal_colors'] == 'pywal':
        _termColors = pywal.colors.get(imagePath)
        for k in ['special', 'colors']:
            for key, value in _termColors[k].items():
                xColors += f"*.{key}: {value}\n"
                if '*.'+key+':' not in COLOR_MAP:
                    print(f"*.{key}: not in color map: {COLOR_MAP}")
                else:
                    _key = COLOR_MAP['*.'+key+':']
                    termColors[_key] = value
    else:
        i = 0
        _termColors = theme['terminal_colors'].split()
        while i < len(_termColors):
            key = _termColors[i].strip()
            if key != '!':
                color = _termColors[i+1].strip()
                xColors += '{} {}\n'.format(key, color)
                if key not in COLOR_MAP:
                    print(f'{key} not present in the map')
                else:
                    termColors[COLOR_MAP[key]] = color
            i += 2
    xColors += f"rofi.color-window: #a0{termColors['red'][1:]}, {termColors['background']}, {termColors['background']}\n"
    xColors += f"rofi.color-normal: #00000000,	{termColors['background']}, #00000000, {termColors['background']}, {termColors['red']}"

    # Write x colors to file
    with THEMES_PATH.joinpath(X_COLORS_FILENAME).open('w') as fh:
        fh.write(xColors)

    # remove the '#' from colors for qtile to work properly
    cleanedTermColors = termColors
    # for k, v in termColors.items():
    #     if isinstance(v, str) and v.startswith('#'):
    #         v = v[1:]
    #     cleaned_term_colors[k] = v

    # Convert color variables in theme file to color codes
    theme['terminal_colors'] = cleanedTermColors
    _theme = dict(theme)
    _theme['wallpaper'] = imagePath
    for key, value in theme.items():
        if key == 'terminal_colors':
            continue
        if key == "gradient" and value is not None:
            i = 0
            while i < 7:
                if i < len(value):
                    _theme["gradient" +
                           str(i+1)+"title"] = cleanedTermColors[value[i]]
                    _theme["gradient" +
                           str(i+1)+"body"] = cleanedTermColors[value[i]]
                else:
                    _theme["gradient" +
                           str(i+1)+"title"] = cleanedTermColors[value[-1]]
                    _theme["gradient" +
                           str(i+1)+"body"] = cleanedTermColors[value[-1]]
                i += 1
        elif value in cleanedTermColors:
            _theme[key] = cleanedTermColors[value]

    # set up colors if not gradients
    if "gradient" not in theme:
        _theme['gradienttitlefg'] = _theme["titlefg"]
        _theme['gradientbodyfg'] = _theme["bodyfg"]
        i = 0
        while i < 7:
            _theme["gradient"+str(i+1)+"title"] = _theme["titlebg"]
            _theme["gradient"+str(i+1)+"body"] = _theme["bodybg"]
            i += 1
    else:
        _theme['gradienttitlefg'] = _theme['gradientbodyfg'] = _theme['gradient']['fg'] if 'fg' in theme['gradient'] else _theme['titlefg']
        del _theme['gradient']

    # create colors file for vscode
    vc_colors = ["" for x in range(16)]
    for i, name in enumerate(["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]):
        vc_colors[i] = theme['terminal_colors'][name]
        vc_colors[i+8] = theme['terminal_colors']['bright_'+name]

    vc_colors = "\n".join(vc_colors)

    if not WAL_COLORS_PATH.exists():
        WAL_COLORS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with WAL_COLORS_PATH.open('w') as f:
        f.write(vc_colors)

    with THEMES_PATH.joinpath(PARSED_THEME_FILENAME).open('w') as fh:
        yaml.dump(_theme, fh, default_flow_style=False)

    return _theme, imagePath


def main(theme='yosmite', list=False):
    # List themes and exit
    if list:
        print(f'Available themes: {getThemeNames()}')
        return

    theme, wallpaperPath = processTheme(theme)

    # set wallpaper
    print(wallpaperPath)
    try:
        subprocess.Popen(['feh', '--bg-fill', f'{wallpaperPath}'])
    except Exception as e:
        try:
            subprocess.Popen(['gsettings', 'set', 'org.gnome.desktop.background',
                              'picture-uri', f'file:///{wallpaperPath}'])
        except Exception as e:
            print(e)

    # appy x colors
    try:
        subprocess.call(
            ['xrdb', '-load', str(THEMES_PATH.joinpath(X_COLORS_FILENAME))])
        subprocess.call(
            ['xrdb', '-merge', str(Path('~/.Xresources').expanduser())])
    except subprocess.CalledProcessError as e:
        print(e)

    # apply alacritty colors
    if ALACRITTY_CONF_PATH is None:
        return

    # Read the current file to get other configs
    if not ALACRITTY_CONF_PATH.exists():
        print("Invalid Alacritty path : {}".format(ALACRITTY_CONF_PATH))
        return
    with ALACRITTY_CONF_PATH.open('r') as fh:
        alaConf = yaml.safe_load(fh)

    for key in theme['terminal_colors']:
        if 'ground' in key:
            alaConf['colors']['primary'][key] = theme['terminal_colors'][key]
        elif 'bright' in key:
            alaConf['colors']['bright'][key.split(
                '_')[1]] = theme['terminal_colors'][key]
        else:
            alaConf['colors']['normal'][key] = theme['terminal_colors'][key]
    
    with ALACRITTY_CONF_PATH.open('w') as fh:
        yaml.dump(alaConf, fh, default_flow_style=False)

def _cliEntry():
    parser = argparse.ArgumentParser()
    parser.add_argument('theme', default='yosmite', nargs='?',
                        help='The name of the theme to set, say "yosmite"')
    parser.add_argument('--list', '-l', action='store_true',
                        help='List the themes available')
    args = parser.parse_args()
    main(args.theme, args.list)

if __name__ == '__main__':
    _cliEntry()
