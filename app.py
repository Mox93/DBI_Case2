import flask
from face_analysis import find_faces
from db import db, DB_NAME, PORT, HOST, Image, Individual
import base64


app = flask.Flask(__name__)

app.config["MONGODB_DB"] = DB_NAME
app.config["MONGODB_PORT"] = PORT
app.config["MONGODB_HOST"] = HOST

db.init_app(app)

counter = 0


@app.route('/api/img', methods=["GET", "POST"])
def img_analise():
    global counter
    counter += 1

    image_file = flask.request.files['image']
    print(f"\n{counter}-Received image File name : {image_file.filename}")

    img_bytes = image_file.read()

    img = Image()
    img.file.new_file()
    img.file.write(img_bytes)
    img.file.close()
    img.save()
    img.recognized = find_faces(img)
    img.save()

    return flask.jsonify(data=img.json())
    # return flask.jsonify(faces=[face.json() for face in img.recognized])
    # return flask.jsonify(img=str(base64.b64encode(img)))


@app.route("/api/img/<string:_id>", methods=["GET", "POST"])
def image(_id):
    try:
        img = Image.objects(id=_id).first()

        if img:
            if flask.request.method == "POST":
                return flask.jsonify(data=img.json())

            return flask.jsonify(data=img.json(), bitmap=str(base64.b64encode(img.file.read())))

    except Exception as e:
        return flask.jsonify(msg=str(e))


@app.route("/api/individual/<string:_id>", methods=["GET", "POST"])
def individual(_id):
    try:
        person = Individual.objects(id=_id).first()

        if person:
            if flask.request.method == "POST":
                data = flask.request.get_json()
                print(f"The Data I've got is {data} and its Type is {type(data)}")
                person.name = data.get("name")
                person.save()

            return flask.jsonify(data=person.json(count=False))

    except Exception as e:
        return flask.jsonify(msg=str(e))


app.run(host="192.168.0.109", port=5000, debug=True)

