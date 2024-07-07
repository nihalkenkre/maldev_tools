import argparse


def xor(string, key):
    xor_string = ''

    k = 0
    for s in range(len(string)):
        if k == len(key):
            k = 0

        i = (ord(string[s]) ^ ord(key[k]))
        xor_string += chr(i)

        k += 1

    return xor_string


def main(args):
    string = list(args.string)
    key = list(args.key)

    xor_string = xor(string, key)

    print(f'String: {[hex(ord(s))for s in string]}')
    print(f'Xored : {[hex(ord(x))for x in xor_string]}')
    print(f'Key: {[hex(ord(k))for k in key]}')
    print(f'Length: {len(xor_string)}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('string', help='String to XOR')
    parser.add_argument('key', default='00000',
                        help='Key to XOR the INPUT_STRING with')

    args = parser.parse_args()

    main(args)
