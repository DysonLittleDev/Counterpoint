import MiniMidi
import MiniTuneLib
import time

if __name__ == "__main__":
    mini = MiniMidi.MiniMidi()
    file = mini.openFile("MidiFiles/untitled.mid")

    # score = MiniTuneLib.Score(file.tracks)
    # mini.playTracks(file, range(len(file.tracks)))
    time_signature = mini.getTimeSignature(file.tracks[0])
    score = MiniTuneLib.Score(file.tracks, file.ticks_per_beat, time_signature)
    #mini.playTracks(file.tracks, range(len(file.tracks)))
