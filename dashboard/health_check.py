# dashboard/health_check.py
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
import sys

@csrf_exempt
@never_cache
def health_check(request):
    """
    Health check endpoint for monitoring and load balancing.
    """
    health_status = {
        "status": "healthy",
        "checks": {}
    }
    
    status_code = 200
    
    # Check 1: Database connectivity
    try:
        connection.ensure_connection()
        health_status["checks"]["database"] = "connected"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
        status_code = 503
    
    # Check 2: Python runtime
    try:
        health_status["checks"]["python_version"] = sys.version.split()[0]
    except Exception as e:
        health_status["checks"]["python"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
        status_code = 503
    
    health_status["version"] = "1.0.0"
    
    return JsonResponse(health_status, status=status_code)