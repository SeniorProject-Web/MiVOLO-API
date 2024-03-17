from django.urls import path
from .views import getCustomer, predictCustomer

urlpatterns = [
    path("getCustomer/", getCustomer), # http://127.0.0.1:8000/api/getCustomer/
    path("recieveCustomer/", predictCustomer), # http://127.0.0.1:8000/api/recieveCustomer/
]
