from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import CategorySerializer, MenuItemSerializer, CartSerializer, OrderSerializer, UserSerilializer
from rest_framework.response import Response

from rest_framework.permissions import IsAdminUser
from django.shortcuts import  get_object_or_404

from django.contrib.auth.models import Group, User

from rest_framework import viewsets
from rest_framework import status


class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]


##########################
# Menu-items endpoints
##########################

# class MenuItemsView(generics.ListCreateAPIView):
# 	queryset = MenuItem.objects.all()
# 	serializer_class = MenuItemSerializer

# 	def get_permission(self):
# 		permission_classes = [IsAuthenticated]

# 		if self.request.method != 'GET':
# 			permission_classes = [IsAdminUser]

# 		return [permission() for permission in permission_classes]