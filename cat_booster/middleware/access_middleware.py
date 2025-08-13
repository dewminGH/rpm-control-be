from utils.helpers import validate_exception_response_403_json

class AccessMiddleware:
    """
    Access verify
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        api_key =request.headers.get("x-api-key")
        if api_key != "123":
            return validate_exception_response_403_json()
        response = self.get_response(request)
        return response
