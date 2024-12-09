from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class DBHandler:
    def __init__(self):
        connection_string = os.getenv("MONGO_URI")
        try:
            self.client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            print("Connected to MongoDB")
            self.db = self.client['nailib']
            self.collection = self.db['sample_data']
        except Exception as e:
            print(f"Error connecting to database: {e}")
