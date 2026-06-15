from dotenv import load_dotenv
import os

load_dotenv()

APP_NAME = os.getenv("APP_NAME")
APP_VERSION = os.getenv("APP_VERSION")