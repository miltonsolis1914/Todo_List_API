"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User,TODOLis
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/get_todolist', methods=['GET'])
def get_TODO():

    query = TODOLis.query.all()

    # map the results and your list of people  inside of the all_people variable
    results = list(map(lambda x: x.serialize(), query))
    
    return jsonify(results), 200
# this only runs if `$ python src/main.py` is executed
@app.route('/add_todolist', methods=['POST'])
def add_tod():

    # recibir info del request
    request_body = request.get_json()
    print(request_body)


    tod = TODOLis(done=request_body["done"],label=request_body["label"])
    db.session.add(tod)
    db.session.commit()

    return jsonify("All good"), 200

@app.route('/del_todolist/<int:position>', methods=['DELETE'])
def del_tod(position):

    # recibir info del request
    
    tod = TODOLis.query.get(position)
    if tod is None:
        raise APIException('TodoList not found', status_code=404)

    db.session.delete(tod)

    db.session.commit()

    return jsonify("All good"), 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
