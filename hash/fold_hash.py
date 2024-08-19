import argparse


def hash_32(input):
    hash = 0

    input_bytes = bytes(input, encoding='utf-8')
    input_bytes_len = len(input_bytes)

    i = 0
    while i < input_bytes_len:
        current_fold = input_bytes[i]
        current_fold <<= 8

        if i + 1 < input_bytes_len:
            current_fold |= input_bytes[i + 1]
            current_fold <<= 8

        hash += current_fold

        i += 2

    return hash


def hash_64(input):
    hash = 0

    input_bytes = bytes(input, encoding='utf-8')
    input_bytes_len = len(input_bytes)

    i = 0
    while i < input_bytes_len:
        current_fold = input_bytes[i]
        current_fold <<= 8

        if i + 1 < input_bytes_len:
            current_fold |= input_bytes[i + 1]
            current_fold <<= 8

        if i + 2 < input_bytes_len:
            current_fold |= input_bytes[i+2]
            current_fold <<= 8

        if i + 3 < input_bytes_len:
            current_fold |= input_bytes[i+3]

        hash += current_fold

        i += 4

    return hash


def main(args):

    hash32 = hash_32(args.input)
    hash64 = hash_64(args.input)

    print(f'32 bit hash {hex(hash32)}')
    print(f'64 bit hash {hex(hash64)}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        add_help='Returns a folded hash value of the input string', epilog='Happy Hashing')
    parser.add_argument('input')

    main(parser.parse_args())
