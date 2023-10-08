from datetime import datetime

from whisper_note.transcription import Transcriptions


def test_transcription_iter() -> None:
    t = Transcriptions(False)
    it1, it2 = iter(t), iter(t)
    assert it1 is not it2
    t.add_phrase(datetime.now(), "1", 1)
    t.add_phrase(datetime.now(), "2", 2)

    next_or_zeroes = lambda it: next(it, (0, 0, 0)) or (0, 0, 0)
    assert next_or_zeroes(it1)[1] == "1"
    assert next_or_zeroes(it2)[1] == "1"
    assert next_or_zeroes(it1)[1] == "2"
    assert next_or_zeroes(it2)[1] == "2"
    assert next(it1) is None
    assert next(it2) is None
