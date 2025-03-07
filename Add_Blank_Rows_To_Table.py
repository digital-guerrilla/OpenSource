import requests
table_id=""
api_key = ""
n = 500

url = f"https://api.morta.io/v1/table/{table_id}/row"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "rows": [{"rowData": {"Example Column 1": None}} for _ in range(n)]
}

for _ in range(n):
    data["rows"].append({"rowData": {"Example Column 1": None}})
    print(f"added row {_}")

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    print("Request was successful")
else:
    print(f"Request failed with status code {response.status_code}")