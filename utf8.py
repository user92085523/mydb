def encode(string):
    utf8_bytes = bytearray()
    for char in string:
        utf8_bytes += char_to_bytes(char)
    return utf8_bytes


def decode(utf8_bytes):
    l_codepoint = bytes_to_codepoints(utf8_bytes)
    return get_str_from_codepoints(l_codepoint)


#utf8_bytesに'\x00'の空データをサイズ分まで追加
#最終BYTEが文字もしくは文字の一部である場合、文字BYTE分削除され'\x00'で埋められる
def fill(utf8_bytes, size=256):
    if len(utf8_bytes) >= size:
        utf8_bytes = remove_overflow_chars(utf8_bytes, size)
    for i in range(size - len(utf8_bytes)):
        utf8_bytes += b'\x00'
    return utf8_bytes


def lfill_0(utf8_bytes, size):
    buff = bytearray()
    for i in range(size - len(utf8_bytes)):
        buff += b'\x30'
    return buff + utf8_bytes


def remove_overflow_chars(utf8_bytes, size):
    for i in range(len(utf8_bytes) - size):
        utf8_bytes.pop()
    for i in range(4):
        poped = utf8_bytes.pop()
        if poped >> 6 != 0x2:
            break
    return utf8_bytes


def char_to_bytes(char):
    codepoint = ord(char)
    bytesize = get_char_bytesize(codepoint)
    return encode_to_binary(codepoint, bytesize)


def bytes_to_codepoints(utf8_bytes):
    l_char = []
    buff = []
    cnt = 0
    for byte in utf8_bytes:
        if byte < 128:
            l_char.append(byte)
        elif cnt == 0:
            if byte >> 5 == 0x6:
                cnt = 1
            elif byte >> 4 == 0xe:
                cnt = 2
            elif byte >> 3 == 0x1e:
                cnt = 3
            buff.append(byte)
        else:
            cnt -= 1
            buff.append(byte)
            if cnt == 0:
                l_char.append(decode_multi_bytes_char(buff))
                buff = []
    return l_char


def decode_multi_bytes_char(l_byte):
    size = len(l_byte)
    b = 0x0
    for i in range(size):
        if i == 0:
            b = l_byte[i] & (0x1 << 7 - size) - 1
        else:
            b = b << 6 | l_byte[i] & 0x3f
    return b


def get_str_from_codepoints(l_codepoint):
    string = ''
    for cp in l_codepoint:
        string += chr(cp)
    return string


def get_char_bytesize(codepoint):
    if codepoint < 0x80:
        return 1
    elif 0x80 <= codepoint < 0x800:
        return 2
    elif 0x800 <= codepoint < 0x10000:
        return 3
    elif 0x10000 <= codepoint < 0x11ffff:
        return 4
    else:
        return None


def encode_to_binary(codepoint, bytesize):
    if bytesize == 1:
        return codepoint.to_bytes(bytesize)
    bits_a = 0x0
    bits_b = 0x0
    for i in reversed(range(bytesize)):
        bits_a += codepoint << i * 2 & 0x3f << i * 8
        if i + 1 == bytesize:
            bits_b = (0x1 << bytesize) - 1 << 8 - bytesize + i * 8
            continue
        bits_b = 0x80 << i * 8 | bits_b
    return (bits_a | bits_b).to_bytes(bytesize)