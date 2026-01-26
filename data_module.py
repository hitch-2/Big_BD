from pymongo import MongoClient
import pandas as pd
import pickle
import os

CACHE_PATH = "cache/data_cache.pkl"


class DataManager:
    def __init__(self, mongo_uri, db_name, collection_name):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def load_from_db(self):
        data = list(self.collection.find({}, {"_id": 0}))
        return pd.DataFrame(data)

    def save_to_cache(self, df):
        os.makedirs("cache", exist_ok=True)
        with open(CACHE_PATH, "wb") as f:
            pickle.dump(df, f)

    def load_from_cache(self):
        if not os.path.exists(CACHE_PATH):
            return None
        with open(CACHE_PATH, "rb") as f:
            return pickle.load(f)

    def get_data(self, use_cache=True):
        if use_cache:
            cached = self.load_from_cache()
            if cached is not None:
                return cached

        df = self.load_from_db()
        self.save_to_cache(df)
        return df
