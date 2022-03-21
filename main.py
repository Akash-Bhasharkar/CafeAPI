from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from random import randint
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///cafes.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self) :
        return {column.name : getattr(self, column.name) for column in self.__table__.columns}
        


@app.route("/")
def home():
    return render_template("index.html")
    

@app.route("/random")
def random() :
    id = randint(1, 21)
    cafe = Cafe.query.get(id)
    return jsonify(cafe = cafe.to_dict() )

@app.route("/all")
def all() :
    all_cafes = Cafe.query.all()
    cafe_list = []
    for cafe in all_cafes :
        cafe_list.append(cafe.to_dict())
    return jsonify(cafes = cafe_list)

@app.route("/search")
def search():
    location = request.args.get("loc")
    cafe = db.session.query(Cafe).filter_by(location=location).first()
    if cafe:
       return jsonify(cafe = cafe.to_dict())
    else :
       return jsonify( error = {"Not found" : "Sorry"})


@app.route("/add", methods=["POST"])
def add():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price")
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


@app.route("/update-price/<cafe_id>", methods = ["PATCH"])
def update(cafe_id):
    new_coffee_price = request.args.get("new_price")
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
       cafe.coffee_price = new_coffee_price
       db.session.commit()
       return jsonify(success = {"success" : "Done"}), 200
    else :
       return jsonify( error = {"Not found" : "Sorry"}), 404

@app.route("/report-closed/<cafe_id>", methods = ["DELETE"])
def delete(cafe_id) :
    key = request.args.get("api-key")
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe and key == os.getenv("apikey"):
       db.session.delete(cafe)
       db.session.commit()
       return jsonify(success = {"success" : "Done"}), 200
    else :
       return jsonify( error = {"Not found" : "Sorry"}), 404



if __name__ == '__main__':
    app.run(debug=True)
