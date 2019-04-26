import pprint
import pymongo

class DbConnection():

    client = None
    collectionLists = []

    def __init__(self):
        self.client = pymongo.MongoClient();

    def closeConnection(self):
        client.close();

    def insertData(self, data, collectionname):
        collectionname.insert_one(data)

    def printData(self, collectionname, count = 10):
        for item in collectionname.find().limit(count):
            print(item)

    @classmethod
    def getAllCollectionName(self, db):
        return db.collection_names(include_system_collections=False)

    @classmethod
    def dropCollection(self, db, collectionname):
        db.collectionname.drop()

    def createCollection(db, collectionname):
        # basically db is 'DbConnection.client.netSus'
        name = db.collectionname
        collectionLists.append(name)
        return name