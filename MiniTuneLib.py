import mido
from operator import itemgetter, attrgetter
from enum import Enum, auto
import math
from dataclasses import dataclass
from typing import Self

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


class Note:
    class NoteRelationship(Enum):
        OCTAVE = 0
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
        UNISON = 12 # this and octave are "swapped" for math reasons


    def __init__(self, value: int):
        self.value = value


    def relate(self, other: Self) -> NoteRelationship:
        return 12 if self.value == other.value else Note.NoteRelationship((self.value - other.value) % 12)




class Chord:

    def __init__(self, notes: list[Note], time: int, duration: int):
        self.notes = notes
        self.time = time
        self.duration = duration
        self.value = notes[0].value

    def isParallel(self, other: Self) -> bool:
        return self.time == other.time and self.duration == other.duration

    def relate(self, other: Self) -> Note.NoteRelationship:
        if len(self.notes) != 1 or len(other.notes) != 1:
            raise Exception("Relating chords with multiple notes not supported!")
            # FIXME then support them lol

        return self.notes[0].relate(other.notes[0])

    # these are for time
    def __lt__(self, other: Self):
        return self.time < other.time
    def __gt__(self, other: Self):
        return self.time > other.time


class Phrase:

    def __init__(self, chordArray: list[Chord], startTime: int, duration: int):
        self.chordArray = chordArray
        self.startTime = startTime
        self.duration = duration

    def fully_within(self, chord: Chord) -> bool:
        return self.startTime <= chord.time and self.startTime + self.duration >= chord.time + chord.duration


class PhrasePair:

    def __init__(self, melodyPhrase: Phrase, countermelodyPhrase: Phrase):
        self.melodyPhrase = melodyPhrase
        self.countermelodyPhrase = countermelodyPhrase
        self.startTime = melodyPhrase.startTime
        self.duration = melodyPhrase.duration

class Melody:

    def __init__(self, chordArray: list[Chord]):

        self.chordArray = chordArray

    def getAtTime(self, time: int) -> Chord:
        return next((x for x in self.chordArray if x.time == time), None)

    @classmethod
    def fromMidiTrack(cls, track: mido.MidiTrack) -> Self:

        onOffMessageArray: list[mido.Message] = []

        for message in track:
            if message.type == 'note_on' or message.type == 'note_off':
                onOffMessageArray.append(message)

        onMessageCache: list[(mido.Message, int)] = []
        chordArray: list[Chord] = []
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

        newChordArray: list[Chord] = []

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



