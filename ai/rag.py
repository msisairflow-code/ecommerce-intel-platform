from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine,text
from google import genai
engine = create_engine('postgresql://warehouse:warehouse@localhost/warehouse')
model = SentenceTransformer('all-MiniLM-L6-v2')
client =genai.Client()
def retrieve_query(content, top_k=5):
    embedding = model.encode(content).tolist()
    embedding_str = "[" + ','.join(map(str, embedding)) + "]"
    print(f"Query embedding: {embedding_str}")
    with engine.connect() as conn:
        result = conn.execute(
            text("""SELECT source_table, source_id, content, embedding <=> CAST(:emb AS vector) AS distance
                     FROM analytics.document_embeddings
                     ORDER BY distance ASC
                     LIMIT :k"""),
            {"emb": embedding_str, "k": top_k},
        )
        return [dict(row._mapping) for row in result]

def generate_answer(question,chunk):
    context = "\n\n".join(f"- {c['content']}" for c in chunk)
    prompt = f"""Answer the customer's question using only the context below.
    If the context doesn't contain the answer, say you don't know.

    Context:
    {context}

    Question: {question}"""
    response=client.models.generate_content(
        model="gemini-2.5-flash",
        contents= prompt,
    )
    return response.text

if __name__ == "__main__":
    print("E-commerce assistant ready. Type 'exit' to quit.")
    while True:
        question = input("\nAsk a question: ")
        if question.lower() == "exit":
            break
        chunks = retrieve_query(question)
        answer = generate_answer(question, chunks)
        print(f"\nAnswer: {answer}")




