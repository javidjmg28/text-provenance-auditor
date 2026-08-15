from text_provenance_auditor.segments import analyse_segments


def test_long_text_is_segmented():
    text = " ".join(f"word{i}" for i in range(950))
    segments = analyse_segments(text, target_words=400)
    assert len(segments) == 3
    assert segments[0].word_count == 400
    assert segments[-1].word_count == 150
