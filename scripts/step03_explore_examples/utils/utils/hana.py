from logging import getLogger
import os
import sys
from hdbcli import dbapi
from .env import assert_env
from .logging import initLogger

log = getLogger(__name__)
initLogger()


def check_if_exists(table_name, schema_name="DBADMIN"):
    connection_to_hana = get_connection_to_hana_db()
    cursor = connection_to_hana.cursor()

    # Check if the table exists
    check_table_query = """
    SELECT COUNT(*)
    FROM TABLES
    WHERE SCHEMA_NAME = ? AND TABLE_NAME = ?
    """

    cursor.execute(check_table_query, (schema_name, table_name))
    return cursor.fetchone()[0] > 0


def teardown_hana_table(table_name):
    """
    Drops the specified table in the HANA database.

    Args:
        table_name (str): The name of the table to be dropped.

    Raises:
        Exception: If there is an error dropping the table.

    Returns:
        None
    """

    exists = check_if_exists(table_name=table_name)
    if exists is False:
        log.success("Nothing to clean up")
        return

    try:
        connection_to_hana = get_connection_to_hana_db()
        cur = connection_to_hana.cursor()
        log.info(f"Dropping table {table_name}")
        cur.execute(f"DROP TABLE {table_name}")
        cur.close()
        log.success(f"Table {table_name} dropped successfully.")
    except Exception as e:
        log.error(type(e))
        log.error(f"Error dropping table: {str(e)}")


# Function to get a connection to the HANA DB
def get_connection_to_hana_db():
    """
    Establishes a connection to the HANA database.

    Returns:
        conn: A connection object representing the connection to the HANA database.

    Raises:
        Exception: If there is an error connecting to the HANA database.
    """
    try:
        assert_env(
            [
                "HANA_DB_ADDRESS",
                "HANA_DB_PORT",
                "HANA_DB_USER",
                "HANA_DB_PASSWORD",
            ]
        )
        conn = dbapi.connect(
            address=os.environ.get("HANA_DB_ADDRESS"),
            port=os.environ.get("HANA_DB_PORT"),
            user=os.environ.get("HANA_DB_USER"),
            password=os.environ.get("HANA_DB_PASSWORD"),
            encrypt=True,
            sslValidateCertificate=False,
        )
        return conn
    except Exception as e:
        log.error(f"Error connecting to HANA DB: {str(e)}")
        sys.exit()


def get_connection_string():
    """
    Returns the connection string for connecting to a HANA database.

    The connection string is generated using the environment variables:
    - HANA_DB_ADDRESS: the address of the HANA database
    - HANA_DB_PORT: the port number of the HANA database
    - HANA_DB_USER: the username for connecting to the HANA database
    - HANA_DB_PASSWORD: the password for connecting to the HANA database

    Returns:
    str: The connection string for connecting to the HANA database.
    """
    assert_env(
        [
            "HANA_DB_ADDRESS",
            "HANA_DB_PORT",
            "HANA_DB_USER",
            "HANA_DB_PASSWORD",
        ]
    )
    return "hana+hdbcli://{user}:{password}@{address}:{port}?encrypt=true".format(
        user=os.environ.get("HANA_DB_USER"),
        password=os.environ.get("HANA_DB_PASSWORD"),
        address=os.environ.get("HANA_DB_ADDRESS"),
        port=os.environ.get("HANA_DB_PORT"),
    )


def has_embeddings(table_name, verbose=True):
    try:
        assert table_name, "Table name must be provided"

        connection_to_hana = get_connection_to_hana_db()
        cur = connection_to_hana.cursor()
        cur.execute(
            f"SELECT VEC_TEXT, VEC_META, TO_NVARCHAR(VEC_VECTOR) FROM {table_name} LIMIT 1"
        )
        rows = cur.fetchone()
        if verbose:
            print(
                f"Preview of embeddings in table {table_name}: \n\nText: {rows[0][:300]},\nMetadata:{rows[1][:300]},\nVector: {rows[2][:100]}\n"
            )

        cur.close()
        return True
    except Exception as e:
        log.error(f"Error executing query: {str(e)}")
        raise e
