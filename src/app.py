from flask import Flask

from config import config
from routes import Ad

app = Flask(__name__)


def page_not_found(error):
    return '<h1>Page not found!😖</h1>', 404


if __name__ == '__main__':
    app.config.from_object(config['development'])

    # Blueprints
    app.register_blueprint(Ad.main, url_prefix='/api/ads')

    # Error handles
    app.register_error_handler(404, page_not_found)
    app.run()
