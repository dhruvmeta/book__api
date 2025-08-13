from django.conf import settings
from django.http import JsonResponse
from functools import wraps

def require_api_key(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        #  Add this debug print
        print("DEBUG: Incoming headers ->", dict(request.headers))

        key = request.headers.get('X-API-Key')  # Correct casing!
        print("DEBUG: API Key received ->", key)

        if key and key in settings.VALID_API_KEYS:
            return view_func(request, *args, **kwargs)

        return JsonResponse({
            'error': 'INVALID_API_KEY',
            'message': 'Missing or invalid API key'
        }, status=401)
    return wrapper
