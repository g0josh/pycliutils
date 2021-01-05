#!/usr/bin/python3
# -*- coding: utf-8 -*-

import subprocess
import os
import sys
import yaml
import argparse

POWER_ICONS = {'power':'%{T3}%{T-}','reboot':'%{T3}%{T-}','lock':'%{T3}%{T-}',
        'logout':'%{T3}%{T-}', 'cancel':'%{T3}%{T-}'}
POLY_INFO_PATH = '/tmp/polybar_info'
PARSED_THEME_PATH = os.path.expanduser('~/.config/themes/.theme')

def getInterfaces():
    interfaces = {'lan':[], 'wlan':[]}
    for w in os.listdir('/sys/class/net'):
        if w.startswith('w'):
            interfaces['wlan'].append(w)
        elif w.startswith('e'):
            interfaces['lan'].append(w)
    return interfaces

def setupMonitors(exec=False):
    try:
        o = subprocess.check_output(['xrandr']).decode()
    except subprocess.CalledProcessError as e:
        print(e.output.decode().strip())
        return

    cmd = ["xrandr"]
    connected = []
    x = 0
    for i,e in enumerate(o.split('\n')):
        if not 'connected' in e:
            continue

        name = e.strip().split()[0]
        if ' connected' in e:
            res = o.split('\n')[i+1].strip().split()[0]
            cmd += ['--output', name, '--mode', res,
                '--pos', "{}x{}".format(x, 0), '--rotate', 'normal']
            x += int(res.split('x')[0])
            connected.append(name)
        elif 'disconnected' in e:
            cmd += ['--output', name, '--off']
    if exec:
        try:
            if sys.version_info[0] < 3:
                subprocess.call(cmd)
            else:
                subprocess.run(cmd)
        except subprocess.CalledProcessError as e:
            print(e.output.decode().strip())
    return connected

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exec-xrandr", "-x", action='store_true', help="Discover and setup monitors")
    parser.add_argument('--theme-path', '-t', type=str, default=PARSED_THEME_PATH, help="Path to the parsed theme file")
    args = parser.parse_args()

    with open(args.theme_path, 'r') as fh:
        theme = yaml.safe_load(fh)
    if 'occupiedbg' not in theme:
        theme['occupiedbg'] = theme['bodybg']
    if 'occupiedfg' not in theme:
        theme['occupiedfg'] = theme['bodyfg']
    if 'bartopborder' not in theme:
        theme['bartopborder'] = 0
    if 'barbottomborder' not in theme:
        theme['barbottomborder'] = 0
    if 'barrightborder' not in theme:
        theme['barrightborder'] = 0
    if 'barleftborder' not in theme:
        theme['barleftborder'] = 0
    if 'bottombar' not in theme:
        theme['bottombar'] = 'false'
    if 'leftmoduleprefix' not in theme:
        theme['leftmoduleprefix'] = '█'
    if 'leftmodulesuffix' not in theme:
        theme['leftmodulesuffix'] = '█'
    if 'rightmoduleprefix' not in theme:
        theme['rightmoduleprefix'] = '█'
    if 'rightmodulesuffix' not in theme:
        theme['rightmodulesuffix'] = '█'

    formats = {}
    formats['layoutWs'] = f'%{{B#00000000}}%{{F{theme["titlebg"]}}}{theme["leftmoduleprefix"]}%{{F-}}%{{B-}}%{{B{theme["titlebg"]}}}%{{F{theme["titlefg"]}}}{" "*theme["wspadding"]}%icon%{" "*theme["wspadding"]}%{{F-}}%{{B-}}%{{B{theme["background"]}}}%{{F{theme["titlebg"]}}}{theme["leftmodulesuffix"]}%{{F-}}%{{B-}}'
    formats['activeWs'] = f'%{{B{theme["background"]}}}%{{F{theme["focusedbg"]}}}{theme["leftmoduleprefix"]}%{{F-}}%{{B-}}%{{B{theme["focusedbg"]}}}%{{F{theme["focusedfg"]}}}{" "*theme["wspadding"]}%{{T3}}%name% %icon%%{{T-}}{" "*theme["wspadding"]}%{{F-}}%{{B-}}%{{B{theme["background"]}}}%{{F{theme["focusedbg"]}}}{theme["leftmodulesuffix"]}%{{F-}}%{{B-}}'
    formats['occupiedWs'] = f'%{{B{theme["background"]}}}%{{F{theme["occupiedbg"]}}}{theme["leftmoduleprefix"]}%{{F-}}%{{B-}}%{{B{theme["occupiedbg"]}}}%{{F{theme["occupiedfg"]}}}{" "*theme["wspadding"]}%{{T3}}%name% %icon%%{{T-}}{" "*theme["wspadding"]}%{{F-}}%{{B-}}%{{B{theme["background"]}}}%{{F{theme["occupiedbg"]}}}{theme["leftmodulesuffix"]}%{{F-}}%{{B-}}'
    formats['visibleWsOther'] = f'%{{B{theme["background"]}}}%{{F{theme["altbg"]}}}{theme["leftmoduleprefix"]}%{{F-}}%{{B-}}%{{B{theme["altbg"]}}}%{{F{theme["altfg"]}}}{" "*theme["wspadding"]}%{{T3}}%name% %icon%%{{T-}}{" "*theme["wspadding"]}%{{F-}}%{{B-}}%{{B{theme["background"]}}}%{{F{theme["altbg"]}}}{theme["leftmodulesuffix"]}%{{F-}}%{{B-}}'
    formats['urgentWs'] = f'%{{B{theme["background"]}}}%{{F{theme["urgentbg"]}}}{theme["leftmoduleprefix"]}%{{F-}}%{{B-}}%{{B{theme["urgentbg"]}}}%{{F{theme["urgentfg"]}}}{" "*theme["wspadding"]}%{{T3}}%name% %icon%%{{T-}}{" "*theme["wspadding"]}%{{F-}}%{{B-}}%{{B{theme["background"]}}}%{{F{theme["urgentbg"]}}}{theme["leftmodulesuffix"]}%{{F-}}%{{B-}}'
    
    formats['timeTitle'] = f'%{{B{theme["background"]}}}%{{F{theme["titlebg"]}}}{theme["leftmoduleprefix"]}%{{F-}}%{{B-}}%{{B{theme["titlebg"]}}}%{{F{theme["titlefg"]}}}{" "*theme["titlepadding"]}%{{T3}}%{{T-}}{" "*theme["titlepadding"]}%{{F-}}%{{B-}}%{{B{theme["bodybg"]}}}%{{F{theme["titlebg"]}}}{theme["leftmodulesuffix"]}%{{F-}}%{{B-}}'
    bg = theme['gradient3title'] if 'gradient3title' in theme else theme['titlebg']
    fg = theme['gradienttitlefg'] if 'gradienttitlefg' in theme else theme['titlefg']
    formats['utilizationTitle'] = f'%{{B{theme["background"]}}}%{{F{bg}}}{theme["rightmoduleprefix"]}%{{F-}}%{{B-}}%{{B{bg}}}%{{F{fg}}}{" "*theme["titlepadding"]}%{{T3}}%{{T-}}{" "*theme["titlepadding"]}%{{F-}}%{{B-}}%{{B{bg}}}%{{F{bg}}}{theme["rightmodulesuffix"]}%{{F-}}%{{B-}}'
    bg = theme['gradient4title'] if 'gradient4title' in theme else theme['titlebg']
    formats['temperatureTitle'] = f'%{{B{theme["background"]}}}%{{F{bg}}}{theme["rightmoduleprefix"]}%{{F-}}%{{B-}}%{{B{bg}}}%{{F{fg}}}{" "*theme["titlepadding"]}%{{T3}}%{{T-}}{" "*theme["titlepadding"]}%{{F-}}%{{B-}}%{{B{bg}}}%{{F{bg}}}{theme["rightmodulesuffix"]}%{{F-}}%{{B-}}'

    poly_vars = {}
    # power menu widgets
    poly_vars["poweropen"]= f'%{{B{theme["background"]}}}%{{F{theme["gradient7title"]}}}{theme["rightmoduleprefix"]}%{{F-}}%{{B-}}%{{B{theme["gradient7title"]}}}%{{F{theme["titlefg"]}}}{" "*theme["titlepadding"]}{POWER_ICONS["power"]}{" "*theme["titlepadding"]}%{{F-}}%{{B-}}%{{B#00000000}}%{{F{theme["gradient7title"]}}}{theme["rightmodulesuffix"]}%{{F-}}%{{B-}}'
    poly_vars['powerclose']= f'%{{B{theme["background"]}}}%{{F{theme["gradient7title"]}}}{theme["rightmoduleprefix"]}%{{F-}}%{{B-}}%{{B{theme["gradient7title"]}}}%{{F{theme["titlefg"]}}}{" "*theme["titlepadding"]}{POWER_ICONS["cancel"]}{" "*theme["titlepadding"]}%{{F-}}%{{B-}}%{{B#00000000}}%{{F{theme["gradient7title"]}}}{theme["rightmodulesuffix"]}%{{F-}}%{{B-}}'
    poly_vars['reboot']= f'%{{B{theme["background"]}}}%{{F{theme["gradient7title"]}}}{theme["rightmoduleprefix"]}%{{F-}}%{{B-}}%{{B{theme["gradient7title"]}}}%{{F{theme["titlefg"]}}}{" "*theme["bodypadding"]}{POWER_ICONS["reboot"]}{" "*theme["bodypadding"]}%{{F-}}%{{B-}}%{{B{theme["background"]}}}%{{F{theme["gradient7title"]}}}{theme["rightmodulesuffix"]}%{{F-}}%{{B-}}'
    poly_vars['poweroff']= f'%{{B{theme["background"]}}}%{{F{theme["gradient7title"]}}}{theme["rightmoduleprefix"]}%{{F-}}%{{B-}}%{{B{theme["gradient7title"]}}}%{{F{theme["titlefg"]}}}{" "*theme["bodypadding"]}{POWER_ICONS["power"]}{" "*theme["bodypadding"]}%{{F-}}%{{B-}}%{{B{theme["background"]}}}%{{F{theme["gradient7title"]}}}{theme["rightmodulesuffix"]}%{{F-}}%{{B-}}'
    poly_vars['logout']= f'%{{B{theme["background"]}}}%{{F{theme["gradient7title"]}}}{theme["rightmoduleprefix"]}%{{F-}}%{{B-}}%{{B{theme["gradient7title"]}}}%{{F{theme["titlefg"]}}}{" "*theme["bodypadding"]}{POWER_ICONS["logout"]}{" "*theme["bodypadding"]}%{{F-}}%{{B-}}%{{B{theme["background"]}}}%{{F{theme["gradient7title"]}}}{theme["rightmodulesuffix"]}%{{F-}}%{{B-}}'
    poly_vars['lock']= f'%{{B{theme["background"]}}}%{{F{theme["gradient7title"]}}}{theme["rightmoduleprefix"]}%{{F-}}%{{B-}}%{{B{theme["gradient7title"]}}}%{{F{theme["titlefg"]}}}{" "*theme["bodypadding"]}{POWER_ICONS["lock"]}{" "*theme["bodypadding"]}%{{F-}}%{{B-}}%{{B{theme["background"]}}}%{{F{theme["gradient7title"]}}}{theme["rightmodulesuffix"]}%{{F-}}%{{B-}}'
    interfaces = getInterfaces()
    connected = setupMonitors(args.exec_xrandr)
    _connected = {}
    subprocess.call(['killall', 'polybar'])
    subprocess.Popen(["feh", "--bg-fill", os.path.expanduser("~/Pictures/Wallpaper"), "--no-fehbg"])
    for i, monitor in enumerate(connected):
        try:
            os.environ['POLY_MONITOR'] = monitor
            os.environ['POLY_POWER_OPEN'] = poly_vars['poweropen']
            os.environ['POLY_POWER_CLOSE'] = poly_vars['powerclose']
            os.environ['POLY_POWEROFF'] = poly_vars['poweroff']
            os.environ['POLY_REBOOT'] = poly_vars['reboot']
            os.environ['POLY_LOGOUT'] = poly_vars['logout']
            os.environ['POLY_LOCK'] = poly_vars['lock']
            for index, wlan in enumerate(interfaces['wlan']):
                os.environ[f'POLY_WLAN{index+1}'] = wlan
            for index, lan in enumerate(interfaces['lan']):
                os.environ[f'POLY_LAN{index+1}'] = lan
                
            for key in theme:
                _key = str('POLY_'+key.upper())
                os.environ[_key] = str(theme[key])
            for key in formats:
                _key = str('POLY_'+key.upper())
                os.environ[_key] = str(formats[key])
            o = subprocess.Popen(['polybar', '-r', os.environ['WM']])
            #o = subprocess.Popen(['polybar', '-r', 'i3']) 
            _connected[str(i)] = {'name':monitor, 'pid':str(o.pid)}
        except Exception as e:
            print(e)
    with open(POLY_INFO_PATH, 'w') as fh:
        yaml.dump({'formats':formats,
            'screens':_connected,'separator':theme['moduleseparator']}, fh)

if __name__ == '__main__':
    main()
