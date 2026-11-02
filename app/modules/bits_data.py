from collections import defaultdict


class BitsData:
    def __init__(self, b: bytes = b"", last_bit: int = 0) -> None:
        self._data: bytearray = bytearray(b)
        self._last_bit_size: int = last_bit

    def to_bytes(self) -> bytes:
        return bytes(self._data)

    def extract_data(self, code_symbol: defaultdict[str, int]):
        char = ""
        for ind, byte in enumerate(self._data):
            byte_end = 7
            if ind == len(self._data) - 1:
                byte_end = self._last_bit_size - 1
            for i in range(byte_end, -1, -1):
                if byte & (1 << i) != 0:
                    char += "1"
                else:
                    char += "0"
                if char in code_symbol:
                    yield code_symbol[char]
                    char = ""
        if len(char) != 0:
            raise Exception("corrupted data")

    def append_data(self, value: str) -> None:
        if not self._data:
            self._data.append(0)

        for char in value:
            self._data[-1] = (self._data[-1] << 1) | (char == "1")
            self._last_bit_size += 1

            if self._last_bit_size == 8:
                self._data.append(0)
                self._last_bit_size = 0