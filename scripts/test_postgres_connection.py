
from pipeline.db import get_connection


def main():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                current_database(),
                current_user,
                version();
        """)

        result = cursor.fetchone()

        print("PostgreSQL connection successful!")
        print("Database:", result[0])
        print("User:", result[1])
        print("Version:", result[2])

    except Exception as error:
        print("PostgreSQL connection failed:")
        print(error)

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


if __name__ == "__main__":
    main()
