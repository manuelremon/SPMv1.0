from targets.example import add

def test_add():
    # deliberately failing until agente lo arregle
    assert add(2, 2) == 4
    assert add(-1, 1) == 0
