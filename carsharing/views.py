import asyncio
from datetime import datetime
from time import sleep

from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
import folium

from carsharing.forms import RegisterForm, LoginForm, DocumentForm
from carsharing.models import Car, CATEGORIES, Document, Order

from carsharing.map import get_route, is_too_far_away

WS_DATA = dict()


def sync_gps(request):
    address = request.GET.get("gps_mac_address", None)
    if WS_DATA.get(address):
        WS_DATA[address]["coord"] = request.GET.get("coord", None)
    return HttpResponse("Ok")


def create_order(request, car_state_number: str):
    car = get_object_or_404(Car, state_number=car_state_number)
    if hasattr(request.user, 'order'):
        request.user.order.delete()
    request.user.order = Order.objects.create(
        car=car, user=request.user, driving_start=datetime.now()
    )
    return HttpResponseRedirect("/map")


class LoginView(TemplateView):
    template_name = "auth.html"

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect("/")
            form.add_error("username", 'Вы ввели неверный логин или пароль')
        return render(request, self.template_name, {"errors": form.errors})


class RegisterView(TemplateView):
    template_name = "auth.html"

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            password = data.pop("password")

            user = User.objects.create_user(**data)
            user.set_password(password)

            user.save()
            login(request, user)
            return HttpResponseRedirect("/")
        return render(request, self.template_name, {"errors": form.errors})


class ProfileView(TemplateView, LoginRequiredMixin):
    template_name = "profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['driving_categories'] = CATEGORIES
        return context

    def post(self, request):
        form = DocumentForm(request.POST)
        if form.is_valid():
            document = request.user.document if hasattr(request.user, 'document') else Document(user=request.user)

            for key, value in form.cleaned_data.items():
                setattr(document, key, value)

            document.approved = False
            document.save()
        return HttpResponseRedirect("/lk/")


class MainView(LoginRequiredMixin, TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cars'] = Car.objects.all()
        return context


def show_map(request):
    return render(request, 'map.html')


@login_required
def show_route(request, lat1, long1, lat2, long2):
    if not hasattr(request.user, 'order'):
        return HttpResponseRedirect("/")
    figure = folium.Figure()
    lat1, long1, lat2, long2 = float(lat1), float(long1), float(lat2), float(long2)

    lines, route = get_route(long1, lat1, long2, lat2)
    WS_DATA[str(request.user.order.car.gps_mac_address)] = {
        "coord": [lat1, long1],
        "lines": lines
    }

    m = folium.Map(location=[(route['start_point'][0]),
                             (route['start_point'][1])],
                   zoom_start=10)

    m.add_to(figure)

    folium.PolyLine(route['route'], weight=8, color='blue', opacity=0.6).add_to(m)
    folium.Marker(location=route['start_point'], icon=(icon := folium.Icon(icon='play', color='green'))).add_to(m)
    folium.Marker(location=route['end_point'], icon=folium.Icon(icon='stop', color='red')).add_to(m)
    figure.render()

    context = {'map': figure, 'map_name': m.get_name(), 'icon_name': icon.get_name()}
    return render(request, 'route.html', context)


class WebsocketView(AsyncWebsocketConsumer):

    async def auth(self, cookie) -> str | None:
        cookie = cookie.decode()

        for name in cookie.split('; '):
            if "sessionid" in name:
                session_key = name.split('=')[1]
                break
        else:
            return None

        session = SessionStore(session_key=session_key)
        if not await session.aexists(session_key):
            return None
        session_data = await session.aload()

        try:
            user: User = await User.objects.prefetch_related(
                "order__car",
            ).aget(id=int(session_data.get('_auth_user_id', 0)))
        except User.DoesNotExist:
            return None
        return str(user.order.car.gps_mac_address)

    async def connect(self):
        auth_headers = [header[1] for header in self.scope['headers'] if b'cookie' in header]
        if not auth_headers:
            return None
        if not (_id := await self.auth(auth_headers[0])):
            return None
        if _id not in WS_DATA:
            return None
        self.data = WS_DATA[_id]
        await self.accept()

    async def disconnect(self, close_code):
        ...

    async def receive(self, text_data):
        self.data["coord"] = [self.data["coord"][0], self.data["coord"][1]]
        if is_too_far_away(self.data['lines'], self.data["coord"]):
            return await self.disconnect(1004)
        sleep(1)
        await self.send(str(self.data["coord"]))
