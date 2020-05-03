#!/usr/bin/python3

from subprocess import check_output, Popen, CalledProcessError
import json
import os

EMPTY_WS_WALLPAPER_PATH = os.path.expanduser("~/Pictures/Wallpaper")
OCCUPIED_WS_WALLPAPER_PATH = os.path.expanduser("~/Pictures/BlurredWallpaper")

def GetCurrWs():
    try:
        wsS = check_output(["i3-msg", "-t", "get_workspaces"]).decode()
    except CalledProcessError as e:
        print("Error while getting i3 workspaces: ", e)
        return False, False

    ws = json.loads(wsS)
    for _ws in ws:
        if _ws['visible'] and _ws['focused']:
            return _ws['name'], _ws["output"]

    return False, False

def changeWal(wallPath):
    cmd = "feh --bg-fill " + wallPath
    Popen(cmd.split())

def main():
    currWs, monitor = GetCurrWs()
    if not currWs:
        return
    try:
        treeS = check_output(["i3-msg", "-t", "get_tree"]).decode()
    except CalledProcessError as e:
        print("Error while getting i3 tree: ", e)

    tree = json.loads(treeS)
    for tree_nodes in tree['nodes']:
        if tree_nodes['name'] != monitor:
            continue
        for content in tree_nodes['nodes']:
            if content['name'] != 'content':
                continue
            ws = None
            for _ws in content['nodes']:
                if _ws['name'] == currWs:
                    ws = _ws
                    break
            # print(ws)
            if ws is not None:
                if len(ws['nodes']) > 0:
                    changeWal(OCCUPIED_WS_WALLPAPER_PATH)
                else:
                    changeWal(EMPTY_WS_WALLPAPER_PATH)
                return True
            else:
                changeWal(EMPTY_WS_WALLPAPER_PATH)

if __name__ == "__main__":
    main()
