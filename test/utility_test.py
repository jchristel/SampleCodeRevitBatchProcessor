from duHast.Utilities import Utility as util

def test_EncodeAscii():
    assert util.encode_ascii("hello world") == b"hello world"
    assert util.encode_ascii("Привет, мир!") == b"?, ?!"
    assert util.encode_ascii("") == b""
    assert util.encode_ascii("123") == b"123"
    assert util.encode_ascii(123) == 123
    assert util.encode_ascii(None) == None
    assert util.encode_ascii(True) == True