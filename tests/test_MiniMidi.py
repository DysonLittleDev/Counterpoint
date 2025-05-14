from pathlib import Path
import src.MiniMidi as MiniMidi
import mido

# NOTE: this test uses midi files in tests/midi-tests. i have not added any
# test cases in that folder yet.
def test_playTracks():
    test_dir: Path = Path("tests/midi-tests")
    test_files: list[Path] = []

    for item in test_dir.iterdir():
        if item.is_file() and item.suffixes == ['.mid']:
            test_files.append(item)

    # try to play each file in midi-tests. if an exception is raised,
    # print the error and which file it occurred on and move on to the
    # next file. any exception raised will cause this test to fail at the end
    not_failed: bool = True
    for test in test_files:
        midi: MiniMidi = MiniMidi.MiniMidi()
        file: mido.MidiFile = midi.openFile(test)
        try:
            midi.playTracks(file, range(len(file.tracks)))
        except Exception as e:
            print(f"Error [{e}] raised while playing {test.name}")
            not_failed = False
            continue

    assert(not_failed)