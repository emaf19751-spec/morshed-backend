import psycopg2

def init_db():
    conn = psycopg2.connect(
        host="db",
        port="5432",
        user="morshed",
        password="morshed123",
        dbname="morsheddb"
    )
    cur = conn.cursor()

    # Drop old table if it exists
    cur.execute("DROP TABLE IF EXISTS roadside_requests;")

    # Recreate the table with the correct schema
    cur.execute("""
    CREATE TABLE roadside_requests (
        id SERIAL PRIMARY KEY,
        service VARCHAR(50),
        vehicle_make VARCHAR(50),
        vehicle_model VARCHAR(50),
        year INT,
        mileage_km INT,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ roadside_requests table has been reset and is ready.")

if __name__ == "__main__":
    init_db()
