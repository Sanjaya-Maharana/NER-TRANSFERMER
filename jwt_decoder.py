import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from datetime import datetime

JWT_USER_SECRET_KEY = "asdgcvsdcv@@@#$@%@!~!~!!)(U*@*fdbvjblejhfvhgvsjfgv$@%&*(W&!)W(!SDHQWFUWKDDOY@TEF@&ETO!*E@(T@(ET!QDXWFBCWJWFGEKUFEUE"
ADMIN_SECRET_JWT_TOKEN = "rtawdchvscfbdhfvbjkdfnvhdgfjhhHHHHH@@!$@#(%*#$@(*)#!()@*$73y8277"
JWT_ENCODE_ALGO = "HS256"

def decode_jwt_token(token: str):
    try:
        decoded_token = jwt.decode(token, ADMIN_SECRET_JWT_TOKEN, algorithms=[JWT_ENCODE_ALGO])
        return decoded_token
    except ExpiredSignatureError:
        return {"error": "Token has expired"}
    except InvalidTokenError:
        return {"error": "Invalid token"}
    except Exception:
        try:
            decoded_token = jwt.decode(token, JWT_USER_SECRET_KEY, algorithms=[JWT_ENCODE_ALGO])
            return decoded_token
        except ExpiredSignatureError:
            return {"error": "Token has expired"}
        except InvalidTokenError:
            return {"error": "Invalid token"}
        except Exception as e:
            return {"error": str(e)}


decoded = decode_jwt_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwiZmlyc3RfbmFtZSI6IlRoZSIsImxhc3RfbmFtZSI6Ik9jZWFubiIsInBhc3N3b3JkIjoicGJrZGYyX3NoYTI1NiQzOTAwMDAkenBrcXBQV2pyUU5KckI5T0lCVVk5MSQrdDEwSDRZZE9ZREZvbUNpWStZMEdlWUZaWmtFaHBsVys3NmxnZEZLcVFzPSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiY29tcGFueV9uYW1lIjoidGhvciIsImNvbXBhbnlfYWRkcmVzcyI6ImJodXRhbmlcbmFscGhhdGh1bSIsImVtYWlsIjoib2NlYW5uQHlvcG1haWwuY29tIiwic3RhdHVzIjoxLCJzdWJzY3JpYmVkX3VzZXJzIjpudWxsLCJ1c2VyX2FjdGl2ZSI6bnVsbCwiaW5hY3RpdmVfdXNlcnMiOm51bGwsInBob25lX251bWJlciI6Ijk4OTg3Njc3ODAiLCJjb21wYW55X2RvbWFpbiI6ImFzZHNzZCIsIm9uYm9yZGluZ19kYXRlIjoiMjAyMy0xMi0xNlQxNzoxOTo0MCswNTozMCIsImNvdW50cnkiOiJJbmRpYSIsImNvdW50cnlfY29kZSI6Iis5MSIsImNvbXBhbnlfdHlwZSI6eyJsYWJlbCI6Ik9wZXJhdGlvbiIsInZhbHVlIjoiT3BlcmF0aW9uIn0sImN1cnJlbmN5IjoiQWxnZXJpYW4gRGluYXIiLCJmYXhfbnVtYmVyIjoiODc2NTQ2NzgiLCJjcmVhdGVkX2F0IjoiMjAyMy0xMi0xNlQxNzoxOTo0MCswNTozMCIsIm1vZGlmaWVkX2F0IjpudWxsLCJ2YXQiOiIxMjM0NTY3ODkwOTg3NjU0MzIxMSIsImlzX3N1YnNjcmliZWQiOnRydWUsInVzZXJfZG9tYWluIjoidGhvciIsInR3b2ZhX2F1dGhfZW5hYmxlIjpmYWxzZSwidHdvZmFfc2VjcmV0IjpudWxsLCJtYWlsX2ltcG9ydF9saW1pdCI6MTAsIlZNX0FDQ0VTUyI6dHJ1ZSwiTUFJTF9BQ0NFU1MiOnRydWUsImRhdGFiYXNlX25hbWUiOiJ0aG9yIiwic3Vic2NyaWJlcl91c2VyX2xpbWl0IjpudWxsLCJpc192bV90b3VyX2lzX2NvbXBsZXRlZCI6dHJ1ZSwibm9fb2ZfbG9naW5zIjo4Mzc1LCJjb21wYW55X2Rpc3BsYXkiOm51bGwsInJlZ19ubyI6bnVsbCwiaXNfdm1fZGJfY3JlYXRlZCI6dHJ1ZSwiaW5pdGlhbF9lbWFpbF9jb3VudCI6NTAxLCJpbXBvcnRfZW5hYmxlX2Rpc2FibGUiOmZhbHNlLCJzaWdudXBfcGxhY2UiOiJ3ZWJzaXRlIiwiaXNfYmFubmVyX3Zpc2libGUiOmZhbHNlLCJpc3RvdXJndWlkZSI6dHJ1ZSwicm9sZSI6ImFkbWluIiwiZW1haWxDbGllbnRzIjpbeyJpZCI6Mzg2LCJpbXBvcnRfZW1haWwiOiJicm9rZXJzQHRoZW9jZWFubi5jb20iLCJNYWlsTGFiZWwiOiJCcm9rZXJzIn0seyJpZCI6MzkwLCJpbXBvcnRfZW1haWwiOiJmaXhAdGhlb2NlYW5uLmFpIiwiTWFpbExhYmVsIjoiZml4ICJ9LHsiaWQiOjM0MSwiaW1wb3J0X2VtYWlsIjoib3BzQHRoZW9jZWFubi5haSIsIk1haWxMYWJlbCI6Ik9wcyJ9LHsiaWQiOjM5NiwiaW1wb3J0X2VtYWlsIjoib21zYWlAdGhlb2NlYW5uLmFpIiwiTWFpbExhYmVsIjpudWxsfV0sImluYm94ZXMiOlsiYnJva2Vyc0B0aGVvY2Vhbm4uY29tIiwiZml4QHRoZW9jZWFubi5haSIsIm9wc0B0aGVvY2Vhbm4uYWkiLCJvbXNhaUB0aGVvY2Vhbm4uYWkiXSwiaXNzIjoiQXV0aCBTZXJ2aWNlIHNhc3MiLCJleHAiOjE3MjgwMTUxMjEsImlzc3Vlcl9tYWlsIjoib21zYWlAdGhlb2NlYW5uLmFpIiwianRpIjoiNzczNzFlNWYtMDkwNS00YTVjLWEwMDMtZGE3NjgzNWU0ZGVjIn0.gIYbNoIHplH0VhTp7g6gxLmg941SByAy1EQdaeN9MIA")
print(decoded)



