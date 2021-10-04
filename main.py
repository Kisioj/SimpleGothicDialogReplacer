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
        "/_INTERN/",
        "/AI/AI_INTERN/",
        "/AI/TEST_SKRIPTS/",
        "/STORY/TEXT.D",
        "/STORY/U_LOADINGSCREEN.D",
        "/STORY/B_STORY/B_LOGENTRY.D",
        "/STORY/B_STORY/DK/B_DIALOG_FUNCTIONS.D",
        "/STORY/B_STORY/B_TEACHATTRIBUTEPOINTS.D",
        "/STORY/B_STORY/B_TEACHFIGHTTALENTPERCENT.D",
        "/STORY/B_STORY/B_TEACHTHIEFTALENT.D",
    )

    walked_paths = set()

    file_2_texts = []

    for i, file_path in enumerate(files_paths, start=1):
        if file_path in walked_paths:
            continue
        walked_paths.add(file_path)
        short_path = file_path.upper().replace('\\', '/').split('/SCRIPTS/CONTENT')[-1]
        if any(short_path.startswith(path) for path in ignored_paths):
            continue

        if args.verbose:
            print(f'\r{i}/{len(files_paths)} {file_path}')

        try:
            texts = data_sniffer.sniff(file_path)
        except UnicodeDecodeError:
            texts = []
            print('UnicodeDecodeError')

        file_2_texts.append((short_path, texts))

    # print('\n'*10)  # TODO comment this and below
    # file_2_texts.sort(key=lambda row: len(row[1]))
    # for short_path, texts in file_2_texts:
    #     if len(texts) == 0:
    #         continue
    #     print(len(texts), short_path)
    #     for line in texts:
    #         print(line)
    #     print('\n')


if __name__ == '__main__':
    main()
