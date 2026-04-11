import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.logger import get_logger
from app.metrics import metrics

logger = get_logger("middleware")

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that runs on EVERY request.

    Flow: Request → Middleware → Your Endpoint → Middleware → Response
    """
    
    async def dispatch(self, request: Request, call_next):

        # record start time
        start_time = time.time()

        # get request info
        method = request.method
        path = request.url.path

        # skip logging for health ckecks
        if path == "/health":
            return await call_next(request)
        
        # log the incoming request
        logger.info(f"-> {method} {path}")

        # call the actual endpoint
        try:
            response = await call_next(request)
        except Exception as e:
            #log unhandled errors
            duration = time.time() - start_time
            logger.error(f"[ERROR] {method} {path} - unhandled error: {str(e)} ({duration:.2f}s)")
            metrics.record_request(path, duration, 500)
            raise

        # calculate how long the request took
        duration = time.time() - start_time

        # record in metrics
        metrics.record_request(path, duration, response.status_code)

        # log the response with status
        if response.status_code >= 500:
            logger.error(f"[ERROR] {method} {path} - {response.status_code} ({duration:.2f}s)")
        elif response.status_code >= 400:
            logger.warning(f"[WARN] {method} {path} - {response.status_code} ({duration:.2f}s)")
        else:
            logger.info(f"[OK] {method} {path} - {response.status_code} ({duration:.2f}s)")
            
        return response