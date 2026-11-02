from collections import defaultdict

from .bits_data import BitsData


class ShannonFano:
    @staticmethod
    def _create_probability_list(string: bytes) -> [(int, int)]:
        probability = defaultdict(int)
        for b in string:
            probability[b] += 1
        probability_list = [(prob, key) for key, prob in probability.items()]
        probability_list.sort(reverse=True)
        return probability_list

    @staticmethod
    def _get_symbol_code_table(string: bytes) -> defaultdict[int, str]:
        symbol_code_table = defaultdict(str)

        def create_table(probability: [(int, bytes)], sm: int, code: str = "") -> None:
            if len(probability) == 0:
                return
            if len(probability) == 1:
                symbol_code_table[probability[0][1]] = code
                return

            sum_of_prob = 0
            ind = 0
            while sum_of_prob * 2 < sm:
                sum_of_prob += probability[ind][0]
                ind += 1
            create_table(probability[:ind], sum_of_prob, code + "0") # можно оптимизировать, но это потом
            create_table(probability[ind:], sm - sum_of_prob, code + "1")

        pl = ShannonFano._create_probability_list(string)
        create_table(pl, sum(i[0] for i in pl))
        return symbol_code_table

    @staticmethod
    def _prob_encode(prob: defaultdict[int, str]) -> bytes:
        """l:s l:c"""
        result = b""
        for key, code in prob.items():
            b_code = code.encode()
            result += (
                int.to_bytes(1, 1, "big") +
                int.to_bytes(key, 1, "big") +
                int.to_bytes(len(b_code), 1, "big") +
                b_code
            )
        result += int.to_bytes(0, 1, "big")
        return result

    @staticmethod
    def encode(string: bytes) -> bytes:
        pt = ShannonFano._get_symbol_code_table(string)
        data = BitsData()
        for byte in string:
            data.append_data(pt[byte])
        return (
                ShannonFano._prob_encode(pt) +
                int.to_bytes(data._last_bit_size, 1, "big")
                + data.to_bytes()
                )

    @staticmethod
    def _prob_decode(string: bytes) -> (defaultdict[str, int], int):
        """l:s l:c"""
        prob = defaultdict(int)
        ind = 0
        while string[ind] != 0:
            key_len = string[ind]
            key = string[ind + 1]
            b_code_len = string[ind + 2]
            b_code = string[ind + 3:ind + 3 + b_code_len].decode()
            ind += 3 + b_code_len
            prob[b_code] = key
        return prob, ind + 1

    @staticmethod
    def decode(string: bytes) -> bytes:
        code_to_symbol, ind = ShannonFano._prob_decode(string)
        data = BitsData(string[ind + 1:], string[ind])
        b = bytearray()
        for d in data.extract_data(code_to_symbol):
            b.append(d)
        return bytes(b)
