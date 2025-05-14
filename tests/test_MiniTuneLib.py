from pathlib import Path
import src.MiniMidi as MiniMidi
import src.MiniTuneLib as MiniTuneLib


def get_score(filepath: str):
    """Return score written in a .score file

    Args:
        filepath (str): path to a valid .score file
    """
    return


'''
NOTE: This test uses midi files in tests/midi-tests. I have not added any
test cases in that folder yet. 

For each midi file, there should be a ".score" file that 
describes its correct score and they should both have the same file name. For example, 
for midi file "midi1.mid", there should also be "midi1.score" that has midi1's correct score.
Until the format of score is finalized, there is a function stub named get_score() that will
be used in the unit test below
'''


def test_midiScore():
    test_dir = Path("tests/midi-tests")
    test_files: list[Path] = []
    score_files: dict[str, Path] = {}

    for item in test_dir.iterdir():
        if item.is_file() and item.suffixes == ['.mid']:
            test_files.append(item)
        elif item.is_file() and item.suffixes == ['.score']:
            score_files[item.stem] = item

    not_failed = True
    # Score all midi files in midi-tests and check if the score is correct.
    # Test doesn't stop on first failure, and will print errors for all tests.
    # Failure will happen at the end of the test
    for test in test_files:
        print(f"Scoring {test.name}")
        mini = MiniMidi.MiniMidi()
        file = mini.openFile(test)

        # TODO: this is supposed to be where test is scored and where
        #       the correct score is read
        try:
            actual_score = MiniTuneLib.Score(file.tracks)
            correct_score = get_score(score_files[test.stem])
        except Exception as e:
            print(f"Error [{e}] raised when scoring {test.name}")
            not_failed = False
            continue

        if actual_score != correct_score:
            print(
                f"Wrong score for {test.name}: "
                f"Actual score is {actual_score} "
                f"but correct score is {correct_score}"
            )
            not_failed = False

    assert (not_failed)
