import time
from collections import deque

from app.logger import get_logger

logger = get_logger("metrics")

class MetricsTracker:
    """
    Tracks application metrics and detects anomalies.
    """

    def __init__(self):
        # store recent response times (last 100 requests)
        # deque = a list with a max size — old items fall off automatically
        self.response_time = deque(maxlen=100)

        #count errors in a sliding window
        self.recent_errors = deque(maxlen=100)

        # Count failed logins (for detecting brute force attacks)
        self.failed_logins = deque(maxlen=100)

        # track if model service is reachable
        self.model_service_healthy = True
        self.model_service_failures = 0

        # alert thresholds
        self.SLOW_REQUEST_THRESHOLD = 30.0    # seconds
        self.ERROR_RATE_THRESHOLD = 5         # errors in window
        self.FAILED_LOGIN_THRESHOLD = 10      # failed attempts
        self.MODEL_FAILURE_THRESHOLD = 3      # consecutive failures

        self.active_alerts = set()

    def record_request(self, endpoint: str, duration: float, status_code: int):
        """
        Record a completed request
        Called by the middleware after every request
        """
        self.response_time.append({
            "endpoint": endpoint,
            "duration": duration,
            "status_code": status_code,
            "timestamp": time.time()
        })

        #check for slow requests
        if duration > self.SLOW_REQUEST_THRESHOLD:
            self._trigger_alert(
                "slow_request",
                f"Slow request detected: {endpoint} took {duration:.1f}s"
                f" (threshold: {self.SLOW_REQUEST_THRESHOLD}s)"
            )
        
        # record errors
        if status_code >= 500:
            self.recent_errors.append(time.time())
            self._check_error_rate()
    
    def record_failed_login(self, username: str):
        """Record a failed login attempt"""
        self.failed_logins.append({
            "username": username,
            "timestamp": time.time()
        })
        self._check_login_attacks()

    def record_model_service_failure(self):
        """Record when model service is unreachable"""
        self.model_service_failures += 1
        self.model_service_healthy = False

        if self.model_service_failures >= self.MODEL_FAILURE_THRESHOLD:
            self._trigger_alert(
                "model_service_down",
                f"Model service is DOWN - {self.model_service_failures} "
                f"consecutive failures"
            )
    
    def record_model_service_success(self):
        """Record when model service responds successfully"""
        if not self.model_service_healthy:
            logger.info("Model service recovered - back online")
            self.active_alerts.discard("model_service_down")

        self.model_service_failures = 0
        self.model_service_healthy = True
    
    def _check_error_rate(self):
        """Check if we're getting too many errors"""
        # count errors in the last 60 seconds
        cutoff = time.time() - 60
        recent = [t for t in self.recent_errors if t > cutoff]

        if len(recent) >= self.ERROR_RATE_THRESHOLD:
            self._trigger_alert(
                "high_error_rate",
                f"High error rate: {len(recent)} server errors in the last 60s"
            )

    def _check_login_attacks(self):
        """Check for potential brute force login attempts"""
        # count failed logins in the last 5 minutes
        cutoff = time.time() - 300
        recent = [f for f in self.failed_logins if f["timestamp"] > cutoff]

        if len(recent) >= self.FAILED_LOGIN_THRESHOLD:
            username = set(f["username"] for f in recent)
            self._trigger_alert(
                "login_attack",
                f"Possible brute force attack: {len(recent)} failed logins "
                f"in 5 minutes - usernames targeted: {username}"
            )
    
    def _trigger_alert(self, alert_id: str, message: str):
        """
        Trigger an alert. Only fires once per alert type
        until the condition clears (prevents alert spam).
        """
        if alert_id not in self.active_alerts:
            self.active_alerts.add(alert_id)
            logger.critical(f"ALERT [{alert_id}]: {message}")
            # This is where we'll add email/Slack notifications later
            send_alert(alert_id, message)

    def get_status(self):
        """Return current metrics — useful for a monitoring dashboard"""
        recent_times = [r["duration"] for r in self.response_time]

        return {
            "total_tracked_requests": len(self.response_time),
            "avg_response_time": round(
                sum(recent_times) / len(recent_times), 2
            ) if recent_times else 0,
            "max_response_time": round(max(recent_times), 2) if recent_times else 0,
            "model_service_healthy": self.model_service_healthy,
            "active_alerts": list(self.active_alerts),
            "recent_error_count": len([
                t for t in self.recent_errors if t > time.time() - 60
            ])
        }

def send_alert(alert_id: str, message: str):
    """
    Send alert notifications via email and logs
    """
    from app.alerts import send_email_alert
    logger.critical(f"NOTIFICATION: {message}")
    send_email_alert(alert_id, message)

# single global instance — shared across the whole app
metrics = MetricsTracker()