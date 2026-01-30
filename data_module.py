from pymongo import MongoClient
import pandas as pd
import pickle
import os
import time

CACHE_PATH = "cache/data_cache.pkl"
CACHE_TTL_SECONDS = 300  # МЕНЯЕТЕ ЗДЕСЬ (в секундах)


class DataManager:
    def __init__(self, mongo_uri, db_name, collection_name):
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.collection_name = collection_name

    # ---------- Mongo ----------

    def _connect(self):
        client = MongoClient(
            self.mongo_uri,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=3000,
        )

        # ВАЖНО: принудительная проверка соединения
        client.admin.command("ping")

        db = client[self.db_name]
        return db[self.collection_name]

    def load_from_db(self):
        collection = self._connect()
        data = list(collection.find({}, {"_id": 0}))

        if not data:
            return pd.DataFrame()

        return pd.DataFrame(data)

    # ---------- Cache ----------

    def save_to_cache(self, df: pd.DataFrame):
        os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)

        payload = {
            "timestamp": time.time(),
            "data": df
        }

        with open(CACHE_PATH, "wb") as f:
            pickle.dump(payload, f)

    def load_from_cache(self):
        if not os.path.exists(CACHE_PATH):
            return None, None

        try:
            with open(CACHE_PATH, "rb") as f:
                payload = pickle.load(f)

            if isinstance(payload, dict):
                return payload.get("data"), payload.get("timestamp")

            # старый формат
            return payload, None

        except Exception:
            return None, None

    # ---------- Public ----------

    def get_data(self):
        cached_df, cached_time = self.load_from_cache()

        # 1. Есть кэш и он свежий
        if cached_df is not None and cached_time is not None:
            age = time.time() - cached_time
            if age < CACHE_TTL_SECONDS:
                print("Загружены данные из кэша")
                return cached_df

        # 2. Пытаемся обновить из БД
        try:
            print("Пробую загрузить данные из БД...")
            df = self.load_from_db()

            if not df.empty:
                self.save_to_cache(df)
                print("Данные загружены из БД и сохранены в кэш")
                return df

        except Exception as e:
            print("БД недоступна:", e)

        # 3. БД недоступна, но есть старый кэш
        if cached_df is not None:
            print("Использую старые данные из кэша")
            return cached_df

        # 4. Совсем ничего нет — НЕ ПАДАЕМ
        print("Нет доступа к БД и отсутствует кэш. Возвращаю пустые данные.")
        return pd.DataFrame()
