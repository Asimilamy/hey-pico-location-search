"""
Rate limiting middleware for FastAPI
Implements per-IP request throttling to prevent API abuse
"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from datetime import datetime, timedelta
from typing import Dict, Tuple
from .config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce rate limiting per client IP
    
    Tracks requests per minute and rejects excess requests
    """
    
    def __init__(self, app):
        super().__init__(app)
        # Store: {ip: (request_count, window_start_time)}
        self.request_history: Dict[str, Tuple[int, datetime]] = {}
    
    async def dispatch(self, request: Request, call_next):
        """Check rate limit before processing request"""
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for health checks
        if request.url.path == "/health":
            return await call_next(request)
        
        # Get current time
        now = datetime.now()
        rate_limit = settings.rate_limit_per_minute
        time_window = timedelta(minutes=1)
        
        # Check if IP has made requests before
        if client_ip in self.request_history:
            count, window_start = self.request_history[client_ip]
            
            # Check if we're still in the same time window
            if now - window_start < time_window:
                # Still in same window
                if count >= rate_limit:
                    # Rate limit exceeded
                    return JSONResponse(
                        status_code=429,
                        content={
                            "detail": f"Rate limit exceeded. Max {rate_limit} requests per minute.",
                            "retry_after": int((window_start + time_window - now).total_seconds()) + 1
                        },
                        headers={"Retry-After": str(int((window_start + time_window - now).total_seconds()) + 1)}
                    )
                
                # Increment counter
                self.request_history[client_ip] = (count + 1, window_start)
            else:
                # Window expired, start new one
                self.request_history[client_ip] = (1, now)
        else:
            # First request from this IP
            self.request_history[client_ip] = (1, now)
        
        # Clean up old entries (optional, prevents memory issues)
        self._cleanup_old_entries(now, time_window)
        
        # Process the request
        response = await call_next(request)
        
        # Add rate limit headers to response
        remaining = rate_limit - self.request_history[client_ip][0]
        window_reset = self.request_history[client_ip][1] + time_window
        
        response.headers["X-RateLimit-Limit"] = str(rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Reset"] = str(int(window_reset.timestamp()))
        
        return response
    
    def _cleanup_old_entries(self, now: datetime, time_window: timedelta):
        """Remove expired entries from request history to prevent memory bloat"""
        expired_ips = [
            ip for ip, (_, window_start) in self.request_history.items()
            if now - window_start > time_window * 2  # Keep history for 2 minutes for safety
        ]
        
        for ip in expired_ips:
            del self.request_history[ip]
