import time
import logging

logger = logging.getLogger("pydataui.request")

class RequestLogger:
    def __init__(self, app_config=None):
        self.enabled = True
        self.format = "[{method}] {path} → {status} ({time}ms)"
    
    def log(self, method, path, status, duration_ms):
        if not self.enabled:
            return
        
        msg = self.format.format(
            method=method,
            path=path,
            status=status,
            time=f"{duration_ms:.2f}"
        )
        logger.info(msg)

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return
            
        start_time = time.time()
        method = scope["method"]
        path = scope["path"]
        
        status_code = [500] # Use list to pass by reference to inner function
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_code[0] = message["status"]
            await send(message)
            
        try:
            # We would normally call the next app here, but since this is just the middleware structure:
            pass
        finally:
            duration = (time.time() - start_time) * 1000
            self.log(method, path, status_code[0], duration)
