import pandas as pd
from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine,text

engine = create_engine('postgresql://warehouse:warehouse@localhost/warehouse')
model = SentenceTransformer('all-MiniLM-L6-v2')

products = pd.read_sql("SELECT product_id, name, description FROM raw.products", engine)
reviews = pd.read_sql("SELECT review_id, review_text FROM raw.reviews", engine)

with engine.connect() as conn:
    conn.execute(text("Truncate table analytics.document_embeddings"))
    conn.commit()

    for _,row in products.iterrows():
        content = f"{row['name']} {row['description']}"
        embedding=model.encode(content).tolist()
        embedding_str = "[" + ','.join(map(str, embedding)) + "]"
        conn.execute(
            text("""INSERT INTO analytics.document_embeddings
                     (source_table, source_id, content, embedding)
                     VALUES (:st, :sid, :content, CAST(:emb AS vector))"""),
            {"st": "products", "sid": int(row["product_id"]), "content": content, "emb": embedding_str},
        )
    for _,row in reviews.iterrows():
        embedding = model.encode(row["review_text"]).tolist()
        embedding_str = "[" + ",".join(map(str, embedding)) + "]"
        conn.execute(
            text("""INSERT INTO analytics.document_embeddings
                     (source_table, source_id, content, embedding)
                     VALUES (:st, :sid, :content, CAST(:emb AS vector))"""),
            {"st": "reviews", "sid": int(row["review_id"]), "content": row["review_text"], "emb": embedding_str},
        )

    conn.commit()

print("Embedding complete.")

