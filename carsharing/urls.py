from django.contrib.auth.views import LogoutView
from django.urls import path
from carsharing.views import (
    LoginView, RegisterView, MainView, ProfileView, show_route, show_map, WebsocketView, sync_gps, create_order
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('register/', RegisterView.as_view(), name='register'),
    path('lk/', ProfileView.as_view(), name='lk'),
    path('map/<str:lat1>,<str:long1>,<str:lat2>,<str:long2>', show_route, name='route'),
    path('map/', show_map, name='map'),
    path('gps/', sync_gps, name='gps'),
    path('order/<str:car_state_number>', create_order, name="order"),
    path('', MainView.as_view(), name='main'),
]

websocket_urlpatterns = [
    path('map/', WebsocketView.as_asgi())
]
