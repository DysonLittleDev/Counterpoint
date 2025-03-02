import mido
from operator import itemgetter, attrgetter
from enum import Enum, auto

class Score:

    def __init__(self, trackArray):
        self.trackArray = trackArray
        self.melodyArray = []

        for track in self.trackArray:
            self.melodyArray.append(Melody.fromMidiTrack(track))




class Melody:

    def __init__(self, noteArray):

        self.noteArray = noteArray

    @classmethod
    def fromMidiTrack(cls, track):

        onOffMessageArray = []

        for message in track:
            if message.type == 'note_on' or message.type == 'note_off':
                onOffMessageArray.append(message)

        onMessageCache = []
        chordArray = []
        runningTime = 0
        for message in onOffMessageArray:
            if message.type == 'note_on':
                runningTime += message.time
                onMessageCache.append((message, runningTime))


            if message.type == 'note_off':
                runningTime += message.time
                for cached in onMessageCache:
                    if cached[0].note == message.note:
                        noteValues = [Note(message.note)]
                        noteDuration = runningTime - cached[1]

                        chordArray.append(Chord(noteValues, cached[1], noteDuration))

                        onMessageCache.remove(cached)
                        break

        # cleanup simultaneous notes
        # this is prolly a mess to read but trust me

        newChordArray = []

        while len(chordArray) > 0:
            currentChord = chordArray.pop(0)
            foundFlag = False
            for newChord in newChordArray:
                if currentChord.time == newChord.time and currentChord.duration == newChord.duration:
                    newChord.notes.extend(currentChord.notes)
                    foundFlag = True
                    break

            if not foundFlag:
                newChordArray.append(currentChord)


        return Melody(newChordArray)

class Chord:

    def __init__(self, notes, time, duration):
        self.notes = notes
        self.time = time
        self.duration = duration



    # these are for time
    def __lt__(self, other):
        return self.time < other.time
    def __gt__(self, other):
        return self.time > other.time


class Note:
    class NoteRelationship(Enum):
        UNISON = 0
        MINOR_SECOND = 1
        MAJOR_SECOND = 2
        MINOR_THIRD = 3
        MAJOR_THIRD = 4
        PERFECT_FOURTH = 5
        TRITONE = 6
        PERFECT_FIFTH = 7
        MINOR_SIXTH = 8
        MAJOR_SIXTH = 9
        MINOR_SEVENTH = 10
        MAJOR_SEVENTH = 11


    def __init__(self, value):
        self.value = value


    def relate(self, other):
        return Note.NoteRelationship((self.value - other.value) % 12)

class CounterpointFailureType(Enum):
    TEST1 = 0
