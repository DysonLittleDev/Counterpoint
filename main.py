import MiniMidi
import MiniTuneLib
import time

if __name__ == "__main__":
    mini = MiniMidi.MiniMidi()
    file = mini.openFile("MidiFiles/untitled.mid")

    # score = MiniTuneLib.Score(file.tracks)
    # mini.playTracks(file, range(len(file.tracks)))
