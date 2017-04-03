from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.generic import View, TemplateView
from django.http import JsonResponse, Http404, HttpResponseRedirect, HttpResponse
from django.contrib import auth
from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse

class HomeView(TemplateView):

    def get(self, request, *args, **kwargs):
        template_name = "index.html"
        response = render_to_response(
            template_name, {}, RequestContext(request))
        return response

class LogoutView(TemplateView):

    def get(self, request, *args, **kwargs):
    	auth.logout(request)
        response = HttpResponseRedirect(reverse('home'))
        return response

class LoginView(View):

    def get(self, request, *args, **kwargs):
        template_name = "login.html"
        if request.user.is_authenticated():
        	response = HttpResponseRedirect(reverse('dashboard'))
        else:
        	response = render_to_response(
            	template_name, {}, RequestContext(request))
        return response

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        print username,password
        if username and password:
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                print request.user
                data = {"url": reverse('dashboard')}
            else:
                data = {"message": "Invalid login details."}
        else:
            data = {'message': "Invalid information."}
        return JsonResponse(data, safe=False)

class DashboardView(TemplateView):

    def get(self, request, *args, **kwargs):
        template_name = "dashboard.html"
        response = render_to_response(
            template_name, {}, RequestContext(request))
        return response


class PortfolioView(TemplateView):

    def get(self, request, *args, **kwargs):
        template_name = "portfolio.html"
        response = render_to_response(
            template_name, {}, RequestContext(request))
        return response


class OrdersView(TemplateView):

    def get(self, request, *args, **kwargs):
        template_name = "orders.html"
        response = render_to_response(
            template_name, {}, RequestContext(request))
        return response



class ProfileView(TemplateView):

    def get(self, request, *args, **kwargs):
        template_name = "profile.html"
        response = render_to_response(
            template_name, {}, RequestContext(request))
        return response

	
