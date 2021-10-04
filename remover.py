from glob import glob
import sys
import os
import re

scripts_path = sys.argv[1]
ENCODING = 'windows-1250'

for i, filepath in enumerate(glob(os.path.join(scripts_path, '**/*.[dD]'), recursive=True)):
    try:
        with open(filepath, encoding=ENCODING) as file:
            content = file.read()
    except UnicodeDecodeError:
        print(i, filepath, 'UnicodeDecodeError')
        continue

    new_content = re.sub(r'"{{([^}]+)}}"', r'"\g<1>"', content)
    if content != new_content:
        with open(filepath, 'w', encoding=ENCODING) as file:
            file.write(new_content)

    print(i, filepath)
