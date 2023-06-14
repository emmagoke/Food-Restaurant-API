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

class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    search_fields = ['category__title']
    ordering_fields = ['price', 'inventory']

    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]


class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]


################################
## Cart management endpoints ##
################################


# @api_view(['GET', 'POST', 'DELETE'])
# @permission_classes([IsAuthenticated])
# def cartitems(request):
# 	user_id = request.user.id
# 	# user = get_object_or_404(User, pk=user_id)
# 	# user_cart = user.cart_set.all()
# 	# user_cart = Cart.objects.filter(user__pk=user_id)
# 	if request.method == 'POST':
# 		menuitemId = request.get('menuitem')
# 		quantity = request.get('quantity')
# 		menuitem = get_object_or_404(MenuItem, pk=menuitemId)
# 		price = quantity * menuitem.price
# 		new_cart = Cart(user=request.user, menuitem=menuitemId,
# 			unit_price=menuitem.price, price=price)
		
# 		user_cart.save()
# 		return Response({}, status.HTTP_201_CREATED)
# 	elif request.method == 'GET':
# 		user_cart = Cart.objects.filter(user__pk=user_id)
# 		serialized_item = CartSerializer(user_cart, many=True)

# 		return Response(serialized_item.data, 200)
# 	elif request.method == 'DELETE':
# 		user_cart = Cart.objects.filter(user__pk=user_id)
# 		user_cart.delete()
# 		return Response({}, 200)

class CartView(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.all().filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        Cart.objects.all().filter(user=self.request.user).delete()
        return Response("ok")



################################
## Order management endpoints ##
################################
class OrderView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Order.objects.all()
        elif self.request.user.groups.count()==0: #normal customer - no group
            return Order.objects.all().filter(user=self.request.user)
        elif self.request.user.groups.filter(name='Delivery Crew').exists(): #delivery crew
            return Order.objects.all().filter(delivery_crew=self.request.user)  #only show oreders assigned to him
        else: #delivery crew or manager
            return Order.objects.all()
        # else:
        #     return Order.objects.all()

    def create(self, request, *args, **kwargs):
        menuitem_count = Cart.objects.all().filter(user=self.request.user).count()
        if menuitem_count == 0:
            return Response({"message:": "no item in cart"})

        data = request.data.copy()
        total = self.get_total_price(self.request.user)
        data['total'] = total
        data['user'] = self.request.user.id
        order_serializer = OrderSerializer(data=data)
        if (order_serializer.is_valid()):
            order = order_serializer.save()

            items = Cart.objects.all().filter(user=self.request.user).all()

            for item in items.values():
                orderitem = OrderItem(
                    order=order,
                    menuitem_id=item['menuitem_id'],
                    price=item['price'],
                    quantity=item['quantity'],
                )
                orderitem.save()

            Cart.objects.all().filter(user=self.request.user).delete() #Delete cart items

            result = order_serializer.data.copy()
            result['total'] = total
            return Response(order_serializer.data)
    
    def get_total_price(self, user):
        total = 0
        items = Cart.objects.all().filter(user=user).all()
        for item in items.values():
            total += item['price']
        return total


class SingleOrderView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        if self.request.user.groups.count()==0: # Normal user, not belonging to any group = Customer
            return Response('Not Ok')
        else: #everyone else - Super Admin, Manager and Delivery Crew
            return super().update(request, *args, **kwargs)



#####################################
## User group management endpoints
#####################################
class GroupViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]
    def list(self, request):
        users = User.objects.all().filter(groups__name='Manager')
        items = UserSerilializer(users, many=True)
        return Response(items.data)

    def create(self, request):
        user = get_object_or_404(User, username=request.data['username'])
        managers = Group.objects.get(name="Manager")
        managers.user_set.add(user)
        return Response({"message": "user added to the manager group"}, 200)

    def destroy(self, request):
        user = get_object_or_404(User, username=request.data['username'])
        managers = Group.objects.get(name="Manager")
        managers.user_set.remove(user)
        return Response({"message": "user removed from the manager group"}, 200)

class DeliveryCrewViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    def list(self, request):
        users = User.objects.all().filter(groups__name='Delivery Crew')
        items = UserSerilializer(users, many=True)
        return Response(items.data)

    def create(self, request):
        #only for super admin and managers
        if self.request.user.is_superuser == False:
            if self.request.user.groups.filter(name='Manager').exists() == False:
                return Response({"message":"forbidden"}, status.HTTP_403_FORBIDDEN)
        
        user = get_object_or_404(User, username=request.data['username'])
        dc = Group.objects.get(name="Delivery Crew")
        dc.user_set.add(user)
        return Response({"message": "user added to the delivery crew group"}, 200)

    def destroy(self, request):
        #only for super admin and managers
        if self.request.user.is_superuser == False:
            if self.request.user.groups.filter(name='Manager').exists() == False:
                return Response({"message":"forbidden"}, status.HTTP_403_FORBIDDEN)
        user = get_object_or_404(User, username=request.data['username'])
        dc = Group.objects.get(name="Delivery Crew")
        dc.user_set.remove(user)
        return Response({"message": "user removed from the delivery crew group"}, 200)