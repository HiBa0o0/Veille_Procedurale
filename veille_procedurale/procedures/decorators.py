from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def quality_cell_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or not request.user.profile.is_quality_cell():
            messages.error(request, "Accès réservé aux membres de la cellule qualité.")
            return redirect('procedures:my_procedures')
        return view_func(request, *args, **kwargs)
    return _wrapped_view