import os
import uuid
import configparser

import psycopg2


def create_api_secret(identifier, secret, db_connection):
    """
    A combination of an identifier and secret is created in the database
    :param identifier: a client_id part of the JWT
    :param secret: the secret to identify the client_id
    :param db_connection: connection to postgres
    :return:
    """
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
    """
    The authorizations_applicatie table holds the combination of a identifier with an admin flag (heeft_alle_autorisaties).
    The identifier and secret have to be added to vng_api_common_jwtsecret as well using:

    create_api_secret(identifier, secret, db_connection)

    :param identifier: a client_id part of the JWT
    :param label: a human-readable label to set a purpose for the identifier
    :param db_connection: connection to postgres
    :return:
    """
    try:
        cursor = db_connection.cursor()
        parsed_identifier = f"{{{identifier}}}"
        parsed_uuid = str(uuid.uuid4())
        # When seeding data we want each api to have admin rights
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


def create_common_api_credential(api_config, client_id, secret, namespace, db_connection):
    """
    Creates all the services with endpoints in the vng_api_common_apicredential table
    So that each api trusts all the other internal apis
    The internal service address is also added so you can use the full internal address since
    the short version will fail some URL regexes
    :param api_config: a list of api names and endpoints (provided by config.ini)
    :param client_id: a client_id part of the JWT
    :param secret: the secret to identify the client_id
    :param db_connection: connection to postgres
    :return:
    """
    try:
        print(f"adding vng_api_common_apicredential with client_id: {client_id}")
        cursor = db_connection.cursor()
        for name in api_config:
            print(f"label set to api: {name}")
            print(f"api_root set to: {api_config[name]}")
            internal_address = f"http://{name}.{namespace}.svc.cluster.local:8000/api/v1"
            print(f"internal_address set to: {internal_address}")
            cursor.execute(
                "INSERT INTO vng_api_common_apicredential (api_root, client_id, secret, label, user_id, user_representation)  VALUES(%s, %s, %s, %s, %s, %s)",
                (api_config[name], client_id, secret, name, client_id, client_id),
            )

            cursor.execute(
                "INSERT INTO vng_api_common_apicredential (api_root, client_id, secret, label, user_id, user_representation)  VALUES(%s, %s, %s, %s, %s, %s)",
                (internal_address, client_id, secret, name, client_id, client_id),
            )
        db_connection.commit()
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def create_auth_config(auth_service, component, db_connection):
    """
    In order for the apis to know where to authenticate tokens provided by a request they need access to autorisatie-api.
    When using kubernetes this should be an internal call to the service address.
    This used to be a task for an admin to create to correct ac_service_endpoint but is now part of the seeding process.
    :param auth_service: the base address of the auth_service for example: http://ac:8000
    :param component: name of the service to register for example: ztc
    :param db_connection: connection to postgres
    :return:
    """
    try:
        cursor = db_connection.cursor()
        api_root = f"{auth_service}/api/v1/"
        print(
            f"adding authorizations_authorizationsconfig for component: {component} with api_root {api_root}"
        )
        query = "SELECT * FROM authorizations_authorizationsconfig"

        cursor.execute(query)
        records = cursor.fetchall()
        if len(records) == 1:
            print("a record already exists so updating instead of creating")
            print(records)
            cursor.execute(
                """ UPDATE authorizations_authorizationsconfig
                        SET api_root = %s
                        WHERE id = %s""",
                (api_root, 1),
            )
        else:
            cursor.execute(
                "INSERT INTO authorizations_authorizationsconfig (id, api_root, component)  VALUES(1, %s, %s)",
                (api_root, component),
            )
        db_connection.commit()
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


if __name__ == "__main__":
    # variables will be read from the config.ini
    env = os.environ.get("ENV", "kubernetes")

    # variables related to the db connection
    DB_NAME = os.environ.get("DB_NAME", "zrc")
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_USER = os.environ.get("DB_USER", "postgres")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "supersecretpassword")

    #namespace
    NAMESPACE = os.environ.get("NAMESPACE", "vng")

    # Identifier for the token-issuer
    IDENTIFIER = os.environ.get("TOKEN_ISSUER_NAME", "token_issuer_demo")
    # Secret for the token-issuer
    SECRET = os.environ.get("TOKEN_ISSUER_SECRET", "thisisnotverysecretnorisitsafe")
    # Secret so that apis can communicate with one another
    INTERNAL_API_SECRET = os.environ.get(
        "INTERNAL_API_SECRET", "thisisnotverysecretnorisitsafe"
    )
    # The address for the auth_service
    AUTH_SERVICE = os.environ.get("AUTH_SERVICE", "http://ac:8000")

    # The current service that will be seeded
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

    for service_name in api_config:
        print(
            f"working on service: {service_name} with endpoint: {api_config[service_name]}"
        )

        # Create the identifier and secret for each service so apis can reach each other
        create_api_secret(
            identifier=service_name,
            secret=INTERNAL_API_SECRET,
            db_connection=connection,
        )

        create_authenticated_app(
            identifier=service_name, label=service_name, db_connection=connection
        )

    # add all endpoints with the secret so that the SERVICE_NAME will trust the other apis
    create_common_api_credential(
        api_config=api_config,
        client_id=SERVICE_NAME,
        secret=INTERNAL_API_SECRET,
        namespace=NAMESPACE,
        db_connection=connection,
    )

    # set the address for the autorisatie-api for this service
    create_auth_config(
        auth_service=AUTH_SERVICE, component=SERVICE_NAME, db_connection=connection
    )

    # Create the identifier and secret for the token-issuer in this service
    create_authenticated_app(identifier=IDENTIFIER, db_connection=connection)
    create_api_secret(identifier=IDENTIFIER, secret=SECRET, db_connection=connection)

    connection.close()
    print(f"done seeding db {DB_NAME}")
