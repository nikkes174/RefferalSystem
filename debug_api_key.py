from main import app
from starlette.testclient import TestClient

print("=== DEBUG MIDDLEWARE ===")

client = TestClient(app)

resp = client.get("/referrals/top/1", headers={"X-API-Key": "xxx"})

print("STATUS:", resp.status_code)
print("BODY:", resp.text)
