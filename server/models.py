from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # add relationship
    restaurant_pizzas = db.relationship("restaurant_pizzas", back_populates="pizza", cascade="all, delete-orphan")
    pizzas = association_proxy("restaurant_pizzas", "pizza")
    # add serialization rules
    serialize_rules = ("-restaurantpizzas", "-pizzas")
    def __repr__(self):
        return f"<Restaurant {self.name}>"


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # add relationship
    #!establish bidirectional relationship with RP table + prevent parent deletion errors for orphans
    #*Resturant needs access to its related pizza objs through RP
    restaurant_pizzas = db.relationship("restaurant_pizzas", back_populates="restaurant", cascade="all, delete-orphan")
    #!shortcut to access related Restaurant objects directly through the RestaurantPizza table
    restaurants = association_proxy("restaurant_pizzas", "resturant")
    # add serialization rules
    #!ALWAYS exclude relationships, circular reference
    #? could also just take off dot notation?
    serealize_rules = ("-restaurantpizzas", "-resturants")
    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    #!establish join table by foreignkeys
    pizza_id = db.Column(db.Integer, db.ForeignKey("pizzas.id"))
    restaurant_id  = db.Column(db.Integer, db.ForeignKey("restaurants.id"))
    # add relationships
    restaurant = db.relationship("Restaurant", back_populates = "RestaurantPizza")
    pizza = db.relationship("Pizza", back_populates="RestaurantPizza")
    # add serialization rules
    serialize_rules = ("-restaurant", "-pizza")
    # add validation
    @validates("price")
    def validate_price(self, key, value):
        if not(1 <= value <= 30):
            raise ValueError("Price needs t obe between 1 and 30!")
        return value
    

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
