from os import getenv

user = getenv('POSTGRES_USER')
password = getenv('POSTGRES_PASSWORD')
host = getenv('POSTGRES_HOST')
database = getenv('POSTGRES_DB')
port = getenv('POSTGRES_PORT')

DATABASE_CONNECTION_URI = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'
