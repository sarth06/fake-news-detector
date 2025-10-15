import pytest
from app import gemini_client as gc

def test_local_analyzer_short_text():
    text = "Breaking news! Unbelievable secret discovered."
    res = gc._local_analyzer(text, None)
    assert 'label' in res
    assert 'confidence' in res

def test_local_analyzer_numbers_without_links():
    text = "Study claims 95% of students prefer X."
    res = gc._local_analyzer(text, None)
    assert res['confidence'] <= 0.5
