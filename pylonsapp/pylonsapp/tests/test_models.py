from pylonsapp import model

def test_files():
    f = model.Files()

def test_animals():
    a = model.Animal()
    o = model.Owner()
    a.owner = o
    assert a.owner is o

