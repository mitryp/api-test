import json
import os.path
import random
from itertools import islice
from typing import Optional, Iterable, List

import requests as r
from flask import Flask, request

from counter_api import api


app = Flask(__name__)
app.register_blueprint(api, url_prefix='/counter')

NUMBERS_FILENAME = 'real_nums.txt'

CURRENT_API_ID, CURRENT_API_HASH = [line.rstrip() for line in
                                    r.get('https://raw.githubusercontent.com/mitryp/api-test/main/current_keys'
                                          ).content.decode().split('\n')]


def shuffle_file(filename: str) -> Optional[str]:
    """
    Shuffles file and writes shuffled content into the file named
    '{filename_without_extension}_shuffled.{file_extension}'

    :param filename: str: a file name
    :return: str | None: new file name
    """
    with open(filename, 'r') as fr:
        if not os.path.exists(filename):
            return None

        name_parts = filename.split('.')
        new_filename = f'{".".join(name_parts[:-1])}_shuffled.{name_parts[-1]}'

        lines = fr.readlines()
        random.shuffle(lines)
        with open(new_filename, 'w') as fw:
            fw.writelines(lines)
    return new_filename


def get_new_number_iterator_from_shuffled_file(filename: str) -> Iterable:
    """
    Shuffles the file with path filename and returns iterator object for it.

    :param filename: file to be processed
    :return: iterator object
    """

    new_filename = shuffle_file(filename)
    return (n.rstrip().replace('+', '').replace(' ', '') for n in open(new_filename) if not n.startswith('#'))


NUMBERS = get_new_number_iterator_from_shuffled_file('real_nums.txt')


def get_numbers(count: int) -> List[str]:
    """
    Returns a list of numbers from the NUMBERS iterator with the length of count.
    If the iterator is over, shuffles the file with numbers (NUMBERS_FILENAME).

    :param count: int: the quantity of numbers requested
    :return: List[str]
    """
    global NUMBERS

    numbers = list(islice(NUMBERS, count))
    if len(numbers) != count:
        NUMBERS = get_new_number_iterator_from_shuffled_file(NUMBERS_FILENAME)
        numbers = list(islice(NUMBERS, count))

    return numbers


@app.route('/get-api')
def get_api():
    return {
        'id': CURRENT_API_ID,
        'hash': CURRENT_API_HASH
    }


@app.route('/get-next-phone-numbers')
def get_phone_numbers():
    count = request.args.get('count')

    return json.dumps(get_numbers(int(count) if count else 100))


if __name__ == '__main__':
    app.run()
