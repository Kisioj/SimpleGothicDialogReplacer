import argparse

from daedalus_sniffer import DaedalusSniffer
from src_helper import SrcHelper

from utils import is_valid_file


def main():
    parser = argparse.ArgumentParser(
        description='Extract data from Daedalus project',
    )

    parser.add_argument(
        'src_path',
        type=lambda src_path: is_valid_file(parser, src_path),
        help='path to .src file'
    )

    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='display parsing progress'
    )

    args = parser.parse_args()

    src_helper = SrcHelper(args.src_path)
    files_paths = src_helper.get_daedalus_files()
    data_sniffer = DaedalusSniffer()

    ignored_paths = (
        "/_intern/",
        "/AI/AI_Intern/",
        "/AI/Test_Skripts/",
        "/Story/Text.d",
        "/Story/U_LoadingScreen.d",
    )

    walked_paths = set()

    for i, file_path in enumerate(files_paths, start=1):
        if file_path in walked_paths:
            continue
        walked_paths.add(file_path)
        short_path = file_path.split('/Scripts/Content')[-1]
        if any(short_path.startswith(path) for path in ignored_paths):
            continue
        if args.verbose:
            print(f'\r{i}/{len(files_paths)} {file_path}')
        try:
            data_sniffer.sniff(file_path)
        except UnicodeDecodeError:
            print('UnicodeDecodeError')


if __name__ == '__main__':
    main()
