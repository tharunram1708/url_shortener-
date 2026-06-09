from sqlalchemy import create_engine, text

from app.database import build_database_url


def main():
    database_url = build_database_url()

    if not database_url.startswith("mysql"):
        print("DB_ENGINE is not mysql. Set DB_ENGINE=mysql in your .env file.")
        print(f"Current database URL: {database_url}")
        return

    engine = create_engine(database_url, pool_pre_ping=True)

    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1 AS connected"))
        value = result.scalar_one()

    print("Python connected to MySQL successfully.")
    print(f"Test query result: {value}")


if __name__ == "__main__":
    main()
