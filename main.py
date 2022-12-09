import os
import uuid

import psycopg2


def create_api_secret(identifier, secret, db_connection):
    try:
        cursor = db_connection.cursor()
        cursor.execute(
            "INSERT INTO vng_api_common_jwtsecret (identifier, secret) VALUES(%s, %s)",
            (identifier, secret),
        )
        db_connection.commit()
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def create_authenticated_app(identifier, db_connection, label="token-issuer-seeded"):
    try:
        cursor = db_connection.cursor()
        parsed_identifier = f"{{{identifier}}}"
        parsed_uuid = str(uuid.uuid4())
        heeft_all_authorisatie = True
        cursor.execute(
            "INSERT INTO authorizations_applicatie (uuid, client_ids, label, heeft_alle_autorisaties)  VALUES(%s, %s, %s, %s)",
            (parsed_uuid, parsed_identifier, label, heeft_all_authorisatie),
        )
        db_connection.commit()
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def create_common_api_ref(label, name, db_connection):
    try:
        cursor = db_connection.cursor()
        api_root = f"http://{label}/api/v1/"
        cursor.execute(
            "INSERT INTO vng_api_common_apicredential (api_root, client_id, secret, label, user_id, user_representation)  VALUES(%s, %s, %s, %s, %s, %s)",
            (api_root, name, name, label, name, name),
        )
        db_connection.commit()
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


if __name__ == "__main__":
    APIS = [
        "nrc",
        "zrc",
        "drc",
        "ztc",
        "brc",
        "ac"
    ]
    DB_NAME = os.environ.get("DB_NAME", "ac")
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_USER = os.environ.get("DB_USER", "postgres")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "supersecretpassword")
    IDENTIFIER = os.environ.get("TOKEN_ISSUER_NAME", "token_issuer_demo")
    SECRET = os.environ.get("TOKEN_ISSUER_SECRET", "thisisnotverysecretnotisitsafe")
    print(f"seeding db {DB_NAME}")
    connection = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=5432
    )

    api = DB_NAME
    for inner_name in APIS:
        create_common_api_ref(inner_name, api, connection)
        create_api_secret(inner_name, inner_name, connection)
        create_authenticated_app(identifier=inner_name, db_connection=connection, label=inner_name)

    create_authenticated_app(identifier=IDENTIFIER, db_connection=connection)
    create_api_secret(identifier=IDENTIFIER, secret=SECRET, db_connection=connection)

    connection.close()
    print(f"done seeding db {DB_NAME}")
