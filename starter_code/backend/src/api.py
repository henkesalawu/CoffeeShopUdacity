import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
# GET request for all available drinks
@app.route("/drinks", methods=['GET'])
def get_drinks():
    try:
        drinks = Drink.query.all()

        if len(drinks) == 0:
            abort(400)

        return jsonify({
            "success": True,
            "drinks": [drink.short() for drink in drinks]
        }), 200
    
    except Exception as e:
        print(e)
        abort(422)

# GET request for drinks details
@app.route("/drinks-detail", methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    try:
        drinks = Drink.query.all()

        if len(drinks) == 0:
            abort(400)

        return jsonify({
            "success": True,
            "drinks": [drink.long() for drink in drinks]
        }), 200
    
    except Exception as e:
        print(e)
        abort(422)

# POST request to add drink
@app.route("/drinks", methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):
    body = request.get_json()
    new_title = body.get('drink', None)
    new_recipe = body.get('recipe', None)

    try:        
        if not new_title:
            abort(422)
        if not new_recipe:
            abort(422)
        
        drink = Drink(
            title=new_title,
            recipe=json.dumps(new_recipe)
            )
        drink.insert()
            
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200
    except Exception as e:
        print(e)
        abort(404)

# PATCH request to update specific drink
@app.route("/drinks/<int:drink_id>", methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(payload, drink_id):
    body = request.get_json()

    try:
        drink_to_update = Drink.query.get(drink_id)

        if drink_to_update is None:
            abort(404)

        new_title = body.get('title')
        new_recipe = body.get('recipe')

        if new_title:
            drink_to_update.title = new_title
        if new_recipe:
            drink_to_update.recipe = json.dumps(new_recipe)
        
        drink_to_update.update()

        updated_drink = Drink.query.get(drink_id)
        return jsonify({
            "success": True,
            "drinks": [updated_drink.long()]
            }), 200
    
    except Exception as e:
        print(e)
        abort(422)

# DELETE request to delete specific drink
@app.route("/drinks/<int:drink_id>", methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
   
    try:
        drink_to_delete = Drink.query.get(drink_id)

        if drink_to_delete is None:
            abort(404)

        drink_to_delete.delete()
        
        return jsonify({
            "success": True,
            "delete": drink_id
            }), 200
    
    except Exception as e:
        print(e)
        abort(422)



# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource Not Found"
    }), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
    }), 500

@app.errorhandler(AuthError)
def authorization_error(error):
    return jsonify({
        "success": False,
        "status_code": error.status_code,
        "error": error.error['description']
    }), error.status_code

@app.errorhandler(405)
def not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Not Allowed"
    }), 405
