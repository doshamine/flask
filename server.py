from flask import Flask, jsonify, request, Response
from flask.views import MethodView
from models import Advertisement, Session, User
from auth import check_password
from flask_login import LoginManager, login_user, login_required, current_user
from sqlalchemy import select
import secrets
app = Flask("app")
app.config['SECRET_KEY'] = secrets.token_hex(16)

@app.before_request
def before_request():
    session = Session()
    request.session = session

@app.after_request
def after_request(response: Response):
    request.session.close()
    return response

login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    session = Session()
    return session.execute(select(User).filter_by(id=int(user_id))).scalars().first()

@app.route('/api/v1/login/', methods=['POST'])
def login():
    session = Session()
    user = session.execute(select(User).filter_by(email=request.json["email"])).scalars().first()

    if user and check_password(request.json["password"], user.password):
        login_user(user)
        return jsonify({"message": "Logged in successfully"}), 200
    return jsonify({"error": "Invalid credentials"}), 401


def get_advertisement_by_id(adv_id: int):
    advertisement = request.session.get(Advertisement, adv_id)
    return advertisement

def add_advertisement(advertisement: Advertisement):
    request.session.add(advertisement)
    request.session.commit()

def delete_advertisement(advertisement: Advertisement):
    request.session.delete(advertisement)
    request.session.commit()

class AdvertisementView(MethodView):

    def get(self, adv_id: int):
        advertisement = get_advertisement_by_id(adv_id)
        return jsonify(advertisement.dict), 200

    @login_required
    def post(self):
        json_data = request.json
        advertisement = Advertisement(
            header=json_data["header"], description=json_data["description"],
            user_id=current_user.get_id()
        )
        add_advertisement(advertisement)
        return jsonify(advertisement.id_dict), 201

    @login_required
    def patch(self, adv_id: int):
        json_data = request.json
        advertisement = get_advertisement_by_id(adv_id)
        if int(current_user.get_id()) == advertisement.user_id:
            if "header" in json_data:
                advertisement.header = json_data["header"]
            if "description" in json_data:
                advertisement.description = json_data["description"]

            add_advertisement(advertisement)
            return jsonify(advertisement.id_dict), 201
        return jsonify({"status": "no permission"}), 403

    @login_required
    def delete(self, adv_id: int):
        advertisement = get_advertisement_by_id(adv_id)
        if int(current_user.get_id()) == advertisement.user_id:
            delete_advertisement(advertisement)
            return jsonify({"status": "success"}), 204
        return jsonify({"status": "no permission"}), 403

advertisement_view = AdvertisementView.as_view("advertisement_view")
app.add_url_rule("/api/v1/advertisement/", view_func=advertisement_view, methods=["POST"])
app.add_url_rule("/api/v1/advertisement/<int:adv_id>", view_func=advertisement_view, methods=["GET", "PATCH", "DELETE"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)