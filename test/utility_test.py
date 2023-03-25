from duHast.Utilities import Utility as util

def test_EncodeAscii():
    assert util.EncodeAscii("hello world") == b"hello world"
    assert util.EncodeAscii("Привет, мир!") == b"?, ?!"
    assert util.EncodeAscii("") == b""
    assert util.EncodeAscii("123") == b"123"
    assert util.EncodeAscii(123) == 123
    assert util.EncodeAscii(None) == None
    assert util.EncodeAscii(True) == True