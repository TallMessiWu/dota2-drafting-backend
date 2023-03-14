import pickle
import random

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


class Randomize(Resource):
    def get(self):
        regions = [1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 25, 37, 38]
        patches = [47, 48, 49, 50, 51]
        first_pick_team = [0, 1]
        heroes_info = [102, 73, 68, 1, 113, 2, 3, 65, 38, 4, 62, 78, 99, 61, 96, 81, 66, 56, 51, 5, 55, 119, 135, 50,
                       43, 87, 69,
                       49, 6, 107, 7, 103, 106, 58, 33, 41, 121, 72, 123, 59, 74, 91, 64, 8, 90, 23, 104, 52, 31, 54,
                       25, 26, 80,
                       48, 77, 97, 136, 129, 94, 82, 9, 114, 10, 89, 53, 36, 60, 88, 84, 57, 111, 76, 120, 44, 12, 110,
                       137, 13,
                       14, 45, 39, 15, 32, 86, 16, 79, 11, 27, 75, 101, 28, 93, 128, 35, 67, 71, 17, 18, 105, 46, 109,
                       29, 98, 34,
                       19, 83, 95, 100, 108, 85, 70, 20, 40, 47, 92, 126, 37, 63, 21, 112, 30, 42, 22]
        return [random.choice(regions), random.choice(patches), random.choice(first_pick_team),
                random.sample(heroes_info, k=24)]


class Hero(Resource):
    def get(self, region, patch, first_pick_team, selected_heroes):
        selected_heroes = [int(i.strip()) for i in selected_heroes.split(",")]
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
        return [int(rf.predict(table)[0]), "{}%".format(round(rf.predict_proba(table).max() * 100, 2))]


api.add_resource(HeroPicture, "/hero/<int:hero_id>")
api.add_resource(Randomize, "/randomize")
api.add_resource(Hero, "/hero/<int:region>/<int:patch>/<int:first_pick_team>/<selected_heroes>")
