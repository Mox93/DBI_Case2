import numpy as np
import cv2
import face_recognition
from datetime import datetime
from db import Identifier, Line, Point, Size, Individual
from bson.binary import Binary
import pickle


# class Point(object):
#     def __init__(self, x, y):
#         self.x = x
#         self.y = y
#
#     def json(self):
#         return dict(x=self.x, y=self.y)
#
#
# class Line(object):
#     def __init__(self, start, end):
#         self.start = Point(start[0], start[1])
#         self.end = Point(end[0], end[1])
#
#     def json(self):
#         return dict(start=self.start.json(), end=self.end.json())
#
#
# class Size(object):
#     def __init__(self, width, height):
#         self.width = width
#         self.height = height
#
#     def json(self):
#         return dict(width=self.width, height=self.height)
#
#
# class Face(object):
#     def __init__(self, top, bottom, left, right, width, height, name="Unknown", exp="Unknown"):
#         self.top = Line((top, left), (top, right))
#         self.bottom = Line((bottom, left), (bottom, right))
#         self.left = Line((top, left), (bottom, left))
#         self.right = Line((top, right), (bottom, right))
#         self.name = name
#         self.exp = exp
#         self.size = Size(width, height)
#
#     def json(self):
#         return dict(top=self.top.json(), bottom=self.bottom.json(),
#                     left=self.left.json(), right=self.right.json(),
#                     name=self.name, exp=self.exp)  # , size=self.size.json())


def find_faces(img):

    img_bytes = img.file.read()
    nparr = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    img.size = Size(frame.shape[1], frame.shape[0])
    # print(img.size.width, img.size.height)

    x, y, z = frame.shape
    x, y = max(x, y), min(x, y)
    scale = int(max(x/640, y/480))

    small_frame = cv2.resize(frame, (0, 0), fx=1/scale, fy=1/scale)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Find all the faces and face encodings in the image
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    # print(f"{face_locations=}")

    face_ids = []
    faces = []

    individuals = Individual.objects().all()
    known_face_encodings = []
    known_face_ids = []

    for person in individuals:
        known_face_encodings.append(pickle.loads(person.encoder))
        known_face_ids.append(person.id)

    i = 0

    for face_encoding in face_encodings:
        new_person = False
        if known_face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)

            if matches[best_match_index]:
                _id = known_face_ids[best_match_index]
                old_face = Individual.objects(id=_id).first()
                if old_face:
                    old_face.ref_img.append(img)
                    old_face.save()
                    print("Old Face")
            else:
                new_person = True

        else:
            new_person = True

        if new_person:
            i += 1
            name = "Unknown"  # f"Person-{i}"
            new_face = Individual(name, Binary(pickle.dumps(face_encoding, protocol=2), subtype=128), [img])
            print("New Face")
            new_face.save()
            _id = new_face.id

        face_ids.append(_id)

    for (top, right, bottom, left), _id in zip(face_locations, face_ids):
        top *= scale
        right *= scale
        bottom *= scale
        left *= scale

        top_line = Line(Point(left, top), Point(right, top))
        bottom_line = Line(Point(left, bottom), Point(right, bottom))
        left_line = Line(Point(left, top), Point(left, bottom))
        right_line = Line(Point(right, top), Point(right, bottom))

        faces.append(Identifier(top_line, bottom_line, left_line, right_line, _id, exp="happy"))

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 10*scale), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        person = Individual.objects(id=_id).first()
        name = person.name if person else "Unknown"
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Save the resulting image
    cv2.imwrite(f"/home/mohamed/Projects/DBI_Case2/img/test-{datetime.now()}.jpg", frame)

    return faces

