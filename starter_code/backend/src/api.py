import json
from flask import Flask, request, jsonify, abort
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

with app.app_context():
    db_drop_and_create_all()

# ROUTES
# GET request for all available drinks / short description
@app.route("/drinks", methods=['GET'])
def get_drinks():
    """
    Get list of available drinks
    """
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
    """
    Get details of the drink
    """
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
    """
    Create new drink
    """
    body = request.get_json()
    new_title = body.get('title')
    new_recipe = body.get('recipe')
    new_recipe = json.dumps(new_recipe)
    try:
        if not new_title:
            abort(422)
            print('title missing')
        if not new_recipe:
            abort(422)

        drink = Drink(
            title=new_title,
            recipe=new_recipe
            )
        drink.insert()
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        })
    except Exception as e:
        print(e)
        abort(422)

# PATCH request to update specific drink
@app.route("/drinks/<int:drink_id>", methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(payload, drink_id):
    """
    Update existing drink
    """
    body = request.get_json()

    try:
        drink_to_update = Drink.query.get(drink_id)

        if drink_to_update is None:
            abort(404)

        new_title = body.get('title', None)
        new_recipe = body.get('recipe', None)

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
    """
    Delete selected drink
    """
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

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Cannot process the request."
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

@app.errorhandler(401)
def notauthorized(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'Not authorized'
    }), 401
