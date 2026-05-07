from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

class LoginRequiredMixinWithMessage(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "Для оформления заказа войдите в систему")
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)