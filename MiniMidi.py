import sys

import mido
import time
import math
import string


class MiniMidi:

    def __init__(self):

        self.port = mido.open_output()

    def openFile(self, filename: string) -> mido.MidiFile:
        return mido.MidiFile(filename=filename)

    def getTempo(self, headerTrack: mido.MidiTrack) -> int:
        return (x for x in headerTrack if isinstance(x, mido.MetaMessage) and x.type == 'set_tempo').tempo

    def getTimeSignature(self, headerTrack: mido.MidiTrack) -> tuple[int, int]:
        time_signature = (x for x in headerTrack if isinstance(x, mido.MetaMessage) and x.type == 'time_signature')

        return (time_signature.numerator, time_signature.denominator)

    def playTracks(self, file: mido.MidiFile, trackNums: list[int]):
        headerTrack = file.tracks[0]
        tempo = (x for x in headerTrack if isinstance(x, mido.MetaMessage) and x.type == 'set_tempo').tempo
        time_signature = (x for x in headerTrack if isinstance(x, mido.MetaMessage) and x.type == 'time_signature')


        trackRange: list[mido.MidiTrack] = []
        trackCountup: list[int] = []
        for num in trackNums:
            trackRange.append(file.tracks[num])
            trackCountup.append(0)


        while any(len(x) > 0 for x in trackRange):

            def popMessage(message: mido.Message):
                if isinstance(message, mido.MetaMessage):
                    print(message)
                else:
                    self.port.send(message)

            shortestWait: int = sys.maxsize # infinity?

            for i, track in enumerate(trackRange):


                if len(track) == 0:
                    continue
                if trackCountup[i] >= track[0].time:
                    popMessage(track.pop(0))
                    while len(track) > 0 and track[0].time == 0:
                        popMessage(track.pop(0))
                    trackCountup[i] = 0

                if len(track) > 0:
                    shortestWait = min(shortestWait, track[0].time - trackCountup[i])


            trackCountup = [x + shortestWait for x in trackCountup]


            print(shortestWait)
            print(trackCountup)
            time.sleep(mido.tick2second(shortestWait, file.ticks_per_beat, tempo))
