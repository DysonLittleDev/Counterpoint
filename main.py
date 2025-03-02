import MiniMidi
import MiniTuneLib
import time

if __name__ == "__main__":
    mini = MiniMidi.MiniMidi()
    file = mini.openFile("MidiFiles/Test.mid")

    score = MiniTuneLib.Score(file.tracks)
    #mini.playTracks(file.tracks, range(len(file.tracks)))
