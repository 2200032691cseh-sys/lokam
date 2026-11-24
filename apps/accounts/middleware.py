from django.contrib.auth import logout

SESSION_GENERATION_KEY = "lokam_session_generation"


def enforce_session_generation(get_response):
    def middleware(request):
        if request.user.is_authenticated and (
            request.session.get(SESSION_GENERATION_KEY)
            != request.user.session_generation
        ):
            logout(request)
        return get_response(request)

    return middleware
