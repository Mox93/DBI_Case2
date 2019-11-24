from flask_mongoengine import MongoEngine
from bson import ObjectId


db = MongoEngine()

# DB Configuration Values
DB_NAME = "dbi_case2"
PORT = 27017
HOST = "localhost"


class Point(db.EmbeddedDocument):
    x = db.IntField(required=True)
    y = db.IntField(required=True)


class Line(db.EmbeddedDocument):
    start = db.EmbeddedDocumentField(Point, required=True)
    end = db.EmbeddedDocumentField(Point, required=True)


class Size(db.EmbeddedDocument):
    width = db.IntField(required=True)
    height = db.IntField(required=True)

    def json(self):
        return dict(width=self.width, height=self.height)


class Identifier(db.EmbeddedDocument):
    top = db.EmbeddedDocumentField(Line, required=True)
    bottom = db.EmbeddedDocumentField(Line, required=True)
    left = db.EmbeddedDocumentField(Line, required=True)
    right = db.EmbeddedDocumentField(Line, required=True)
    individual = db.ObjectIdField()
    exp = db.StringField(required=True, defualt="Unknown")

    def json(self):
        result = self.to_mongo()
        individual = Individual.objects(id=str(self.individual)).first()
        if individual:
            result["individual"] = individual.json()

        return result


class Image(db.Document):
    meta = {"collection": "images"}

    file = db.FileField(required=True)
    size = db.EmbeddedDocumentField(Size)
    recognized = db.EmbeddedDocumentListField(Identifier)

    def json(self):
        Individual.index = 0
        result = self.to_mongo()
        result["_id"] = str(result["_id"])
        del result["file"]  # = str(result["file"])
        result["size"] = self.size.json()
        result["recognized"] = [identifier.json() for identifier in self.recognized]

        return result


class Individual(db.Document):
    meta = {"collection": "individuals"}

    name = db.StringField(required=True, default="Unknown")
    encoder = db.BinaryField(required=True)
    ref_img = db.ListField(db.ReferenceField(Image, required=True))

    index = 0

    def json(self, count=True):
        result = self.to_mongo()
        result["_id"] = str(result["_id"])

        if count and result["name"] == "Unknown":
            Individual.index += 1
            result["name"] = f"Person-{Individual.index}"

        del result["encoder"]
        result["ref_img"] = [str(ref) for ref in result["ref_img"]]

        return result

