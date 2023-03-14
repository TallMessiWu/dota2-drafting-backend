import pickle
from ast import literal_eval

from flask import Blueprint, send_file
from flask_restful import Api, Resource
import os
from config import SITE_ROOT
import pandas as pd


hero_bp = Blueprint("hero", __name__)
api = Api(hero_bp)


class HeroPicture(Resource):
    def get(self, hero_id):
        return send_file(os.path.join(SITE_ROOT, "assets/heroes-avatars", "{}.jpg".format(hero_id)))


class Hero(Resource):
    def get(self, region, patch, first_pick_team, selected_heroes):
        print(selected_heroes)
        selected_heroes = [int(i.strip()) for i in selected_heroes.split(",")]
        print(selected_heroes)

        heroes_stats = pd.read_csv(os.path.join(SITE_ROOT, "data/processed_data/heroes_stats.csv"), index_col=0)
        with open(os.path.join(SITE_ROOT, "models/random_forest.sav"), "rb") as f:
            rf = pickle.load(f)

        table = {
            "region": region,
            "patch": patch,
            "first_pick_team": first_pick_team,
        }
        table = pd.DataFrame.from_dict(table, orient="index").T
        for i in range(24):
            hero_stat = heroes_stats.query("id == {}".format(selected_heroes[i])).drop("localized_name",
                                                                                       axis=1).add_prefix(
                "selection_{}_".format(i)).reset_index(drop=True)
            table = pd.concat([table, hero_stat], axis=1)
        return int(rf.predict(table)[0])


api.add_resource(HeroPicture, "/hero/<int:hero_id>")
api.add_resource(Hero, "/hero/<int:region>/<int:patch>/<int:first_pick_team>/<selected_heroes>")
