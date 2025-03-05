import os

from dotenv import load_dotenv

load_dotenv()
upbit = {
    "accessKey": os.getenv("UPBIT_ACCESS_KEY"),
    "secretKey": os.getenv("UPBIT_SECRET_KEY"),
}
bithumb = {
    "accessKey": os.getenv("BITHUMB_ACCESS_KEY"),
    "secretKey": os.getenv("BITHUMB_SECRET_KEY"),
}

database = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "database": os.getenv("DB_NAME"),
    "url": f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}",
}
