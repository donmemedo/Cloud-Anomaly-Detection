import json
import re
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import numpy as np
from enum import Enum
import asyncio
from contextlib import asynccontextmanager


# ============= Data Models =============
class MetricData(BaseModel):
    timestamp: List[str]
    cpu: List[float]
    memory: List[float]
    disk_io: List[float]
    net_in: List[float]
    net_out: List[float]
    gpu: Optional[List[float]] = None


class LogEntry(BaseModel):
    timestamp: str
    message: str
    source: str


class LogData(BaseModel):
    entries: List[LogEntry]


class DetectionRequest(BaseModel):
    metrics: MetricData
    logs: LogData
    use_symbolic_verifier: bool = True


class AgentOutput(BaseModel):
    is_anomaly: bool
    description: str
    anomaly_category: Optional[str] = None
    anomaly_subtype: Optional[str] = None
    reason: Optional[str] = None


class DetectionResponse(BaseModel):
    metrics_agent_output: AgentOutput
    log_agent_output: AgentOutput
    integrated_agent_output: AgentOutput
    symbolic_verification_result: Optional[Dict] = None
    final_decision: AgentOutput
    processing_time_ms: float


# ============= Anomaly Scenarios =============
class AnomalyScenario(str, Enum):
    # Resource Exhaustion & Bottlenecks
    CPU_HOG_PROCESS = "cpu_hog_process"
    MEMORY_LEAK = "memory_leak"
    DISK_IO_BOTTLENECK = "disk_io_bottleneck"
    NOISY_NEIGHBOR = "noisy_neighbor"
    HANDLE_THREAD_EXHAUSTION = "handle_thread_exhaustion"

    # Network Anomalies
    HIGH_NETWORK_LATENCY = "high_network_latency_packet_loss"
    BANDWIDTH_SATURATION = "bandwidth_saturation"
    DNS_RESOLUTION_FAILURE = "dns_resolution_failure"
    FIREWALL_MISCONFIGURATION = "firewall_security_group_misconfiguration"

    # Software & Application Anomalies
    APPLICATION_CRASH_LOOP = "application_crash_loop"
    DEADLOCK_LIVELOCK = "deadlock_livelock"
    EXTERNAL_DEPENDENCY_FAILURE = "external_dependency_failure"
    APPLICATION_MISCONFIGURATION = "application_misconfiguration"
    GC_STORM = "garbage_collection_gc_storm"

    # Malicious Events
    CRYPTOMINING_MALWARE = "cryptomining_malware"
    DDOS_BOTNET_AGENT = "ddos_botnet_agent"
    RANSOMWARE = "ransomware"
    DATA_EXFILTRATION = "data_exfiltration"
    SPAM_BOT = "spam_bot"
    ROOTKIT_BACKDOOR = "rootkit_backdoor"
    BRUTE_FORCE_ATTACK = "brute_force_credential_stuffing_attack"
    WEB_SHELL = "web_shell_beaconing_command_execution"
    PASSWORD_CRACKING = "password_cracking"
    LOG_TAMPERING = "log_deletion_tampering"
    REVERSE_SHELL = "reverse_shell"
    APPLICATION_LAYER_DDOS = "application_layer_ddos_attack"

    # Other Complex & Subtle Anomalies
    TIME_SKEW = "time_skew_clock_drift"
    KERNEL_DRIVER_BUG = "kernel_driver_bug"
    NORMAL = "none"


