from typing import Any
from django import http
from django.shortcuts import render, redirect
# from django.views.generic import TemplateView
import requests
from django.views import View
from django.http import Http404
from cms_app.models import *
from cms_app.serializers import *
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.contrib.auth import login

# Create your views here.

class LoginView(View):
    template_name = 'index.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        api_url = 'http://127.0.0.1:8000/api/login/'
        response = requests.post(api_url, data={
            'username' : username,
            'password' : password
        })

        if response.status_code == 200:
            data = response.json()
            token = data['token']
            user_id = data['user_id']

            user = BaseUser.objects.get(user_id = user_id)
            login(request, user)

            request.session['token'] = token
            return redirect('index')
        else:
            error_message  =response.json().get('error', 'Invalid Credentials')
            return render(request, self.template_name, {'error' : error_message})
        
# login_view = LoginView.as_view()

class Logout(LogoutView):
    next_page = reverse_lazy('index')

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class index(View):
    template_name = 'index.html'
    api_endpoint = 'http://127.0.0.1:8000/api/blogs'

    def get(self, request):
        response = requests.get(self.api_endpoint)

        if response.status_code == 200:
            api_data = response.json()
            context = {
                'api_data': api_data
            }

            return render(request, self.template_name, context)
        
        else:
            raise Http404


class ViewMore(View):
    template_name = 'view_more.html'

    def get(self, request, id):
        try:
            obj = Blog.objects.get(post_id = id)
        except Blog.DoesNotExist:
            return render(request, self.template_name, {'error' : 'Object not found'})

        serializer = BlogSerializer(obj)
        context = {
            'api_data' : serializer.data
        }

        return render(request, self.template_name, context)