# Cloud-Anomaly-Detection

A FastAPI-based system for detecting anomalies in cloud environments using metrics and log analysis.

## Features
- **Multi-agent detection**: Fast metrics analysis and slow log analysis
- **Symbolic verification**: Rule-based validation of detected anomalies
- **28+ anomaly scenarios**: Covers resource, network, software, and security anomalies
- **RESTful API**: Easy integration with monitoring systems

## Quick Start

### Prerequisites
- Python 3.10+
- Docker (optional)

### Local Installation
```bash
git clone https://github.com/donmemedo/Cloud-Anomaly-Detection.git
cd Cloud-Anomaly-Detection
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```



## Branch Strategy
- **`dev`** → Development branch for ongoing work
- **`stg`** → Staging branch for pre-production testing  
- **`main`** → Production-ready releases


## Development Workflow

### Branch Usage
```bash
# Start new feature from dev
git checkout dev
git pull origin dev
git checkout -b feature/new-detection-algorithm

# Push to staging for testing
git checkout stg
git merge --no-ff feature/new-detection-algorithm
git push origin stg

# Deploy to production
git checkout main
git merge --no-ff stg
git push origin main