# ============= Agent Classes =============
class MetricsAgent:
    """Fast Detection Agent for metrics analysis"""

    @staticmethod
    def detect_anomaly_patterns(metrics: MetricData) -> Dict[str, Any]:
        """Detect anomaly patterns in metrics data"""
        patterns = {
            "spike": False,
            "dip": False,
            "gradual_increase": False,
            "gradual_decrease": False,
            "fluctuation": False
        }

        # Analyze CPU patterns
        cpu_data = metrics.cpu
        if len(cpu_data) >= 10:
            # Detect spikes (sudden increases)
            if max(cpu_data) > 90 and cpu_data[-1] > np.mean(cpu_data[:5]) + 30:
                patterns["spike"] = True

            # Detect dips (sudden decreases)
            if min(cpu_data) < 10 and cpu_data[-1] < np.mean(cpu_data[:5]) - 30:
                patterns["dip"] = True

            # Detect gradual increase
            trend = np.polyfit(range(len(cpu_data)), cpu_data, 1)[0]
            if trend > 0.5 and cpu_data[-1] > cpu_data[0] + 20:
                patterns["gradual_increase"] = True

            # Detect gradual decrease
            if trend < -0.5 and cpu_data[-1] < cpu_data[0] - 20:
                patterns["gradual_decrease"] = True

            # Detect fluctuation (high variance)
            if np.std(cpu_data) > 20:
                patterns["fluctuation"] = True

        return patterns

    @staticmethod
    async def analyze(metrics: MetricData) -> AgentOutput:
        """Analyze metrics data for anomalies"""

        patterns = MetricsAgent.detect_anomaly_patterns(metrics)

        # Determine if anomaly exists
        is_anomaly = any(patterns.values())

        # Create description
        description_parts = []
        for pattern, detected in patterns.items():
            if detected:
                description_parts.append(pattern)

        if is_anomaly:
            description = f"Detected patterns: {', '.join(description_parts)} in metrics data"
        else:
            description = "No significant anomaly patterns detected in metrics"

        return AgentOutput(
            is_anomaly=is_anomaly,
            description=description,
            anomaly_category="metrics_analysis",
            anomaly_subtype=None,
            reason=description
        )


class LogAgent:
    """Slow Detection Agent for log analysis"""

    # Define keywords for different anomaly levels
    HIGH_SEVERITY_KEYWORDS = [
        "error", "failure", "crash", "panic", "fatal", "exception",
        "intrusion", "malware", "attack", "breach", "unauthorized",
        "exfiltration", "ransom", "backdoor", "rootkit", "ddos"
    ]

    MEDIUM_SEVERITY_KEYWORDS = [
        "warning", "timeout", "slow", "latency", "failed", "rejected",
        "suspicious", "unusual", "anomalous", "threshold", "exceeded"
    ]

    LOW_SEVERITY_KEYWORDS = [
        "info", "notice", "debug", "starting", "stopping", "completed",
        "scheduled", "backup", "rotation", "scan", "maintenance"
    ]

    @staticmethod
    def extract_anomaly_level(log_entries: List[LogEntry]) -> str:
        """Extract anomaly level from log entries"""
        high_count = 0
        medium_count = 0
        low_count = 0

        for entry in log_entries:
            message_lower = entry.message.lower()

            # Count keyword occurrences
            for keyword in LogAgent.HIGH_SEVERITY_KEYWORDS:
                if keyword in message_lower:
                    high_count += 1

            for keyword in LogAgent.MEDIUM_SEVERITY_KEYWORDS:
                if keyword in message_lower:
                    medium_count += 1

            for keyword in LogAgent.LOW_SEVERITY_KEYWORDS:
                if keyword in message_lower:
                    low_count += 1

        # Determine anomaly level
        if high_count >= 3:
            return "high"
        elif medium_count >= 5 or (high_count > 0 and medium_count > 0):
            return "medium"
        elif low_count > 0 or medium_count > 0:
            return "low"
        else:
            return "none"

    @staticmethod
    async def analyze(logs: LogData) -> AgentOutput:
        """Analyze log data for anomalies"""

        anomaly_level = LogAgent.extract_anomaly_level(logs.entries)

        # Summarize log behavior
        if len(logs.entries) > 0:
            time_range = f"{logs.entries[0].timestamp} to {logs.entries[-1].timestamp}"
        else:
            time_range = "no time range available"

        if anomaly_level != "none":
            description = f"Log analysis shows {anomaly_level} severity anomalies in time range {time_range}"
            is_anomaly = True
        else:
            description = f"No significant anomalies detected in logs from {time_range}"
            is_anomaly = False

        return AgentOutput(
            is_anomaly=is_anomaly,
            description=description,
            anomaly_category="log_analysis",
            anomaly_subtype=anomaly_level,
            reason=description
        )


