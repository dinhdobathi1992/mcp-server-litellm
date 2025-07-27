#!/usr/bin/env python3
"""
Performance configuration for the LiteLLM MCP server.

This file contains various performance tuning options that can be adjusted
to optimize response speed and throughput.
"""

import os
from typing import Dict, Any

# HTTP Client Performance Settings
HTTP_TIMEOUT = float(os.environ.get("HTTP_TIMEOUT", "30.0"))
HTTP_CONNECT_TIMEOUT = float(os.environ.get("HTTP_CONNECT_TIMEOUT", "10.0"))
HTTP_MAX_KEEPALIVE_CONNECTIONS = int(os.environ.get("HTTP_MAX_KEEPALIVE_CONNECTIONS", "20"))
HTTP_MAX_CONNECTIONS = int(os.environ.get("HTTP_MAX_CONNECTIONS", "100"))
HTTP_ENABLE_HTTP2 = os.environ.get("HTTP_ENABLE_HTTP2", "true").lower() == "true"

# LiteLLM Performance Settings
LITELLM_REQUEST_TIMEOUT = float(os.environ.get("LITELLM_REQUEST_TIMEOUT", "60.0"))
LITELLM_MAX_RETRIES = int(os.environ.get("LITELLM_MAX_RETRIES", "3"))
LITELLM_RETRY_DELAY = float(os.environ.get("LITELLM_RETRY_DELAY", "1.0"))

# Model-Specific Performance Settings
MODEL_PERFORMANCE_CONFIG = {
    "gpt-4o": {
        "default_max_tokens": 1000,
        "default_temperature": 0.7,
        "enable_streaming": True,
        "preferred_timeout": 45.0,
    },
    "anthropic.claude-3-7-sonnet-20250219-v1:0": {
        "default_max_tokens": 1000,
        "default_temperature": 0.7,
        "enable_streaming": True,
        "preferred_timeout": 60.0,
    }
}

# Caching Settings (for future implementation)
ENABLE_RESPONSE_CACHING = os.environ.get("ENABLE_RESPONSE_CACHING", "false").lower() == "true"
CACHE_TTL_SECONDS = int(os.environ.get("CACHE_TTL_SECONDS", "300"))  # 5 minutes
CACHE_MAX_SIZE = int(os.environ.get("CACHE_MAX_SIZE", "1000"))

# Logging Performance Settings
LOG_PERFORMANCE_METRICS = os.environ.get("LOG_PERFORMANCE_METRICS", "true").lower() == "true"
LOG_SLOW_QUERIES_THRESHOLD = float(os.environ.get("LOG_SLOW_QUERIES_THRESHOLD", "5.0"))  # seconds

# Connection Pool Settings
CONNECTION_POOL_SETTINGS = {
    "timeout": HTTP_TIMEOUT,
    "connect_timeout": HTTP_CONNECT_TIMEOUT,
    "max_keepalive_connections": HTTP_MAX_KEEPALIVE_CONNECTIONS,
    "max_connections": HTTP_MAX_CONNECTIONS,
    "http2": HTTP_ENABLE_HTTP2,
}

def get_model_config(model: str) -> Dict[str, Any]:
    """
    Get performance configuration for a specific model.
    
    Args:
        model: The model name
        
    Returns:
        Dictionary containing model-specific performance settings
    """
    return MODEL_PERFORMANCE_CONFIG.get(model, {
        "default_max_tokens": 1000,
        "default_temperature": 0.7,
        "enable_streaming": True,
        "preferred_timeout": 60.0,
    })

def get_optimized_completion_params(model: str, **kwargs) -> Dict[str, Any]:
    """
    Get optimized completion parameters for a model.
    
    Args:
        model: The model name
        **kwargs: Additional parameters to override defaults
        
    Returns:
        Dictionary of optimized completion parameters
    """
    model_config = get_model_config(model)
    
    # Start with model-specific defaults
    params = {
        "max_tokens": kwargs.get("max_tokens", model_config["default_max_tokens"]),
        "temperature": kwargs.get("temperature", model_config["default_temperature"]),
        "stream": kwargs.get("stream", model_config["enable_streaming"]),
    }
    
    # Add any additional parameters
    for key, value in kwargs.items():
        if key not in params:
            params[key] = value
    
    return params

def should_log_performance(start_time: float, end_time: float) -> bool:
    """
    Determine if a request should be logged for performance monitoring.
    
    Args:
        start_time: Request start time
        end_time: Request end time
        
    Returns:
        True if the request should be logged
    """
    if not LOG_PERFORMANCE_METRICS:
        return False
    
    duration = end_time - start_time
    return duration > LOG_SLOW_QUERIES_THRESHOLD

# Performance monitoring utilities
class PerformanceMonitor:
    """Utility class for monitoring and logging performance metrics."""
    
    def __init__(self):
        self.request_count = 0
        self.total_response_time = 0.0
        self.slow_requests = 0
        
    def record_request(self, duration: float):
        """Record a request duration."""
        self.request_count += 1
        self.total_response_time += duration
        
        if duration > LOG_SLOW_QUERIES_THRESHOLD:
            self.slow_requests += 1
    
    def get_average_response_time(self) -> float:
        """Get average response time."""
        if self.request_count == 0:
            return 0.0
        return self.total_response_time / self.request_count
    
    def get_slow_request_percentage(self) -> float:
        """Get percentage of slow requests."""
        if self.request_count == 0:
            return 0.0
        return (self.slow_requests / self.request_count) * 100

# Global performance monitor instance
performance_monitor = PerformanceMonitor() 