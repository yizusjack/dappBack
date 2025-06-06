from flask import Flask, jsonify, request
import jwt
import datetime
import os

from scipy.constants import value

from config import config
from models import db
from dotenv import load_dotenv
from sqlalchemy import create_engine
from seeder import userSeed
from models import User
import hashlib
from daltonize import imageTransform
from naive import getResult
import json

load_dotenv()

#Gets a hashed password from the given entry
def getHashedPassword(password):
    hashedPsswd = hashlib.sha256()
    hashedPsswd.update(password.encode('utf8'))
    return hashedPsswd.hexdigest()

def create_app(enviroment):
    # Connect to server

    app = Flask(__name__)

    app.config.from_object(enviroment)

    with app.app_context():
        db.init_app(app)
        db.create_all()
        userSeed()

    return app

enviroment = config['development']
app = create_app(enviroment)

def token_required(f):
    def decorated(*args, **kwargs):
        token = request.headers.get('authorization')
        if not token:
            return jsonify({'error': 'No existe el token'}), 403
        if token.startswith('Bearer '):
            token = token[len('Bearer '):]
        try:
            jwt.decode(token, os.getenv('API_KEY'), algorithms="HS256")
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token no válido"}), 401
        return f(*args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated


@app.route('/get-token', methods=['POST'])
def get_token():
    auth = request.json['authorization']
    if auth and 'username' in auth and 'password' in auth:
        ##Genera un hash con la contraseña recibida
        hashedPsswd = getHashedPassword(auth['password'])
        ##Obtiene el usuario de la petición
        user = User.query.filter_by(username=auth['username']).first()
        ##Comprueba que las credenciales coincidan
        if user and hashedPsswd == user.password:
            token = jwt.encode({'user': auth['username'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, os.getenv('API_KEY'))
            response = {
                'message': 'Token generado con éxito',
                'token': token
            }
            return jsonify(response), 200
        ##Si las credenciales no coinciden
        response = {
            'message': 'Sus credenciales no coinciden con nuestros registros'
        }
        return jsonify(response), 403
    #Si la petición está incompleta retorna un error 422
    response = {
        'message': 'Datos incompletos. Favor de revisar su petición'
    }
    return jsonify(response), 422

@app.route('/receive-test', methods=['POST'])
@token_required
def get_ishihara():
    data = request.json
    data_str = data["respuestas"]
    data_list = json.loads(data_str)
    respuestas = [str(item["valor"]) for item in data_list]

    # print(data)
    # print(respuestas)

    prediction = getResult(respuestas)

    response = {
        'message': 'Éxito',
        'tipo_daltonismo': prediction
    }
    return jsonify(response), 200

@app.route('/transform-image', methods=['POST'])
@token_required
def transform_image():
    data = request.json

    imagenTransformada = imageTransform(data['imagen'], data['tipo_daltonismo'], data['simulacion'])

    if imagenTransformada == None:
        response = {
            'message': 'Imagen o tipo de daltonismo no válido',
        }
        return jsonify(response), 400

    response = {
        'message': 'Éxito',
        'imagenTransformada': imagenTransformada,
        'imagenOriginal': data['imagen']
    }
    return jsonify(response), 200


if __name__ == "__main__":
    app.run(debug=True)