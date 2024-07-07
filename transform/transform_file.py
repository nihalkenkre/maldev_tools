import os
import argparse


def xor(input_bytes, key):
    output_bytes = []

    k = 0
    for s in range(len(input_bytes)):
        if k == len(key):
            k = 0

        i = (input_bytes[s] ^ ord(key[k]))
        output_bytes.append(i)

        k += 1

    return output_bytes


def main(args):
    output_lines = []

    output_file_path = args.output_file_path

    with open(args.input_file_path, 'rb') as input_file:
        input_lines = input_file.readlines()

        for input_line in input_lines:
            if args.sub_command == 'xor':
                output_lines.append(xor(list(input_line), list(args.key)))
            elif args.sub_command == 'passthrough':
                output_lines.append(input_line)

    if args.binary:
        with open(output_file_path, 'wb') as output_file:
            for xored_line in output_lines:
                output_file.write(bytes(xored_line))

        print('Transformed data written to', output_file_path)

    else:
        with open(output_file_path, 'w') as output_file:
            file_ext = args.output_file_path.split('.')[-1]

            if file_ext == 'h' or file_ext == 'hpp' or file_ext == 'hxx':
                output_str = 'unsigned char ' + args.variable_name + '[] = {'

                output_byte_counter = 0

                for xored_line in output_lines:
                    for xored_byte in xored_line:
                        output_str += hex(xored_byte)
                        output_str += ','
                        output_byte_counter += 1

                output_str += '};'
                output_str += '\n\n'
                output_str += 'size_t ' + args.variable_name + '_len = ' + \
                    str(output_byte_counter) + ';'
                output_str += '\n\n'
                output_file.write(output_str)

            elif file_ext == 'asm' or file_ext == 's':
                output_str = args.variable_name + ': db '

                output_byte_counter = 0

                for xored_line in output_lines:
                    for xored_byte in xored_line:
                        output_str += hex(xored_byte)
                        output_str += ','
                        output_byte_counter += 1

                output_str += '0'

                output_str += '\n'
                output_str += '.len equ $ - ' + args.variable_name + ' - 1\n'

                output_file.write(output_str)

        print('Transformed data written to', output_file_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.description = "Transforms the contents of a file, either to a C/C++ include, or to an asm include, or to a raw binary file, with or without XOR encryption\n\
        Pass a filename with extension .h/.hpp/.hxx to get a C/C++ include file\n\
        Pass a filename with extension .s/.asm to get a assembly include file."

    parser.epilog = "Happy XORing"

    parser.add_argument('-i', '--input-file-path',
                        required=True, help='Input file path to be transformed')
    parser.add_argument(
        '-ofp', '--output-file-path', required=True, help='Output path for the transformed data')

    mutex_group = parser.add_mutually_exclusive_group(required=True)
    mutex_group.add_argument('-vn', '--variable_name',
                             help='Name of the variable in the include file')
    mutex_group.add_argument(
        '-b', '--binary', action='store_true', help='Output the contents as raw binary')

    # sub commands
    subparsers = parser.add_subparsers(dest='sub_command', required=True)

    # XOR sub command
    xor_subparser = subparsers.add_parser('xor')
    xor_subparser.add_argument(
        '-k', '--key', required=True, help='Value to encrypt the data with')

    # Passthrough sub command
    passthrough_subparser = subparsers.add_parser('passthrough')

    args = parser.parse_args()

    main(args)