class IntegratedAgent:
    """Integrated agent that combines metrics and log analysis"""

    # Mapping of patterns to anomaly scenarios
    SCENARIO_MAPPINGS = {
        ("spike", "high"): AnomalyScenario.CPU_HOG_PROCESS,
        ("gradual_increase", "high"): AnomalyScenario.MEMORY_LEAK,
        ("fluctuation", "medium"): AnomalyScenario.DISK_IO_BOTTLENECK,
        ("spike", "medium"): AnomalyScenario.NETWORK_ANOMALIES,
        # Add more mappings as needed
    }

    @staticmethod
    def correlate_evidence(metrics_output: AgentOutput, log_output: AgentOutput,
                           metrics_data: MetricData, log_data: LogData) -> AgentOutput:
        """Correlate evidence from metrics and logs"""

        # Extract patterns from descriptions
        metrics_desc = metrics_output.description.lower()
        log_desc = log_output.description.lower()

        # Determine if it's a true anomaly
        is_true_anomaly = False
        reason = ""
        anomaly_category = "none"
        anomaly_subtype = "none"

        # Rule 1: Both agents detect anomaly
        if metrics_output.is_anomaly and log_output.is_anomaly:
            # Check temporal correlation
            if "timeout" in log_desc and "spike" in metrics_desc:
                is_true_anomaly = True
                anomaly_category = "resource_exhaustion_and_bottleneck"
                anomaly_subtype = AnomalyScenario.CPU_HOG_PROCESS.value
                reason = "CPU spike correlated with timeout errors in logs indicates resource exhaustion"

        # Rule 2: Metrics anomaly with benign logs (possible false positive)
        elif metrics_output.is_anomaly and not log_output.is_anomaly:
            # Check if logs provide benign explanation
            if any(keyword in log_desc for keyword in ["backup", "maintenance", "scheduled"]):
                is_true_anomaly = False
                reason = "Metrics anomaly explained by scheduled maintenance activity in logs"
            else:
                is_true_anomaly = True
                anomaly_category = "subtle_anomaly"
                anomaly_subtype = AnomalyScenario.KERNEL_DRIVER_BUG.value
                reason = "Metrics anomaly without corresponding log entries suggests subtle system issue"

        # Rule 3: Log anomaly without metrics anomaly
        elif not metrics_output.is_anomaly and log_output.is_anomaly:
            if log_output.anomaly_subtype == "high":
                is_true_anomaly = True
                anomaly_category = "security_incident"
                anomaly_subtype = AnomalyScenario.DATA_EXFILTRATION.value
                reason = "High severity log anomalies detected without metric changes - possible security incident"
            else:
                is_true_anomaly = False
                reason = "Log anomalies are low severity and not reflected in system metrics"

        else:
            is_true_anomaly = False
            reason = "No anomalies detected by either metrics or log analysis"

        description = f"Integrated analysis: {reason}"

        return AgentOutput(
            is_anomaly=is_true_anomaly,
            description=description,
            anomaly_category=anomaly_category if is_true_anomaly else "none",
            anomaly_subtype=anomaly_subtype if is_true_anomaly else "none",
            reason=reason
        )

    @staticmethod
    async def analyze(metrics_output: AgentOutput, log_output: AgentOutput,
                      metrics_data: MetricData, log_data: LogData) -> AgentOutput:
        """Perform integrated analysis"""
        return await asyncio.to_thread(
            IntegratedAgent.correlate_evidence,
            metrics_output, log_output, metrics_data, log_data
        )


