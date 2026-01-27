from pymongo import MongoClient
import pandas as pd
import pickle
import os
import time

CACHE_PATH = "cache/data_cache.pkl"
CACHE_TTL_SECONDS = 300  # 5 минут, МЕНЯЕТЕ ЗДЕСЬ


class DataManager:
    def __init__(self, mongo_uri, db_name, collection_name):
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.collection_name = collection_name

    def _connect(self):
        client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=3000)
        db = client[self.db_name]
        return db[self.collection_name]

    def load_from_db(self):
        collection = self._connect()
        data = list(collection.find({}, {"_id": 0}))
        return pd.DataFrame(data)

    def save_to_cache(self, df):
        os.makedirs("cache", exist_ok=True)
        payload = {
            "timestamp": time.time(),
            "data": df
        }
        with open(CACHE_PATH, "wb") as f:
            pickle.dump(payload, f)

    def load_from_cache(self):
        if not os.path.exists(CACHE_PATH):
            return None, None

        with open(CACHE_PATH, "rb") as f:
            payload = pickle.load(f)

        return payload["data"], payload["timestamp"]

    def get_data(self):
        cached_df, cached_time = self.load_from_cache()

        # если кэша нет вообще
        if cached_df is None:
            try:
                df = self.load_from_db()
                self.save_to_cache(df)
                return df
            except Exception:
                raise RuntimeError("Нет доступа к БД и отсутствует кэш")

        # если кэш есть — проверяем TTL
        cache_age = time.time() - cached_time
        if cache_age < CACHE_TTL_SECONDS:
            return cached_df

        # кэш устарел — пробуем обновить
        try:
            df = self.load_from_db()
            self.save_to_cache(df)
            return df
        except Exception:
            print("БД недоступна, использую старые данные из кэша")
            return cached_df
