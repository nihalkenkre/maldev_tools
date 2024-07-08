import argparse


def xor(input_bytes, key):
    output_bytes = bytearray()

    k = 0
    for s in range(len(input_bytes)):
        if k == len(key):
            k = 0

        i = (input_bytes[s] ^ ord(key[k]))
        output_bytes.append(i)

        k += 1

    return output_bytes


def main(args):
    input_file_path = open(args.input_file_path, 'rb')
    input_data = input_file_path.read()
    input_file_path.close()

    # Reach the .text section
    # Get e_lfanew for the exe, point to NT Headers section
    e_lfanew = int.from_bytes(input_data[60:64], byteorder='little')

    # NT Header Signature = 4 bytes, NT Header File Header = 20 bytes
    nt_file_header = input_data[e_lfanew+4:e_lfanew+24]

    # Number of sections is [2:4] from the start of NTFileHeader
    section_count = int.from_bytes(nt_file_header[2:4], byteorder='little')

    # Size of Optional Header is [16:18] bytes from the start of NTFileHeader
    optional_header_size = int.from_bytes(
        nt_file_header[16:18], byteorder='little')

    text_raw_data_size = 0
    text_raw_data_ptr = 0

    # Section Headers follow NTHeader 40 bytes each
    for i in range(section_count):
        data_offset = e_lfanew + 24 + optional_header_size + (40 * i)
        section_header = input_data[data_offset:data_offset+40]
        section_name = section_header[0:8].decode('utf-8').rstrip('\x00')

        if '.data' in section_name or '.reloc' in section_name:
            print(
                'EXE has a .data/.reloc section, shellcode will not work. Aborting...')
            return

        if section_name == '.text':
            text_raw_data_size = int.from_bytes(
                section_header[16:20], byteorder='little')
            text_raw_data_ptr = int.from_bytes(
                section_header[20:24], byteorder='little')

    # Optional header follows NT File Header
    optional_header = input_data[e_lfanew +
                                 24:e_lfanew+24+optional_header_size]

    # Add a jmp instr at the start to jump to the entry point
    entry_point = int.from_bytes(
        optional_header[16:20], byteorder='little')
    base_of_code = int.from_bytes(
        optional_header[20:24], byteorder='little')

    jmp_offset = entry_point - base_of_code

    shellcode = bytearray([0xE9])
    shellcode += bytearray(jmp_offset.to_bytes(length=4, byteorder='little'))
    shellcode += bytearray(
        input_data[text_raw_data_ptr: text_raw_data_ptr + text_raw_data_size])

    # Should the data be XORed
    if args.sub_command == 'xor':
        xored_data = xor(shellcode, args.key)
        shellcode = xored_data

    # Write out the shellcode to file
    # Check if the output file is a C/ASM include
    file_ext = args.output_file_path.split('.')[-1]

    if file_ext == 'h' or file_ext == 'hpp' or file_ext == 'hxx':
        output_str = 'unsigned char ' + args.variable_name + '[] = {'

        output_byte_counter = 0

        for each in shellcode:
            output_str += hex(each)
            output_str += ','
            output_byte_counter += 1

        output_str += '};'
        output_str += '\n'
        output_str += 'size_t ' + args.variable_name + \
            '_len = ' + str(output_byte_counter) + ';'
        output_str += '\n'

        with open(args.output_file_path, 'w') as output_file:
            output_file.write(output_str)

    elif file_ext == 'asm' or file_ext == 's':
        output_str = args.variable_name + ': db '

        output_byte_counter = 0

        for each in shellcode:
            output_str += hex(each)
            output_str += ','
            output_byte_counter += 1

        output_str += '0'

        output_str += '\n'
        output_str += '.len equ $ - ' + args.variable_name + ' - 1\n'

        with open(args.output_file_path, 'w') as output_file:
            output_file.write(output_str)
    else:
        with open(args.output_file_path, 'wb') as output_file:
            output_file.write(shellcode)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Extracts the .text of the EXE file into shellcode, and optionally XORs it.', epilog='Happy Shelling')
    parser.add_argument('-i', '--input-file-path',
                        required=True, help='Path of the EXE file')
    parser.add_argument('-o', '--output-file-path', required=True,
                        help='Path of the shellcode file')
    parser.add_argument('-vn', '--variable-name',
                        help='Name of the variable in the include file. Required if the output file path is of C/ASM include')

    # Sub commands
    subparsers = parser.add_subparsers(dest='sub_command')

    # XOR sub command
    xor_subparser = subparsers.add_parser('xor')
    xor_subparser.add_argument(
        '-k', '--key', required=True, help='Value to XOR the data with')

    args = parser.parse_args()
    main(args)
