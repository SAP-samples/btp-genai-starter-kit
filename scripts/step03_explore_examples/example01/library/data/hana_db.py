from hdbcli import dbapi
import os


# Function to get a connection to the HANA DB
def get_connection_to_hana_db():
    conn = dbapi.connect(
        address=os.environ.get("HANA_DB_ADDRESS"),
        port=os.environ.get("HANA_DB_PORT"),
        user=os.environ.get("HANA_DB_USER"),
        password=os.environ.get("HANA_DB_PASSWORD"),
        encrypt=True,
        sslValidateCertificate=False,
    )
    return conn
