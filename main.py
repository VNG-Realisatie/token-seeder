import os
import uuid
import configparser

import psycopg2


def create_api_secret(identifier, secret, db_connection):
    try:
        cursor = db_connection.cursor()
        print(f"adding vng_api_common_jwtsecret with client_id: {identifier}")
        cursor.execute(
            "INSERT INTO vng_api_common_jwtsecret (identifier, secret) VALUES(%s, %s)",
            (identifier, secret),
        )
        db_connection.commit()
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def create_authenticated_app(
    identifier, label="token-issuer-seeded", db_connection=None
):
    try:
        cursor = db_connection.cursor()
        parsed_identifier = f"{{{identifier}}}"
        parsed_uuid = str(uuid.uuid4())
        heeft_all_authorisatie = True
        print(f"adding authorizations_applicatie with client_id: {parsed_identifier}")
        cursor.execute(
            "INSERT INTO authorizations_applicatie (uuid, client_ids, label, heeft_alle_autorisaties)  VALUES(%s, %s, %s, %s)",
            (parsed_uuid, parsed_identifier, label, heeft_all_authorisatie),
        )
        db_connection.commit()
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def create_common_api_credential(api_config, client_id, secret, db_connection):
    try:
        print(f"adding vng_api_common_apicredential with client_id: {client_id}")
        cursor = db_connection.cursor()
        for name in api_config:
            print(f"label set to api: {name}")
            print(f"api_root set to: {api_config[name]}")
            cursor.execute(
                "INSERT INTO vng_api_common_apicredential (api_root, client_id, secret, label, user_id, user_representation)  VALUES(%s, %s, %s, %s, %s, %s)",
                (api_config[name], client_id, secret, name, client_id, client_id),
            )
        db_connection.commit()
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def create_auth_config(name, component, db_connection):
    try:
        cursor = db_connection.cursor()
        api_root = f"{name}/api/v1/"
        print(
            f"adding authorizations_authorizationsconfig for component: {component} with api_root {api_root}"
        )
        cursor.execute(
            "INSERT INTO authorizations_authorizationsconfig (api_root, component)  VALUES(%s, %s)",
            (api_root, component),
        )
        db_connection.commit()
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


if __name__ == "__main__":
    env = os.environ.get("ENV", "kubernetes")
    DB_NAME = os.environ.get("DB_NAME", "zrc")
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_USER = os.environ.get("DB_USER", "postgres")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "supersecretpassword")
    IDENTIFIER = os.environ.get("TOKEN_ISSUER_NAME", "token_issuer_demo")
    SECRET = os.environ.get("TOKEN_ISSUER_SECRET", "thisisnotverysecretnorisitsafe")
    INTERNAL_API_SECRET = os.environ.get(
        "INTERNAL_API_SECRET", "thisisnotverysecretnorisitsafe"
    )
    AUTH_SERVICE = os.environ.get("AUTH_SERVICE", "http://ac:8000")
    SERVICE_NAME = os.environ.get("SERVICE_NAME")
    if SERVICE_NAME is None:
        print(
            f"SERVICE_NAME env value not set so assuming that is equal to the DB you are using: {DB_NAME}"
        )
        SERVICE_NAME = DB_NAME

    config = configparser.ConfigParser()
    config.read("config.ini")
    api_config = config[env]

    print(f"seeding db {DB_NAME}")
    connection = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=5432
    )

    apis_to_add = [api for api in api_config]
    api_endpoints = [api_config[api] for api in api_config]

    for name in api_config:
        print(f"working on {name} with endpoint: {api_config[name]}")

        create_api_secret(
            identifier=name, secret=INTERNAL_API_SECRET, db_connection=connection
        )
        create_authenticated_app(identifier=name, label=name, db_connection=connection)

    create_common_api_credential(
        api_config=api_config,
        client_id=SERVICE_NAME,
        secret=INTERNAL_API_SECRET,
        db_connection=connection,
    )
    create_auth_config(
        name=AUTH_SERVICE, component=SERVICE_NAME, db_connection=connection
    )
    create_authenticated_app(identifier=IDENTIFIER, db_connection=connection)
    create_api_secret(identifier=IDENTIFIER, secret=SECRET, db_connection=connection)

    connection.close()
    print(f"done seeding db {DB_NAME}")
