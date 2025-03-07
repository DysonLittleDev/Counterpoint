import mido
from operator import itemgetter, attrgetter
from enum import Enum, auto
import typing

class Score:
    def __init__(self, trackArray):
        self.trackArray = trackArray
        self.melodyArray = []

        for track in self.trackArray:
            self.melodyArray.append(Melody.fromMidiTrack(track))

    def testFailures(self, melodyComparisonTuple):
        failureArray = []

        melody1 = self.melodyArray[melodyComparisonTuple[0]]
        melody2 = self.melodyArray[melodyComparisonTuple[1]]

        for chord in melody1.chordArray:
            otherChord = melody2.getAtTime(chord.time)

            comparison = chord.notes[0].compare(otherChord.notes[0])

            #Test for rule 0

            if not (comparison == Note.NoteRelationship.UNISON_OR_OCTAVE
                or comparison == Note.NoteRelationship.MAJOR_THIRD
                or comparison == Note.NoteRelationship.MINOR_THIRD
                or comparison == Note.NoteRelationship.MAJOR_SIXTH
                or comparison == Note.NoteRelationship.MINOR_SIXTH
                or comparison == Note.NoteRelationship.PERFECT_FIFTH):
                failureArray.append((CounterpointFailureType.INTERVAL_NOT_CONSONANT_FAILURE, chord.time))

        #test other rules lol

        return failureArray


class Melody:

    def __init__(self, chordArray):
        self.chordArray = chordArray

    def getAtTime(self, time):
        return next((x for x in self.chordArray if x.time == time), None)

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

    def isParallel(self, other):
        return self.time == other.time and self.duration == other.duration


    # these are for time
    def __lt__(self, other):
        return self.time < other.time
    def __gt__(self, other):
        return self.time > other.time


class Note:
    class NoteRelationship(Enum):
        UNISON_OR_OCTAVE = 0
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
    INTERVAL_NOT_CONSONANT_FAILURE = 0
    COUNTERMELODY_LAST_NOTE_NOT_TONIC_FAILURE = 1
    PARALLEL_FIFTH_FAILURE = 2
    PARALLEL_OCTAVE_FAILURE = 3
    DIRECT_OCTAVE_OR_FIFTH_FAILURE = 4
    TRITONE_AVOIDANCE_FAILURE = 5
    AUGMENTED_SECOND_AVOIDANCE_FAILURE = 6
    KEY_SIGNATURE_ADHERENCE_FAILURE = 7
    LEADING_TONE_RESOLUTION_AT_CADENCE_FAILURE = 8
    COUNTERMELODY_STEPS_OR_LEAPS_FAILURE = 9
    COUNTERMELODY_SUCCESSIVE_LEAPS_FAILURE = 10
    SIMULTANEOUS_LEAPS_FAILURE = 11
    SIMULTANEOUS_OPPOSITE_LEAPS_FAILURE = 12
