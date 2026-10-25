import os
import sys
import json
import urllib.request

SUPABASE_ACCESS_TOKEN = os.getenv("SUPABASE_ACCESS_TOKEN", "")
PROJECT_REF = os.getenv("SUPABASE_PROJECT_REF", "pcwiopxewlxhwvddpndq")

def execute_sql(sql_query: str):
    url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
    headers = {
        "Authorization": f"Bearer {SUPABASE_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    data = json.dumps({"query": sql_query}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode("utf-8")
            if body:
                return json.loads(body)
            return {"status": resp.status, "message": "Success with empty body"}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        print(f"HTTPError {e.code}: {err_body}", file=sys.stderr)
        raise
    except Exception as e:
        print(f"Error executing SQL: {e}", file=sys.stderr)
        raise

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if os.path.exists(arg):
            with open(arg, "r", encoding="utf-8") as f:
                query = f.read()
        else:
            query = arg
    else:
        query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"
    
    result = execute_sql(query)
    print(json.dumps(result, indent=2))
