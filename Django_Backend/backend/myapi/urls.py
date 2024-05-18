from django.urls import path
from .views import customerAttention, customerTest, get_ads, health_check

urlpatterns = [
    path("recieveCustomer/", customerTest), # http://127.0.0.1:8000/api/recieveCustomer/
    path("recieveAttention/", customerAttention), # http://127.0.0.1:8000/api/recieveCustomer/
    path("getAdvertise/", get_ads), # http://127.0.0.1:8000/api/getAdvertise/
    path("health/", health_check) # http://127.0.0.1:8000/api/health
]