class Score:

    def __init__(self, trackArray: list[mido.MidiTrack], ticks_per_beat: int, time_signature: tuple[int, int]):
        self.trackArray = trackArray

        #numerator is beats per measure
        #denominator is what note is a beat
        #ticks_per_beat is ticks per beat lol

        self.beats_per_measure = time_signature[0]
        self.ticks_per_beat = ticks_per_beat
        self.ticks_per_measure = self.beats_per_measure * self.ticks_per_beat

        self.melodyArray: list[Melody] = []

        if len(self.trackArray) != 2:
            raise Exception("Must have exactly two tracks!")

        for track in self.trackArray:
            self.melodyArray.append(Melody.fromMidiTrack(track))

        self.melodyPhrases: list[Phrase] = []
        self.countermelodyPhrases: list[Phrase] = []
        self.phrasePairs: list[PhrasePair] = []

        for chord in self.melodyArray[0].chordArray:
            melodyPhrase = Phrase([chord], chord.time, chord.duration)
            counterChordList = []
            for counterChord in self.melodyArray[1].chordArray: # slightly inefficient- could pop chords from chordArray
                if melodyPhrase.fully_within(counterChord):
                    counterChordList.append(counterChord)

            counterPhrase = Phrase(counterChordList, chord.time, chord.duration)

            self.melodyPhrases.append(melodyPhrase)
            self.countermelodyPhrases.append(counterPhrase)
            self.phrasePairs.append(PhrasePair(melodyPhrase, counterPhrase))

        self.phrasePairs.sort(key=lambda x: x.startTime)




    def testFailures(self, phrasePairs: list[PhrasePair]) -> list[tuple[CounterpointFailureType, int]]:

        failureArray: list[tuple[CounterpointFailureType, int]] = []




        for i, phrasePair in enumerate(phrasePairs):
            melodyPhrase = phrasePair.melodyPhrase
            melodyPhraseFirstChord = melodyPhrase.chordArray[0]
            countermelodyPhrase = phrasePair.countermelodyPhrase

            #Test for rule 0
            #The interval between the given note and the note in your counter - melody should be consonant(major / minor
            #3rd or 6th, perfect unison, 5th, or octave, or a compound form).

            for chord in countermelodyPhrase.chordArray:
                comparison = melodyPhraseFirstChord.relate(chord)
                #FIXME this rule only applies to the first and middle chord?

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

            currentInterval = melodyPhraseFirstChord.relate(countermelodyPhrase.chordArray[0])


            if i > 0:
                previousInterval = phrasePairs[i - 1].melodyPhrase.chordArray[0].relate(phrasePairs[i - 1].countermelodyPhrase.chordArray[0])
                if currentInterval == previousInterval:
                    if currentInterval == Note.NoteRelationship.PERFECT_FIFTH:
                        failureArray.append((CounterpointFailureType.PARALLEL_FIFTH_FAILURE, melodyPhraseFirstChord.time))
                    elif currentInterval == Note.NoteRelationship.UNISON_OR_OCTAVE:
                        failureArray.append((CounterpointFailureType.PARALLEL_OCTAVE_FAILURE, melodyPhraseFirstChord.time))



            #Test for rule 4

            #Direct octaves or fifths: if both voices are moving in the same direction (and the upper voice by jump),
            # they should not move to a vertical octave or fifth.

            #FIXME doesn't check for jumps!
            #FIXME edge chords are first or last note in measure?

            melodyChordExtendedList = []
            countermelodyChordExtendedList = []

            if i > 0: melodyChordExtendedList.append(phrasePairs[i - 1].melodyPhrase.chordArray[-1])
            melodyChordExtendedList.extend(melodyPhrase.chordArray)
            if i < len(phrasePairs) - 1: melodyChordExtendedList.append(phrasePairs[i + 1].melodyPhrase.chordArray[0])

            if i > 0: countermelodyChordExtendedList.append(phrasePairs[i - 1].countermelodyPhrase.chordArray[-1])
            countermelodyChordExtendedList.extend(countermelodyPhrase.chordArray)
            if i < len(phrasePairs) - 1: countermelodyChordExtendedList.append(phrasePairs[i + 1].countermelodyPhrase.chordArray[0])

            #FIXME sanitize inputs

            sameDirection = True

            rule4FailureList = [] #only use if they end up being parallel

            melodyDirection = melodyChordExtendedList[0].value - melodyChordExtendedList[1].value
            countermelodyDirection = melodyChordExtendedList[0].value - melodyChordExtendedList[1].value

            for j in range(len(melodyChordExtendedList) - 1): #technically redundant on first comparison
                firstChord = melodyChordExtendedList[j + 1]
                secondChord = melodyChordExtendedList[j + 2]
                if (melodyDirection > 0 and firstChord.value < secondChord.value) or \
                        (melodyDirection < 0 and firstChord.value > secondChord.value):
                    relation = firstChord.relate(secondChord)
                    if relation == Note.NoteRelationship.PERFECT_FIFTH or relation == Note.NoteRelationship.OCTAVE:
                        rule4FailureList.append((CounterpointFailureType.DIRECT_OCTAVE_OR_FIFTH_FAILURE, firstChord.time))
                else:
                    sameDirection = False
                    break

            for j in range(len(countermelodyChordExtendedList) - 1):  # technically redundant on first comparison
                firstChord = countermelodyChordExtendedList[j + 1]
                secondChord = countermelodyChordExtendedList[j + 2]
                if (countermelodyDirection > 0 and firstChord.value < secondChord.value) or \
                        (countermelodyDirection < 0 and firstChord.value > secondChord.value):
                    relation = firstChord.relate(secondChord)
                    if relation == Note.NoteRelationship.PERFECT_FIFTH or relation == Note.NoteRelationship.OCTAVE:
                        rule4FailureList.append(
                            (CounterpointFailureType.DIRECT_OCTAVE_OR_FIFTH_FAILURE, firstChord.time))
                else:
                    sameDirection = False
                    break

            if sameDirection:
                failureArray.extend(rule4FailureList)

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





