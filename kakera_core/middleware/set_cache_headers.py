from django.utils.cache import patch_cache_control

def set_cache_headers(get_response):
    def middleware(request):
        response = get_response(request)

        # Lower the duration of the browser's cache below the server's.
        # We can clear the server's cache, not the client's.
        patch_cache_control(response, max_age=10*60)

        return response

    return middleware
