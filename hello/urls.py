# The urls.py file is where you specify patterns to route different URLs to their appropriate views.
# The code below contains one route to
# map root URL of the app ("") to the views.home function that you just added to hello/views.py:

from django.urls import path
from hello import views

urlpatterns = [
    path("", views.home, name="home"),
    path("api/scrape-text/", views.scrape_text, name="scrape-text"),
]