from bottle import Bottle, request, response
import json
from datetime import datetime, timedelta

from database import Check, init_database

app = Bottle()
init_database()


def parse_time_interval(val):
    assert val.startswith('m')
    assert val[1:].isdigit()
    return timedelta(minutes=int(val[1:]))


@app.route('/api/check/find')
def check_find():
    #date_from = request.query.getunicode('date_from')
    #date_to = request.query.getunicode('date_to')
    ago = parse_time_interval(request.query.getunicode('ago'))
    now = datetime.utcnow()
    qs = Check.select().where((Check.created >= (now - ago)) &
                             (Check.created < now))
    res = []
    for check in qs:
        item = {}
        for key in ('count_ok', 'count_fail', 'count_connect_fail',
                    'count_read_fail', 'count_data_fail'):
            item[key] = getattr(check, key)
        item['id'] = str(check.id)
        item['created'] = check.created.isoformat()
        item['ops'] = json.loads(check.ops)
        res.append(item)
    response.headers['content-type'] = 'text/json'
    return json.dumps({'result': res})


if __name__ == '__main__':
    app.run(host='localhost', port=9000, debug=True, reloader=True)
