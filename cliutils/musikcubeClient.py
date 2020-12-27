import uuid
import asyncio
import subprocess
from queue import Queue, Empty
from enum import Enum
from typing import Optional
import json
import time
import websockets
from aiohttp import web
from argparse import ArgumentParser

TRACK_UPDATE_INTERVAL = 5
MAX_TRACK_LEN = 20
CMD_SERVER_PORT = 7907
MUSIKCUBE_PORT = 7905
MUSIKCUBE_PASSWORD = "myMusikcubeClient"
REQUEST_SCHEMA = {
    "name": "",
    "type": "request",
    "id": "",
    "device_id": "",
    "options": {}
}

cmdQueue = Queue()
currTrack = {
    'track': '',
    'updatedAt': time.time()
}
callback = None


class MusikCubeRequest(Enum):
    AUTH = 'authenticate'
    PLAYBACK_OVERVIEW = 'get_playback_overview'
    TOGGLE_PAUSE = 'pause_or_resume'
    STOP = 'stop'
    PREV_TRACK = 'previous'
    NEXT_TRACK = 'next'
    TOGGLE_SHUFFLE = 'toggle_shuffle'
    TOGGLE_REPEAT = 'toggle_repeat'
    TOGGLE_MUTE = 'toggle_mute'


def makeCmd(type: MusikCubeRequest, update: Optional[dict]):
    request = dict(REQUEST_SCHEMA)
    request.update({
        'name': type.value,
        'id': str(uuid.uuid4()),
        'type': 'request'
    })
    if update is not None:
        request.update(update)
    return json.dumps(request)


async def musikCubeSocket(port: int, device_id: str):
    uri = f'ws://localhost:{port}'
    while 1:
        try:
            async with websockets.connect(uri) as websocket:
                global currTrack, callback

                # send auth
                auth = makeCmd(MusikCubeRequest.AUTH, {'options': {
                    'password': MUSIKCUBE_PASSWORD}, 'device_id': device_id})
                await websocket.send(auth)

                while 1:
                    # send command if one exists
                    try:
                        cmd = cmdQueue.get_nowait()
                    except Empty:
                        cmd = None

                    if cmd is not None:
                        req = makeCmd(cmd, {'device_id': device_id})
                        await websocket.send(req)
                    elif not currTrack['track'] or time.time() - currTrack['updatedAt'] >= TRACK_UPDATE_INTERVAL:
                        req = makeCmd(MusikCubeRequest.PLAYBACK_OVERVIEW,
                                      {'device_id': device_id})
                        await websocket.send(req)

                    try:
                        _resp = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    except asyncio.exceptions.TimeoutError:
                        continue
                    resp = json.loads(_resp)
                    if resp['type'] in ['broadcast', 'response'] and resp['name'] in ['playback_overview_changed', 'get_playback_overview']:
                        if resp['options']['state'] == 'stopped':
                            currTrack = {'track': ' ',
                                         'updatedAt': time.time()}
                            continue
                        _totalTime = int(
                            resp['options']['playing_duration'])
                        _elapsedTime = int(
                            resp['options']['playing_current_time'])
                        totalTime = f'{_totalTime//60}:{0 if _totalTime%60 < 10 else "" }{_totalTime%60}'
                        elapsedTime = f'{_elapsedTime//60}:{0 if _elapsedTime%60 < 10 else "" }{_elapsedTime%60}'
                        _track = resp['options']['playing_track']['title']

                        if len(_track) < MAX_TRACK_LEN:
                            track = _track + (" " *
                                              (MAX_TRACK_LEN-len(_track)))
                        else:
                            track = _track[:MAX_TRACK_LEN-3] + '...'

                        currTrack = {'track': f'{track}   {elapsedTime}/{totalTime}',
                                     'updatedAt': time.time()}
                        if callback:
                            subprocess.Popen(callback, shell=True)
        except (websockets.exceptions.ConnectionClosedError, OSError):
            currTrack = {'track': ' ', 'updatedAt': time.time()}
            if callback:
                subprocess.Popen(callback, shell=True)
            await asyncio.sleep(1.0)


async def handleRecievedCmd(request):
    _cmd = await request.text()
    method = request.method
    if method == 'POST':
        cmd = None
        # Check if the command is valid
        for name, member in MusikCubeRequest.__members__.items():
            if _cmd == name:
                cmd = member
                break
        if cmd is None:
            print(f'Got invalid command: {_cmd}')
            return web.Response(status=422, text='Invalid command')
        cmdQueue.put(cmd)
        return web.Response(text='ok')
    elif method == 'GET':
        global currTrack
        return web.Response(text=currTrack['track'])


async def cmdListener(host: str, port: int):
    app = web.Application()
    app.add_routes([web.post('/', handleRecievedCmd),
                    web.get('/', handleRecievedCmd)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()


async def start():
    await asyncio.gather(
        musikCubeSocket(MUSIKCUBE_PORT, str(uuid.uuid4())),
        cmdListener("localhost", CMD_SERVER_PORT)
    )


def main():
    global callback, TRACK_UPDATE_INTERVAL
    parser = ArgumentParser(description="CLI for Musikcube")
    parser.add_argument('--updated-callback', '-c', default=callback,
                        help='Run any sh command when an update is recieved')
    parser.add_argument('--update-interval', '-u', default=TRACK_UPDATE_INTERVAL, type=int,
                        help=f'How often to get updates(in seconds). Default is {TRACK_UPDATE_INTERVAL}')
    args = parser.parse_args()
    callback = args.updated_callback
    TRACK_UPDATE_INTERVAL = args.update_interval
    asyncio.run(start())


if __name__ == '__main__':
    main()
