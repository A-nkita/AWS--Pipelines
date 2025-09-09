import os
import pandas as pd
from sqlalchemy import create_engine

# Example DataFrame
data = {
    "customer_id": [1, 2, 3],
    "first_name": ["Amit", "Sneha", "Rohan"],
    "last_name": ["Patel", "Sharma", "Mehta"],
    "email": ["amit@example.com", "sneha@example.com", "rohan@example.com"],
    "phone_number": ["9999999999", "8888888888", "7777777777"],
    "join_date": ["2024-01-10", "2024-02-15", "2024-03-20"],
    "city": ["Mumbai", "Delhi", "Pune"],
    "last_purchase_date": ["2024-08-01", "2024-08-15", "2024-09-01"]
}
df = pd.DataFrame(data)

# --- Redshift connection details (from env variables ideally) ---
redshift_host = os.environ["REDSHIFT_HOST"]        #Endpoints
redshift_port = "5439"  # default for Redshift
redshift_db   = os.environ["REDSHIFT_DB"]
redshift_user = os.environ["REDSHIFT_USER"]
redshift_pass = os.environ["REDSHIFT_PASSWORD"]

# --- Create SQLAlchemy engine ---
# Redshift uses PostgreSQL driver
engine = create_engine(
    f"postgresql+psycopg2://{redshift_user}:{redshift_pass}@{redshift_host}:{redshift_port}/{redshift_db}"
)

# --- Write DataFrame to Redshift ---
df.to_sql(
    "customers",        # Table name in Redshift
    engine,
    index=False,
    if_exists="replace"  # or "append" to add rows
)
