from subprocess import check_output, CalledProcessError, Popen
import os
import argparse


def getSinks(getCurrent=False):
    currSink = -1
    sinks = []
    if getCurrent:
        sinksCmd = "pactl list short sinks"
        try:
            _sinks = check_output(
                sinksCmd, shell=True).decode().strip().split('\n')
        except CalledProcessError as e:
            print("Error while getting current sinks: ", e)
            return [], currSink
        for index, sink in enumerate(_sinks):
            tokenized = sink.split('\t')
            sinks.append(tokenized[0])
            if tokenized[-1] == 'RUNNING':
                currSink = index
    else:
        sinksCmd = "pactl list short sinks|awk '{print $1}'"
        try:
            sinks = check_output(sinksCmd, shell=True).decode().strip().split()
        except CalledProcessError as e:
            print("Error while getting current sinks: ", e)
            return [], currSink

    return sinks, currSink


def muteAllSinks(cmd=1):
    '''
    cmd
    0 - Unmute
    1 - mute
    2 - toggle
    '''
    cmds = {0: 0, 1: 1, 2: 'toggle'}
    if cmd not in cmds:
        print("Invalid mute argument, Muting")
        cmd = 1
    sinks, _ = getSinks()
    if not sinks:
        return False
    for sink in sinks:
        muteCmd = f'pactl set-sink-mute {sink} {cmds[cmd]}'.split()
        Popen(muteCmd)

    return True


def changeVolume(value="+5%"):
    value = value.strip()
    if value == "0":
        return True
    sinks, _ = getSinks()
    if not sinks:
        return False
    if value[-1] != '%':
        value += "%"
    for sink in sinks:
        volCmd = f'pactl set-sink-volume {sink} {value}'.split()
        Popen(volCmd)
    return True


def routeInputsToSink(sink='next'):
    '''
     get sink inputs
     sink: can be next/prev or any sink index
    '''
    sinks, currSinkIndex = getSinks(getCurrent=True)
    toSink = 0
    sink = sink.strip().lower()
    if sink == 'next':
        toSink = currSinkIndex + 1 if currSinkIndex < len(sinks)-1 else 0
    elif sink == 'prev':
        toSink = currSinkIndex - 1 if currSinkIndex > 0 else len(sinks) - 1
    else:
        try:
            toSink = sinks.index(sink)
        except ValueError as e:
            print("Invalid sink({}), expected {}".format(
                sink, ['prev', 'next', *sinks]))
            return False

    # get sink inputs
    try:
        inputs = check_output(
            "pactl list short sink-inputs|awk '{print $1}'", shell=True).decode().strip().split()
    except CalledProcessError as e:
        print("Error while getting sink inputs: ", e)
        return False
    Popen("pacmd set-default-sink {}".format(sinks[toSink]).split())
    for inp in inputs:
        cmd = f'pactl move-sink-input {inp} {sinks[toSink]}'
        Popen(cmd.split())
    return True


def main(mute=-1, vol=False, route=False):
    parser = argparse.ArgumentParser(
        description="A command line utility to change all the audio sink input to the next/prev sink. Requires pulseaudio runnning")
    parser.add_argument('--vol', '-v', default=False,
                        help="set volume to the give value in percent. Incremental values can be given as +5%% or -10%%")
    parser.add_argument('--mute', '-m', default=-1, type=int,
                        help="Mute audio, 0 - Unmute, 1 - Mute, 2 - toggle")
    parser.add_argument('--route', '-r', default=False,
                        help="route all sink inpute to the next/prev/specific sink")
    args = parser.parse_args()

    _mute = mute if args.mute == -1 else args.mute
    _vol = vol if args.vol == False else args.vol
    _route = route if args.route == False else args.route

    if all([_mute == -1, _vol == False, _route == False]):
        print("No command specified.")
        return

    if _mute != -1:
        if not muteAllSinks(_mute):
            print("Command failed")
    if _vol != False:
        if not changeVolume(_vol):
            print("Command failed")
    if _route != False:
        if not routeInputsToSink(_route):
            print("Command failed")


if __name__ == '__main__':
    main()
