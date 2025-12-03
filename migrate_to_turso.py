import sqlite3
import requests
import json

# ---------------------------
# CONFIG
# ---------------------------
LOCAL_DB = "university_database.db"

DB_URL = "https://clouduniversitydatabase-yasser-daffa.aws-eu-west-1.turso.io"
DB_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJleHAiOjE3OTYzMTI2MTcsImlhdCI6MTc2NDc3NjYxNywiaWQiOiIwZWFmMzAwOC1hZTM0LTRlYzktYjI5My03MDk5OGJlZTUzNzIiLCJyaWQiOiJiZjFiNWEzYy00MzhiLTRjZDctYTA4OS1iNGM0YTkyODk0MzMifQ.XHWP2xaiGQCta13oHdz4bXt6x_g37GBCvringmq-rxm1tN2J5MG-lM4LTq2SVtK9hC5wRul7ehCNlUIzsoviBQ"

# ---------------------------
# EXECUTOR (your exact style)
# ---------------------------
def execute(sql):
    headers = {
        "Authorization": f"Bearer {DB_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "stmt": {
            "sql": sql,
            "args": []
        }
    }

    r = requests.post(
        f"{DB_URL}/v1/execute",
        headers=headers,
        data=json.dumps(payload)
    )

    if not r.ok:
        print(f" Error creating table: {r.text}")
    else:
        print("    Executed")


# ---------------------------
# MIGRATE ONLY SCHEMA
# ---------------------------
print("[INFO] Opening local DB:", LOCAL_DB)
con = sqlite3.connect(LOCAL_DB)
cur = con.cursor()

tables = cur.execute(
    "SELECT name, sql FROM sqlite_master WHERE type='table'"
).fetchall()

print(f"[INFO] Found {len(tables)} tables.")

for name, create_sql in tables:
    if create_sql is None:
        continue

    print(f"\n[CREATE] {name}")
    execute(create_sql)

print("\n[DONE] All table schemas migrated. No data copied.")
