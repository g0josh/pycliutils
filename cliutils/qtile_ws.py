#!/usr/bin/python3

import sys
import yaml
import subprocess
import argparse

from libqtile.command import Client

LAYOUT_ICONS = {'columns':'HHH','monadtall':'[]=',
        'monadwide':'TTT','max':'[ ]','treetab':'|[]'}

def _main():
    parser = argparse.ArgumentParser(description="Get or set qtile workspaces")
    parser.add_argument("cmd", type=str, help="command can be 'get' or 'set'")
    parser.add_argument("--pid", "-p", type=str, help="Gets the workspace status for the screen displaying polybar with this pid. Should be passed with 'get' command"),
    parser.add_argument("--ws", "-w", type=str, help="Sets this workspace as active on current screen. Should be passed with 'set' command"),
    args = parser.parse_args()
    cmd = args.cmd
    pid = args.pid
    set_ws = args.ws

    client = Client()
    groups = client.groups()
    curr_group = client.group.info()
    with open('/tmp/polybar_info', 'r') as fh:
        d = yaml.safe_load(fh)
    screens = d['screens']
    formats = d['formats']
    separator = d['separator']

    if cmd == 'get':
        if not pid:
            print("--pid is required when using get command")
            sys.exit(0)
        result = ""
        for ws in groups:
            if ws == 'scratchpad':
                continue
            if ws == curr_group['name']:
                if pid == screens[str(curr_group['screen'])]['pid']:
                    if result:
                        result = formats['layoutWs'].replace('%label%',LAYOUT_ICONS[curr_group['layout']]) + result
                    else:
                        result = formats['layoutWs'].replace('%label%',LAYOUT_ICONS[curr_group['layout']])
                    result = result + separator + formats['activeWs'].replace('%label%', curr_group['label'])
                else:
                    result = result + separator + formats['activeWsOther'].replace('%label%', curr_group['label'])
            elif groups[ws]['screen'] is not None:
                if pid == screens[str(groups[ws]['screen'])]['pid']:
                    result = result + separator + formats['visibleWs'].replace('%label%', groups[ws]['label'])
                else:
                    result = result + separator + formats['visibleWsOther'].replace('%label%', groups[ws]['label'])
            elif client.groups()[ws]['windows']:
                result = result + separator + formats['occupiedWs'].replace('%label%', groups[ws]['label'])
        return result
    elif cmd == 'set':
        if not set_ws:
            print("--ws is required when using set command")
            sys.exit(0)
        if not set_ws.isdigit():
            _ws = int(curr_group['name'])
            if set_ws in ['next', '+1']:
                set_ws = str(_ws+1) if _ws+1 <= len(groups)-1 else '1'
            elif set_ws in ['prv','prev','previous','-1']:
                set_ws = str(_ws-1) if _ws-1 >= 1 else str(len(groups)-1)
            else:
                sys.exit(1)
        elif set_ws not in groups:
            sys.exit(1)
        client.group[set_ws].toscreen()
        try:
            subprocess.call(['polybar-msg', 'hook', 'qtileWs', '1'])
        except subprocess.CalledProcessError as e:
            print(e)

def main():
    print(_main())

if __name__ == '__main__':
    print(_main())

