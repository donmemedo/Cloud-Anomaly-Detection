import requests
import json
import time


# Test data for the API
def create_test_data():
    # Create sample metrics data
    metrics = {
        "timestamp": [f"2024-01-01 00:00:{i:02d}" for i in range(90)],
        "cpu": [20 + 70 * (i > 45) + 5 * (i % 10) for i in range(90)],  # Spike at 45
        "memory": [40 + i * 0.3 for i in range(90)],  # Gradual increase
        "disk_io": [10 + 5 * (i % 5) for i in range(90)],
        "net_in": [50 + 20 * (i % 7) for i in range(90)],
        "net_out": [30 + 15 * (i % 6) for i in range(90)]
    }

    # Create sample log data
    logs = {
        "entries": [
            {
                "timestamp": "2024-01-01 00:03:45",
                "message": "Application timeout: request took 15 seconds",
                "source": "web-app"
            },
            {
                "timestamp": "2024-01-01 00:03:50",
                "message": "ERROR: Database connection failed",
                "source": "database"
            },
            {
                "timestamp": "2024-01-01 00:04:00",
                "message": "CPU usage threshold exceeded: 95%",
                "source": "system"
            }
        ]
    }

    return {
        "metrics": metrics,
        "logs": logs,
        "use_symbolic_verifier": True
    }


def test_detection():
    url = "http://localhost:8000/detect"
    test_data = create_test_data()

    print("Testing CloudAnoAgent API...")
    print("=" * 50)

    response = requests.post(url, json=test_data)

    if response.status_code == 200:
        result = response.json()

        print(f"Status: {response.status_code}")
        print(f"Processing Time: {result['processing_time_ms']:.2f} ms")
        print("\n=== Metrics Agent ===")
        print(f"Anomaly Detected: {result['metrics_agent_output']['is_anomaly']}")
        print(f"Description: {result['metrics_agent_output']['description']}")

        print("\n=== Log Agent ===")
        print(f"Anomaly Detected: {result['log_agent_output']['is_anomaly']}")
        print(f"Description: {result['log_agent_output']['description']}")

        print("\n=== Integrated Agent ===")
        print(f"Anomaly Detected: {result['integrated_agent_output']['is_anomaly']}")
        print(f"Scenario: {result['integrated_agent_output']['anomaly_subtype']}")
        print(f"Reason: {result['integrated_agent_output']['reason']}")

        if result['symbolic_verification_result']:
            print("\n=== Symbolic Verification ===")
            print(f"Verified: {result['symbolic_verification_result']['is_verified']}")
            print(f"Details: {json.dumps(result['symbolic_verification_result']['details'], indent=2)}")

        print("\n=== Final Decision ===")
        print(f"Anomaly: {result['final_decision']['is_anomaly']}")
        print(f"Category: {result['final_decision']['anomaly_category']}")
        print(f"Scenario: {result['final_decision']['anomaly_subtype']}")
        print(f"Reason: {result['final_decision']['reason']}")

    else:
        print(f"Error: {response.status_code}")
        print(response.text)


def test_health():
    url = "http://localhost:8000/health"
    response = requests.get(url)
    print(f"Health Check: {response.status_code}")
    print(response.json())


def test_scenarios():
    url = "http://localhost:8000/scenarios"
    response = requests.get(url)
    print(f"Scenarios: {response.status_code}")
    data = response.json()
    print(f"Total scenarios: {len(data['scenarios'])}")


if __name__ == "__main__":
    # Wait for server to start
    time.sleep(2)

    print("CloudAnoAgent API Tests")
    print("=" * 50)

    test_health()
    print()

    test_scenarios()
    print()

    test_detection()