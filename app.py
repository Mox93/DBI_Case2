import flask
import werkzeug
from face_analysis import find_faces, Face


app = flask.Flask(__name__)

counter = 0


@app.route('/api/img', methods=['GET', 'POST'])
def img():
    global counter
    imagefile = flask.request.files['image']
    counter += 1
    print(f"\n{counter}-Received image File name : {imagefile.filename}")

    img = imagefile.read()

    faces = find_faces(img, counter)

    # f1 = Face(**{"loc": (100, 100), "size": (100, 100), "name": "BlaBla", "exp": "WTF!"})
    # f2 = Face(**{"loc": (300, 300), "size": (300, 300), "name": "Someone", "exp": "Haha!"})

    return flask.jsonify(faces=[face.json() for face in faces])

    # return flask.jsonify(img=str(base64.b64encode(img)))


app.run(host="192.168.0.107", port=5000, debug=True)
