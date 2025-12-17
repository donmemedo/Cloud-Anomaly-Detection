# Python client example
import requests

url = "http://localhost:8000/detect"

# Prepare test data
data = {
    "metrics": {
        "timestamp": ["2024-01-01 00:00:00", "2024-01-01 00:00:05", ...],
        "cpu": [20, 25, 95, 98, 96, ...],
        "memory": [40, 41, 42, 43, 44, ...],
        # ... other metrics
    },
    "logs": {
        "entries": [
            {"timestamp": "2024-01-01 00:03:00", "message": "CPU threshold exceeded", "source": "system"},
            # ... more logs
        ]
    },
    "use_symbolic_verifier": True
}

response = requests.post(url, json=data)
print(response.json())