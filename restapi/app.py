from flask import Flask
from apis import blueprint as api


app = Flask(__name__)
# Avoid error 301 when missing trailing slash.
app.url_map.strict_slashes = False

app.register_blueprint(api)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
