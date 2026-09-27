import boto3
import io
import pandas as pd
from sqlalchemy import create_engine

s3=boto3.client('s3',
    endpoint_url="http://localhost:9000",
    aws_access_key_id="minioadmin",
    aws_secret_access_key="minioadmin")

BUCKET="rawdl"
TABLES=["customers", "products", "orders", "order_items", "reviews"]
engine = create_engine('postgresql://warehouse:warehouse@localhost:5432/warehouse')

for table in TABLES:
    obj = s3.get_object(Bucket=BUCKET, Key=f"{table}.csv")
    df = pd.read_csv(io.BytesIO(obj['Body'].read()))
    df.to_sql(table, engine, schema="raw",if_exists='replace', index=False)
    print(f"Loaded {table} from MinIO: {len(df)} rows")