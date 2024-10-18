from django.shortcuts import redirect
from django.urls import reverse

class RedirectUnauthenticatedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Sprawdź, czy użytkownik jest zalogowany
        if not request.user.is_authenticated:
            # Sprawdź, czy użytkownik próbuje uzyskać dostęp do chronionej strony
            if request.path not in [reverse('login'), reverse('register_user')]:
                return redirect('login')  # Przekierowanie do strony logowania

        response = self.get_response(request)
        return response