class SymbolicVerifier:
    """Symbolic verification module with rule-based checks"""

    @staticmethod
    def verify_metric_pattern(metrics: MetricData, scenario: str) -> bool:
        """Verify metric patterns against scenario rules"""

        if scenario == AnomalyScenario.CPU_HOG_PROCESS.value:
            # CPU Hog: sustained high CPU
            cpu_data = metrics.cpu
            if len(cpu_data) >= 30:
                high_cpu_count = sum(1 for cpu in cpu_data[-30:] if cpu > 85)
                return high_cpu_count >= 24
            return False

        elif scenario == AnomalyScenario.MEMORY_LEAK.value:
            # Memory leak: gradual memory increase
            mem_data = metrics.memory
            if len(mem_data) >= 20:
                trend = np.polyfit(range(20), mem_data[-20:], 1)[0]
                return trend > 0.3 and mem_data[-1] > 80

        elif scenario == AnomalyScenario.CRYPTOMINING_MALWARE.value:
            # Cryptomining: sustained high CPU and GPU
            cpu_high = sum(1 for cpu in metrics.cpu[-30:] if cpu > 85) >= 24
            if metrics.gpu:
                gpu_high = sum(1 for gpu in metrics.gpu[-30:] if gpu > 80) >= 20
                return cpu_high and gpu_high
            return cpu_high

        return False

    @staticmethod
    def verify_log_pattern(logs: LogData, scenario: str) -> bool:
        """Verify log patterns against scenario rules"""

        log_messages = [entry.message.lower() for entry in logs.entries]

        if scenario == AnomalyScenario.CPU_HOG_PROCESS.value:
            # CPU Hog: timeout errors
            timeout_keywords = ["timeout", "timed out", "response time exceeded"]
            return any(any(keyword in msg for keyword in timeout_keywords)
                       for msg in log_messages)

        elif scenario == AnomalyScenario.MEMORY_LEAK.value:
            # Memory leak: OOM killer or memory errors
            memory_keywords = ["oom", "out of memory", "memory allocation failed", "swap"]
            return any(any(keyword in msg for keyword in memory_keywords)
                       for msg in log_messages)

        elif scenario == AnomalyScenario.CRYPTOMINING_MALWARE.value:
            # Cryptomining: mining-related keywords
            mining_keywords = [
                "xmrig", "stratum", "nanopool", "miner", "mining",
                "crypto", "bitcoin", "ethereum", "hashrate", "pool"
            ]
            matches = sum(1 for msg in log_messages
                          if any(keyword in msg for keyword in mining_keywords))
            return matches >= 3

        elif scenario == AnomalyScenario.DATA_EXFILTRATION.value:
            # Data exfiltration: suspicious file access or network transfers
            exfil_keywords = [
                "shadow", "passwd", "credentials", "exfiltrate", "export",
                "sensitive", "confidential", "download large", "upload large",
                "unauthorized access", "file access"
            ]
            matches = sum(1 for msg in log_messages
                          if any(keyword in msg for keyword in exfil_keywords))
            return matches >= 2

        return False

    @staticmethod
    def verify(metrics: MetricData, logs: LogData,
               scenario: str) -> Tuple[bool, Dict[str, bool]]:
        """Perform symbolic verification"""

        if scenario == "none":
            return True, {"metric_check": True, "log_check": True}

        metric_check = SymbolicVerifier.verify_metric_pattern(metrics, scenario)
        log_check = SymbolicVerifier.verify_log_pattern(logs, scenario)

        is_verified = metric_check and log_check

        return is_verified, {
            "metric_check": metric_check,
            "log_check": log_check,
            "scenario": scenario
        }


class CloudAnoAgent:
    """Main CloudAnoAgent system"""

    def __init__(self):
        self.metrics_agent = MetricsAgent()
        self.log_agent = LogAgent()
        self.integrated_agent = IntegratedAgent()
        self.symbolic_verifier = SymbolicVerifier()

    async def detect(self, request: DetectionRequest) -> DetectionResponse:
        """Main detection pipeline"""
        start_time = datetime.now()

        # Step 1: Fast Detection (Metrics Agent)
        metrics_output = await self.metrics_agent.analyze(request.metrics)

        # Step 2: Slow Detection (Log Agent) - triggered by metrics anomaly
        log_output = await self.log_agent.analyze(request.logs)

        # Step 3: Integrated Analysis
        integrated_output = await self.integrated_agent.analyze(
            metrics_output, log_output, request.metrics, request.logs
        )

        # Step 4: Symbolic Verification (if enabled)
        symbolic_result = None
        final_decision = integrated_output

        if request.use_symbolic_verifier and integrated_output.is_anomaly:
            scenario = integrated_output.anomaly_subtype
            if scenario and scenario != "none":
                is_verified, verification_details = self.symbolic_verifier.verify(
                    request.metrics, request.logs, scenario
                )
                symbolic_result = {
                    "is_verified": is_verified,
                    "details": verification_details
                }

                # If symbolic verification fails, re-evaluate
                if not is_verified:
                    final_decision = AgentOutput(
                        is_anomaly=False,
                        description="Symbolic verification failed for detected anomaly",
                        anomaly_category="none",
                        anomaly_subtype="none",
                        reason=f"Symbolic checks failed for scenario {scenario}"
                    )

        # Calculate processing time
        processing_time_ms = (datetime.now() - start_time).total_seconds() * 1000

        return DetectionResponse(
            metrics_agent_output=metrics_output,
            log_agent_output=log_output,
            integrated_agent_output=integrated_output,
            symbolic_verification_result=symbolic_result,
            final_decision=final_decision,
            processing_time_ms=processing_time_ms
        )


