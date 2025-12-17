# Cloud-Anomaly-Detection

A FastAPI-based system for detecting anomalies in cloud environments using metrics and log analysis.

## Features
- **Multi-agent detection**: Fast metrics analysis and slow log analysis
- **Symbolic verification**: Rule-based validation of detected anomalies
- **28+ anomaly scenarios**: Covers resource, network, software, and security anomalies
- **RESTful API**: Easy integration with monitoring systems

## Project Structure
cloud-anomaly-detection/  
├── src/ # Source code  
│ ├── main.py # Main FastAPI application  
│ └── test_client.py # API test client  
├── config/ # Configuration files  
├── tests/ # Test files  
├── logs/ # Application logs  
├── models/ # Trained models  
├── data/ # Sample data  
├── docs/ # Documentation  
├── .[env.dev](https://env.dev) # Development environment variables  
├── .env.stg # Staging environment variables  
├── .env.prod # Production environment variables  
├── docker-compose.yml # Base docker-compose  
├── [docker-compose.dev](https://docker-compose.dev).yml  
├── docker-compose.stg.yml  
├── docker-compose.prod.yml  
├── docker-compose.common.yml  
├── Dockerfile # Multi-stage Docker build  
├── Makefile # Build and deployment commands  
├── .gitlab-ci.yml # CI/CD pipeline  
├── requirements.txt # Python dependencies  
├── run.sh # Startup script  
├── sample_usage.py # Usage examples  
└── README.md # This file

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
```

## Quick Start

### Local Development
```bash
# 1. Clone and setup
git clone https://github.com/donmemedo/Cloud-Anomaly-Detection.git
cd Cloud-Anomaly-Detection
git checkout dev

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python src/main.py
# or using the script
./run.sh
```
### Using Docker
```bash
# Development
docker-compose -f docker-compose.dev.yml up --build

# Production
docker-compose -f docker-compose.prod.yml up -d
```
### Using Makefile

```bash
make install      # Install dependencies
make run-dev      # Run development server
make test         # Run tests
make build-prod   # Build production image
make deploy-stg   # Deploy to staging
```
## API Usage

Once running, access:

-   **API**: [http://localhost:8000](http://localhost:8000)
    
-   **Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
    
-   **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)
    

### Test the API:
```bash
python sample_usage.py
python src/test_client.py
```
## Environment Configuration

-   **Development**: Use `.env.dev` and port 8001
    
-   **Staging**: Use `.env.stg` and port 8002
    
-   **Production**: Use `.env.prod` and port 8000
    

## Branch Strategy

-   **`dev`** → Development with hot reload
    
-   **`stg`** → Staging with monitoring
    
-   **`main`** → Production with full stack
    

## Contributing

See CONTRIBUTING.md for guidelines.

## License

MIT License - see LICENSE file.

