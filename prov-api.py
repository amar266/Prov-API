#!flask/bin/python
import six
from flask import Flask, jsonify, abort, request, make_response, url_for
from flask.ext.httpauth import HTTPBasicAuth

app = Flask(__name__, static_url_path="")
auth = HTTPBasicAuth()


@auth.get_password
def get_password(username):
    if username == 'prov':
        return 'prov'
    return None


@auth.error_handler
def unauthorized():
    # return 403 instead of 401 to prevent browsers from displaying the default
    # auth dialog
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


vms = [
    {
        'id': 1,
        'title': u'Ubuntu',
        'description': u'Server on AWS',
        'done': True
    },
    {
        'id': 2,
        'title': u'CentOS',
        'description': u'Server on AWS',
        'done': False
    }
]


def make_public_task(task):
    new_task = {}
    for field in task:
        if field == 'id':
            new_task['uri'] = url_for('get_task', task_id=task['id'],
                                      _external=True)
        else:
            new_task[field] = task[field]
    return new_task


@app.route('/prov-api/v1.0/vms', methods=['GET'])
@auth.login_required
def get_vms():
    return jsonify({'vms': [make_public_task(task) for task in vms]})


@app.route('/prov-api/v1.0/vms/<int:task_id>', methods=['GET'])
@auth.login_required
def get_task(task_id):
    task = [task for task in vms if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    return jsonify({'task': make_public_task(task[0])})


@app.route('/prov-api/v1.0/vms', methods=['POST'])
@auth.login_required
def create_task():
    if not request.json or 'title' not in request.json:
        abort(400)
    task = {
        'id': vms[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }
    vms.append(task)
    return jsonify({'task': make_public_task(task)}), 201


@app.route('/prov-api/v1.0/vms/<int:task_id>', methods=['PUT'])
@auth.login_required
def update_task(task_id):
    task = [task for task in vms if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json and \
            not isinstance(request.json['title'], six.string_types):
        abort(400)
    if 'description' in request.json and \
            not isinstance(request.json['description'], six.string_types):
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    task[0]['title'] = request.json.get('title', task[0]['title'])
    task[0]['description'] = request.json.get('description',
                                              task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])
    return jsonify({'task': make_public_task(task[0])})


@app.route('/prov-api/v1.0/vms/<int:task_id>', methods=['DELETE'])
@auth.login_required
def delete_task(task_id):
    task = [task for task in vms if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    vms.remove(task[0])
    return jsonify({'result': True})


if __name__ == '__main__':
    app.run(debug=True)

