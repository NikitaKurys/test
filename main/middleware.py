from django.shortcuts import redirect
from django.urls import reverse


class RedirectAfterLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated and request.user.is_staff:
            if request.path == reverse('admin:login'):
                return redirect(reverse('admin:main_maintable_add'))

        return response
