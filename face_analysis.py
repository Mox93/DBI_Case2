import numpy as np
import cv2
import face_recognition


class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def json(self):
        return dict(x=self.x, y=self.y)


class Line(object):
    def __init__(self, start, end):
        self.start = Point(start[0], start[1])
        self.end = Point(end[0], end[1])

    def json(self):
        return dict(start=self.start.json(), end=self.end.json())


class Face(object):
    def __init__(self, top, bottom, left, right, name="Unknown", exp="Unknown"):
        self.top = Line((top, left), (top, right))
        self.bottom = Line((bottom, left), (bottom, right))
        self.left = Line((top, left), (bottom, left))
        self.right = Line((top, right), (bottom, right))
        self.name = name
        self.exp = exp

    def json(self):
        return dict(top=self.top.json(), bottom=self.bottom.json(),
                    left=self.left.json(), right=self.right.json(),
                    name=self.name, exp=self.exp)


def find_faces(img, i):
    nparr = np.frombuffer(img, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    print(frame.shape)

    x, y, z = frame.shape
    x, y = max(x, y), min(x, y)

    scale = max(int(x/160), int(y/120))

    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=1/scale, fy=1/scale)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    face_names = []
    faces = []

    for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)
        # matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        # Or instead, use the known face with the smallest distance to the new face
        # face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        # best_match_index = np.argmin(face_distances)
        # if matches[best_match_index]:
        #     name = known_face_names[best_match_index]

        face_names.append(name)

        for (top, right, bottom, left), name in zip(face_locations, face_names):
            top *= scale
            right *= scale
            bottom *= scale
            left *= scale

            print((top, bottom, left, right))
            faces.append(Face(top, bottom, left, right, name, "happy as fuck"))

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display the resulting image
        # cv2.imshow('Image', cv2.resize(frame, (0, 0), fx=0.25, fy=0.25))
        cv2.imwrite(f"/home/mohamed/Projects/DBI_Case2/img/test{i}.jpg", frame)

    return faces

