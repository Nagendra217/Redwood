"""redwood URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from redwood.views import *
from financials.views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', HomeView.as_view(), name="home"),
    url(r'^login', LoginView.as_view(), name="account_login"),
    url(r'^logout', LogoutView.as_view(), name="account_logout"),
    url(r'^dashboard', login_required(DashboardView.as_view()), name="dashboard"),
    url(r'^portfolio', login_required(PortfolioView.as_view()), name="portfolio"),
    url(r'^orders', login_required(OrdersView.as_view()), name="order_book"),
    url(r'^profile', login_required(ProfileView.as_view()), name="profile"),
	url(r'^json/values', login_required(ProfileValues.as_view()), name="values"),
	url(r'^json/performace', login_required(Performance.as_view()), name="performance"),
    url(r'^json/portfolio', login_required(Portfolio.as_view()), name="portfolio"),
    url(r'^json/orders', login_required(Orders.as_view()), name="order"),
    url(r'^json/profile', login_required(UserProfile.as_view()), name="order"),

]
