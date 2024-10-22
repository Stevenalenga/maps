import requests

url = "http://localhost:8000/api/register"
headers = {"Content-Type": "application/json"}
data = {
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "securepassword123"
}

response = requests.post(url, json=data, headers=headers)
print(response.status_code)
print(response.json())