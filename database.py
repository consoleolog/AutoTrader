import psycopg2
from sqlalchemy import create_engine

with open("D:\PycharmProjects\cr\BithumbAutoTrading\database.key") as f:
    lines = f.readlines()
    user = lines[0].strip()
    password = lines[1].strip()
    host = lines[2].strip()
    port = lines[3].strip()
    database = lines[4].strip()

    connection = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password,
        port=port,
    )

    db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    engine = create_engine(db_url)