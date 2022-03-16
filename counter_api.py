import os
import json

from flask import request, Blueprint

api = Blueprint('api', __name__)
API_STORAGE_PATH = os.path.join('reports.json')
COUNTER = dict()


def load_dict(dct: dict):
    try:
        for k, v in json.load(open(API_STORAGE_PATH, 'r', encoding='utf-8')).items():
            dct.update({
                k: v
            })
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        dct.clear()
    print('Load:', dct, sep='\n')


def dump_dict(dct: dict):
    print('Save:', dct, sep='\n')
    with open(API_STORAGE_PATH, 'w', encoding='utf-8') as f:
        json.dump(dct, f)


def format_number(number: str) -> str:
    return number.strip().replace('+', '')


def report_message(origin: str, number: str) -> None:
    load_dict(COUNTER)
    if origin not in COUNTER:
        COUNTER[origin] = dict()

    if number in COUNTER[origin]:
        COUNTER[origin][number] += 1
    else:
        COUNTER[origin][number] = 1

    dump_dict(COUNTER)


@api.route('/report', defaults={'origin': 'whatsapp'})
@api.route('/report/<origin>')
def report(origin):
    number = format_number(request.args['number'])
    if not number:
        return json.dumps(False)

    report_message(origin, number)
    return json.dumps(True)


@api.route('/count', defaults={'origin': 'whatsapp'})
@api.route('/count/<origin>')
def count(origin):
    load_dict(COUNTER)
    number = format_number(request.args['number'])
    if not number or origin not in COUNTER:
        return json.dumps(0)

    return json.dumps(COUNTER[origin][number] if number in COUNTER[origin] else 0)
