from django.urls import path
from . import views

# Dynamic fallback to catch whichever view function exists in views.py
view_func = getattr(views, "create_client", getattr(views, "client_create", None))

urlpatterns = [
    path("", getattr(views, "client_list", lambda r: None), name="client_list"),
    path("add/", view_func, name="client_create"),
    path("create/", view_func, name="client_create_alias"),
    path("<int:pk>/", getattr(views, "client_detail", lambda r: None), name="client_detail"),
]

