import mido
from operator import itemgetter, attrgetter
from enum import Enum, auto

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

        cache_previous_chord_tuple = ()

        for chord in melody1.chordArray:
            otherChord = melody2.getAtTime(chord.time)

            comparison = chord.notes[0].compare(otherChord.notes[0])

            #Test for rule 0
            #The interval between the given note and the note in your counter - melody should be consonant(major / minor
            #3rd or 6th, perfect unison, 5th, or octave, or a compound form).

            if not (comparison == Note.NoteRelationship.UNISON_OR_OCTAVE
                or comparison == Note.NoteRelationship.MAJOR_THIRD
                or comparison == Note.NoteRelationship.MINOR_THIRD
                or comparison == Note.NoteRelationship.MAJOR_SIXTH
                or comparison == Note.NoteRelationship.MINOR_SIXTH
                or comparison == Note.NoteRelationship.PERFECT_FIFTH):
                failureArray.append((CounterpointFailureType.INTERVAL_NOT_CONSONANT_FAILURE, chord.time))

            #Test for rule 1
            #If the counter - melody is above the given melody, then the last note of the counter - melody should
            #be in the tonic chord. If the counter - melody is below the given melody, then the last note of the
            #counter - melody should be the tonic or third of the tonic chord.

            #Test for rule 2 & 3

            #Parallel fifths: if the previous harmonic interval was a fifth,
            # your next note should not create the same harmonic interval again.
            #Parallel octaves: if the previous harmonic interval was an octave,
            # your next note should not create the same harmonic interval again.

            previous_comparison = cache_previous_chord_tuple[0].notes[0].compare(cache_previous_chord_tuple[1].notes[0])

            if comparison == Note.NoteRelationship.PERFECT_FIFTH and previous_comparison == Note.NoteRelationship.PERFECT_FIFTH:
                failureArray.append((CounterpointFailureType.PARALLEL_FIFTH_FAILURE, chord.time))
            #FIXME might fail for unison
            elif comparison == Note.NoteRelationship.UNISON_OR_OCTAVE and previous_comparison == Note.NoteRelationship.UNISON_OR_OCTAVE:
                failureArray.append((CounterpointFailureType.PARALLEL_OCTAVE_FAILURE, chord.time))


            cache_previous_chord_tuple = (chord, otherChord)

            #Test for rule 4

            #Direct octaves or fifths: if both voices are moving in the same direction (and the upper voice by jump),
            # they should not move to a vertical octave or fifth.

            #Test for rule 5

            #Avoid the tritone — the diminished fifth or augmented fourth interval — both melodic (between notes
            # in your melody) and harmonic (between your note and the given note above or below it).

            #Test for rule 6

            #Avoid augmented 2nds, both melodic (between notes in your melody) and harmonic (between your note
            # and the given note above or below it).

            #Test for rule 7

            #Use notes in the key signature only. The only exception allowed is a sharp for the leading tone
            # in a minor scale.

            #Test for rule 8

            #Leading tone resolution at cadence: if your second-to-last note is the leading tone,
            # you should resolve that up a half-step to the tonic at the cadence.

            #Test for rule 9

            #Your counter-melody should move in steps, or in leaps of a 3rd, 4th, 5th, or 6th.

            #Your counter-melody should not contain multiple successive large leaps (5th or 6th) in the same direction.

            #Test for rule 10

            #Your counter melody should not contain more than 3 leaps in a row.

            #Test for rule 11
            #Avoid simultaneous leaps in the same direction.

            #Test for rule 12
            #Simultaneous opposite leaps are only allowed if both voices leap by a third,
            # or one voice leaps by a third while the other voice leaps by a fourth.




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
