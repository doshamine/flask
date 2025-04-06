from flask import Flask, jsonify, request
from flask.views import MethodView
from models import Advertisement, Session

app = Flask("app")

class AdvertisementView(MethodView):
	def get(self, adv_id: int):
		with Session() as session:
			advertisement = session.get(Advertisement, adv_id)
		return jsonify(advertisement.dict)

	def post(self):
		json_data = request.json
		with Session() as session:
			advertisement = Advertisement(
				header=json_data["header"], description=json_data["description"],
				user_id=json_data["user_id"]
			)

			session.add(advertisement)
			session.commit()
			return jsonify(advertisement.id_dict)

	def patch(self, adv_id: int):
		json_data = request.json
		with Session() as session:
			advertisement = session.get(Advertisement, adv_id)

			if "header" in json_data:
				advertisement.header = json_data["header"]
			if "description" in json_data:
				advertisement.description = json_data["description"]

			session.add(advertisement)
			session.commit()
			return jsonify(advertisement.id_dict)

	def delete(self, adv_id: int):
		with Session() as session:
			advertisement = session.get(Advertisement, adv_id)
			session.delete(advertisement)
			session.commit()
		return jsonify({"status": "success"})


advertisement_view = AdvertisementView.as_view("advertisement_view")
app.add_url_rule("/api/v1/advertisement/", view_func=advertisement_view, methods=["POST"])
app.add_url_rule("/api/v1/advertisement/<int:adv_id>", view_func=advertisement_view, methods=["GET", "PATCH", "DELETE"])
app.run()