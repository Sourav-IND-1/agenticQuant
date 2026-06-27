import requests

res = requests.post("http://localhost:8000/api/analyze", json={"prompt": "Invest $50k over 1 year with moderate risk. Expecting AAPL and GOOGL to outperform."})
print(res.status_code)
print(res.text)
