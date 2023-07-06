from django.shortcuts import render
from rest_framework.views import APIView
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import BasePermission
from django.contrib.auth.hashers import make_password
from django.http import Http404
from django.db.models import Q
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

# Create your views here.

class AccessPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        elif request.user.is_authenticated:
            return True
        else:
            return False
        
class LoginAPI(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username = username, password = password)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        else:
            return Response({'error': 'Invalid Credentials'}, status=401)


class BaseUserView(APIView):

    # permission_classes = (AccessPermission, )

    def get(self, request):
        user_objs = BaseUser.objects.all()
        serializer = BaseUserSerializer(user_objs, many = True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = BaseUserSerializer(data = request.data)
        if serializer.is_valid():
            password = make_password(self.request.data["password"])
            serializer.save(password=password)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class BaseUserDetail(APIView):

    permission_classes = (AccessPermission, )

    def get_object(self, uuid):

        try:
            return BaseUser.objects.get(user_id = uuid)
        except BaseUser.DoesNotExist:
            return None
        
    def get(self, request, uuid):
        user_obj = self.get_object(uuid)

        if user_obj is None:
            return Response({
                'message' : 'User does not exist',
                'status': 400
            })
        
        serializer = BaseUserSerializer(user_obj)
        return Response(serializer.data)
    
    def put(self, request, uuid):
        user_obj = self.get_object(uuid)
        if user_obj is None:
            return Response("User does not exist.", status=status.HTTP_404_NOT_FOUND)
        
        if user_obj.user_id != request.user.user_id:
            return Response({'error' : 'You are not able to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = BaseUserSerializer(user_obj, data = request.data, partial = True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, uuid):
        user_obj = self.get_object(uuid)

        if user_obj.user_id != request.user.user_id:
            return Response({'error' : 'You are not able to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        if user_obj is None:
            return Response("User does not exist.", status=status.HTTP_404_NOT_FOUND)

        user_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class BlogView(APIView):
    
    permission_classes = (AccessPermission, )

    def get(self, request):
        if request.user.is_authenticated:
            blog_objs = Blog.objects.filter(Q(is_public = True) | Q(owner = request.user))
        else:
            blog_objs = Blog.objects.filter(is_public = True)

        serializer = BlogSerializer(blog_objs, many = True)
        return Response(serializer.data)
    
    def post(self, request):
        request_data = request.data.copy()
        request_data['owner'] = request.user.user_id
        serializer = BlogSerializer(data = request_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class BlogDetail(APIView):

    permission_classes = (AccessPermission, )

    def get_object(self, id):
        try:
            return Blog.objects.get(post_id = id)
        except Blog.DoesNotExist:
            raise Http404
        
    def get(self, request, id):
        blog = self.get_object(id)
        serializer = BlogSerializer(blog)
        return Response(serializer.data)
    
    def put(self, request, id):
        blog = self.get_object(id)

        if blog.owner != request.user:
            return Response({'error' : 'You are not allowed to update this post'}, status=status.HTTP_403_FORBIDDEN)

        serializer = BlogSerializer(blog, data = request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):
        blog = self.get_object(id)

        print(blog.owner)
        print(request.user)

        if blog.owner != request.user:
            return Response({'error' : 'You are not allowed to delete this post.'}, status=status.HTTP_403_FORBIDDEN)
            
        blog.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class LikeView(APIView):

    permission_classes = (AccessPermission, )

    def get(self, request):
        like_objs = Like.objects.all()
        serializer = LikeSerializer(like_objs, many = True)
        return Response(serializer.data)
    
    def post(self, request):
        request_data = request.data.copy()
        request_data['user'] = request.user.user_id
        serializer = LikeSerializer(data = request_data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user'].user_id
            post_id = serializer.validated_data['post'].post_id

            if Like.objects.filter(user__user_id = user_id, post__post_id = post_id).exists():
                return Response({'message' : 'Like already exists.'}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LikeDetail(APIView):

    permission_classes = (AccessPermission, )

    def get_object(self, id):
        try:
            return Like.objects.get(like_id = id)
        except Like.DoesNotExist:
            raise Http404
        
    def put(self, request, id):
        like = self.get_object(id)

        if like.user != request.user:
            return Response({'error' : 'You are not able to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = LikeSerializer(like, data = request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def get(self, request, id):
        like = self.get_object(id)
        serializer = LikeSerializer(like)
        return Response(serializer.data)

    def delete(self, request, id):
        like_obj = self.get_object(id)

        if like_obj.user != request.user:
            return Response({'error': 'You can not delete this like'}, status=status.HTTP_403_FORBIDDEN)

        like_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)