# ============= FastAPI Application =============
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources"""
    app.state.agent = CloudAnoAgent()
    print("CloudAnoAgent initialized")
    yield
    print("CloudAnoAgent shutdown")


app = FastAPI(
    title="CloudAnoAgent API",
    description="LLM-based Agent for Cloud Anomaly Detection with Symbolic Verification",
    version="1.0.0",
    lifespan=lifespan
)


@app.post("/detect", response_model=DetectionResponse)
async def detect_anomaly(request: DetectionRequest):
    """Main endpoint for anomaly detection"""
    try:
        agent = app.state.agent
        response = await agent.detect(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/detect/upload")
async def detect_from_upload(
        metrics_file: UploadFile = File(...),
        logs_file: UploadFile = File(...),
        use_symbolic_verifier: bool = Form(True)
):
    """Endpoint for file upload detection"""
    try:
        # Parse metrics CSV
        metrics_content = await metrics_file.read()
        metrics_df = pd.read_csv(pd.io.common.BytesIO(metrics_content))

        # Parse logs file
        logs_content = await logs_file.read()
        logs_text = logs_content.decode('utf-8')

        # Convert to expected format
        metrics = MetricData(
            timestamp=metrics_df.get('timestamp', []).tolist(),
            cpu=metrics_df.get('cpu', []).fillna(0).tolist(),
            memory=metrics_df.get('memory', []).fillna(0).tolist(),
            disk_io=metrics_df.get('disk_io', []).fillna(0).tolist(),
            net_in=metrics_df.get('net_in', []).fillna(0).tolist(),
            net_out=metrics_df.get('net_out', []).fillna(0).tolist(),
            gpu=metrics_df.get('gpu', []).fillna(0).tolist() if 'gpu' in metrics_df else None
        )

        # Parse log entries (simplified)
        log_entries = []
        for line in logs_text.split('\n'):
            if line.strip():
                # Simple parsing - adjust based on your log format
                parts = line.split(' ', 3)
                if len(parts) >= 4:
                    timestamp = f"{parts[0]} {parts[1]}"
                    source = parts[2].strip('[]')
                    message = parts[3]
                    log_entries.append(LogEntry(
                        timestamp=timestamp,
                        message=message,
                        source=source
                    ))

        logs = LogData(entries=log_entries)

        # Create request
        request = DetectionRequest(
            metrics=metrics,
            logs=logs,
            use_symbolic_verifier=use_symbolic_verifier
        )

        # Detect anomalies
        agent = app.state.agent
        response = await agent.detect(request)

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")


@app.get("/scenarios")
async def list_scenarios():
    """List all available anomaly scenarios"""
    return {
        "scenarios": [scenario.value for scenario in AnomalyScenario],
        "categories": {
            "resource_exhaustion_and_bottlenecks": [
                AnomalyScenario.CPU_HOG_PROCESS.value,
                AnomalyScenario.MEMORY_LEAK.value,
                AnomalyScenario.DISK_IO_BOTTLENECK.value,
                AnomalyScenario.NOISY_NEIGHBOR.value,
                AnomalyScenario.HANDLE_THREAD_EXHAUSTION.value
            ],
            "network_anomalies": [
                AnomalyScenario.HIGH_NETWORK_LATENCY.value,
                AnomalyScenario.BANDWIDTH_SATURATION.value,
                AnomalyScenario.DNS_RESOLUTION_FAILURE.value,
                AnomalyScenario.FIREWALL_MISCONFIGURATION.value
            ],
            "software_application_anomalies": [
                AnomalyScenario.APPLICATION_CRASH_LOOP.value,
                AnomalyScenario.DEADLOCK_LIVELOCK.value,
                AnomalyScenario.EXTERNAL_DEPENDENCY_FAILURE.value,
                AnomalyScenario.APPLICATION_MISCONFIGURATION.value,
                AnomalyScenario.GC_STORM.value
            ],
            "malicious_events": [
                AnomalyScenario.CRYPTOMINING_MALWARE.value,
                AnomalyScenario.DDOS_BOTNET_AGENT.value,
                AnomalyScenario.RANSOMWARE.value,
                AnomalyScenario.DATA_EXFILTRATION.value,
                AnomalyScenario.SPAM_BOT.value,
                AnomalyScenario.ROOTKIT_BACKDOOR.value,
                AnomalyScenario.BRUTE_FORCE_ATTACK.value,
                AnomalyScenario.WEB_SHELL.value,
                AnomalyScenario.PASSWORD_CRACKING.value,
                AnomalyScenario.LOG_TAMPERING.value,
                AnomalyScenario.REVERSE_SHELL.value,
                AnomalyScenario.APPLICATION_LAYER_DDOS.value
            ],
            "other_complex_anomalies": [
                AnomalyScenario.TIME_SKEW.value,
                AnomalyScenario.KERNEL_DRIVER_BUG.value
            ]
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "CloudAnoAgent",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)