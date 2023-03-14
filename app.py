from flask import Flask, send_file
from blueprints.hero_bp import hero_bp
import os
import config
from config import SITE_ROOT
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(config)

app.register_blueprint(hero_bp)
CORS(app)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/radiant-dire/<int:side>')
def radiant_dire(side):
    return send_file(
        os.path.join(SITE_ROOT, "assets/radiant-dire", "{}.jpg".format(side))
    )


if __name__ == '__main__':
    app.run(port=667)
