from bottle import Bottle, request, response
import json
from datetime import datetime, timedelta
import gzip
import os

from .database import Check, init_database

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Bottle()
init_database()


def parse_time_interval(val):
    assert val.startswith('m')
    assert val[1:].isdigit()
    return timedelta(minutes=int(val[1:]))


@app.route('/')
def page_home():
    return open(os.path.join(BASE_DIR, 'data/web.html')).read()


@app.route('/api/check/find')
def check_find():
    ago = parse_time_interval(request.query.getunicode('ago'))
    exclude = request.query.getunicode('exclude', '').split(',')
    brief = request.query.getunicode('brief') == '1'
    now = datetime.utcnow()
    qs = Check.select().where((Check.created >= (now - ago)) &
                              (Check.created < now) &
                              (~Check.id.in_(exclude)))
    res = []
    for check in qs:
        item = {}
        for key in ('count_ok', 'count_fail', 'count_connect_fail',
                    'count_read_fail', 'count_data_fail',
                    'avg_read_time', 'avg_connect_time',
                    'session_time', 'name'):
            item[key] = getattr(check, key)
        item['id'] = str(check.id)
        item['created'] = check.created.isoformat()
        if not brief:
            item['ops'] = json.loads(gzip.decompress(check.ops).decode('utf-8'))
        res.append(item)
    response.headers['content-type'] = 'text/json'
    return json.dumps({'result': res})


def debug_server():
    app.run(host='localhost', port=9000, debug=True, reloader=True)


if __name__ == '__main__':
    debug_server()
