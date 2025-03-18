#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class Restaurants(Resource):
    #!get all res
    def get(self):
        try:
            restaurants = [restaurant.to_dict()
                           for restaurant in Restaurant.query.all()]
            return make_response(restaurants, 200)
        except Exception as e:
            return make_response({"error": str(e)}, 500)


api.add_resource(Restaurants, "/restaurants")



class RestaurantById(Resource):
    #* get restaurant by ID
    def get(self, id):
        try:
            restaurant = db.session.get(Restaurant, id)
            if not restaurant:
                return make_response({"error": "Restaurant not found"}, 404)
            return make_response(restaurant.to_dict(rules=("restaurant_pizzas",)), 200)
        except Exception as e:
            return make_response({"error": "An internal error occurred"}, 500)

    #! delete restaurant by ID
    def delete(self, id):
        try:
            restaurant = db.session.get(Restaurant, id)
            if not restaurant:
                return make_response({"error": "Restaurant not found"}, 404)
            
            #! del all records associated with with rest_id, filter by the match and del them
            RestaurantPizza.query.filter_by(restaurant_id=id).delete()
            db.session.delete(restaurant)
            db.session.commit()
            #! remember return only the status code
            return make_response("", 204)
        except Exception as e:
            return make_response({"error": str(e)}, 500)

api.add_resource(RestaurantById, "/restaurants/<int:id>")

class Pizzas(Resource):
    def get(self):
        try:
            pizzas = [pizza.to_dict(rules = ("-restaurant_pizzas", "-pizzas",))
                           for pizza in Pizza.query.all()]
            return make_response(pizzas, 200)
        except Exception as e:
                return make_response({"error": str(e)}, 500)

class RestaurantPizzas(Resource):
    def post(self):
        try:
            data = request.get_json()

            price = data.get("price")
            pizza_id = data.get("pizza_id")
            restaurant_id = data.get("restaurant_id")

            
            if not price or not pizza_id or not restaurant_id:
                return make_response({"errors": ["validation errors"]}, 400)
            # if not (1 <= price <= 30):
                # return make_response({"errors": ["validation errors"]}, 400)
            
            restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
            db.session.add(restaurant_pizza)
            db.session.commit()

            response_data = restaurant_pizza.to_dict(rules=("restaurant", "pizza",))
            return make_response(response_data, 201)
        except Exception as e:
            return make_response({"errors": ["validation errors"]}, 400)
        
api.add_resource(Pizzas, "/pizzas")
api.add_resource(RestaurantPizzas, "/restaurant_pizzas")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
