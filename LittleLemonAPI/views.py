from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from .models import MenuItem, Cart, Order, OrderItem
from .serializers import MenuItemSerializer, UserSerializer, CartSerializer, CartItemSerializer
from .serializers import OrderItemSerializer, OrderSerializer, StatusSerializer
from .permissions import IsManagerOrAdmin, IsDeliveryCrew
from django.contrib.auth.models import Group, User
from datetime import date

# Create your views here.

def DefaultView(request):
    return render(request,'home.html')

class OrderItems(generics.ListCreateAPIView, generics.UpdateAPIView):
    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [permission() for permission in [IsAuthenticated, IsManagerOrAdmin]]
        
        return [permission() for permission in [IsAuthenticated]]

    def delete(self, request, *args, **kwargs):
        pk = None
        try:
            pk = kwargs['pk']
        except:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        try:
            pk = kwargs['pk']
            try:
                order = Order.objects.get(pk=pk)
            except:
                return Response(status=status.HTTP_404_NOT_FOUND)
            order.delete()
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        user = request.user
        pk = None
        try:
            if kwargs['pk']:
                pk = kwargs['pk']
        except:
            pass
        if user.is_authenticated:
            if user.groups.filter(name__in=['Delivery Crew']).exists():
                status_value = request.data.get('status', None)
                if status_value is None:
                    return Response({"error": "Status is required."}, status=status.HTTP_400_BAD_REQUEST)

                serializer = StatusSerializer(data=request.data)
                if serializer.is_valid():
                    try:
                        try:
                            order =  Order.objects.get(pk=pk)
                        except:
                            return Response({'error':'Order not found'}, status=status.HTTP_404_NOT_FOUND)
                        order.status = bool(int(status_value))
                        order.save()
                        return Response(status=status.HTTP_200_OK)
                    except Exception as e:
                        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            elif user.groups.filter(name__in=['Manager']).exists():
                status_value = request.data.get('status', None)
                delivery_crew = request.data.get('delivery_crew', None)
                try:
                    order = Order.objects.get(pk=pk)
                    if status_value is not None:
                        order.status  = bool((int(status_value)))
                    if delivery_crew is not None:
                        try:
                            user_crew = User.objects.get(pk=delivery_crew)
                        except:
                            return Response({'error': 'Invalid delivery crew user'},status=status.HTTP_404_NOT_FOUND)
                        order.delivery_crew = user_crew
                    order.save()
                    return Response(status=status.HTTP_200_OK)
                except:
                    return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            else:
                 return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    def get(self, request, *args, **kwargs):
        user = request.user
        pk = None
        try:
            if kwargs['pk']:
                pk = kwargs['pk']
        except:
            pass
        if user.is_authenticated:
            if not pk:
                if user.groups.filter(name__in=['Manager']).exists() or user.is_superuser:
                    queryset = Order.objects.all()
                elif user.groups.filter(name__in=['Delivery Crew']).exists():
                    delivery_group = Group.objects.get(name='Delivery Crew')
                    #queryset = Order.objects.filter(user__groups=delivery_group)
                    queryset = Order.objects.filter(delivery_crew__isnull=False)
                else:
                    queryset = Order.objects.filter(user=user)
                serialize = OrderSerializer(queryset,many=True)
                return Response(serialize.data, status=status.HTTP_200_OK)
            else:
                try:
                    queryset = Order.objects.get(id=pk)
                    if queryset.user != user:
                        return Response(status=status.HTTP_403_FORBIDDEN)
                    serialize = OrderSerializer(queryset)
                    return Response(serialize.data, status=status.HTTP_200_OK)
                except Order.DoesNotExist:
                    return Response({'error': 'Order not found'}, status= status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            try:
                items = Cart.objects.filter(user=user)
                if items:
                    total = 0
                    for item in items:
                        total = total + item.price
                    order = Order(user=user, total=total, date=date.today())
                    order.save()
                    order_items = []
                    for item in items:
                        order_item = OrderItem(
                                order=order,
                                menuitem=item.menuitem,
                                quantity=item.quantity,
                                unit_price=item.unit_price,
                                price=item.price
                        )
                        order_items.append(order_item)
                    # Bulk create all OrderItem instances in one query
                    OrderItem.objects.bulk_create(order_items)
                    items.delete()
                else:
                    return Response({'error': 'Cart is currently empty '}, status= status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(status=status.HTTP_201_CREATED) 

class CartMenuItems(generics.ListCreateAPIView, generics.DestroyAPIView):
    def delete(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            queryset = Cart.objects.filter(user=user).delete()
            return  Response(status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            queryset = Cart.objects.filter(user=user)
            serialize = CartSerializer(queryset,many=True)
        else:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serialize.data, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            menuitem = request.data.get('menuitem')
            quantity = request.data.get("quantity")
            validate_request = {
                'user': user.id,
                'menuitem': menuitem if menuitem else None,
                'quantity': quantity if quantity else None
            }
            serializer = CartItemSerializer(data=validate_request)
            if serializer.is_valid():
                try:
                    item = MenuItem.objects.get(pk=request.data['menuitem'])
                    user = user
                    unit_price = item.price
                    price = item.price * int(request.data['quantity'])
                    cart_item = Cart(user=user, menuitem=item, quantity=request.data['quantity'], price=price, unit_price=unit_price)
                    cart_item.save()
                except Exception as e:
                    return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(status=status.HTTP_201_CREATED) 

class MenuItemSingle(generics.ListAPIView, generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permission() for permission in [IsAuthenticated]]
        return [permission() for permission in [IsAuthenticated, IsManagerOrAdmin]]


class MenuItemView(generics.RetrieveUpdateDestroyAPIView, generics.ListCreateAPIView):
    queryset =  MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permission() for permission in [IsAuthenticated]]
        return [permission() for permission in [IsAuthenticated, IsManagerOrAdmin]]
    
@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated, IsManagerOrAdmin])
def getManagers(request, pk=None):
    if request.method == 'GET':
        manager_group = Group.objects.get(name='Manager')
        users_in_manager_group = User.objects.filter(groups=manager_group)
        serializer = UserSerializer(users_in_manager_group, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'POST':
        user = None
        serializer = None
        try:
            user =  User.objects.get(pk=pk)
            serializer = UserSerializer(user)
        except User.DoesNotExist:
            pass

        if pk == None:
            return Response({'error': 'URL must include a primary key (pk) parameter indicating the user id.'}, status=status.HTTP_400_BAD_REQUEST)
        if not user:
            return Response({'error': 'Could not find user with id ' + str(pk)}, status= status.HTTP_404_NOT_FOUND)
        
        try:
            manager_group = Group.objects.get(name='Manager')
            user.groups.add(manager_group)
            user.save()
        except:
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(status=status.HTTP_201_CREATED)

    if request.method == 'DELETE':
        user = None
        serializer = None
        try:
            user =  User.objects.get(pk=pk)
            serializer = UserSerializer(user)
        except User.DoesNotExist:
            pass

        if pk == None:
            return Response({'error': 'URL must include a primary key (pk) parameter indicating the user id.'}, status=status.HTTP_400_BAD_REQUEST)
        if not user:
            return Response({'error': 'Could not find user with id ' + str(pk)}, status= status.HTTP_404_NOT_FOUND)
        
        try:
            manager_group = Group.objects.get(name='Manager')
            if not user.groups.contains(manager_group):
                return Response({'error': 'User not in Manager group'}, status= status.HTTP_404_NOT_FOUND)

            user.groups.remove(manager_group)
            user.save()
        except:
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(status=status.HTTP_200_OK)
    
@api_view(['GET', 'POST', 'DELETE'])
def getCrew(request, pk=None):
    if request.method == 'GET':
        manager_group = Group.objects.get(name='Delivery Crew')
        users_in_manager_group = User.objects.filter(groups=manager_group)
        serializer = UserSerializer(users_in_manager_group, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'POST':
        user = None
        serializer = None
        try:
            user =  User.objects.get(pk=pk)
            serializer = UserSerializer(user)
        except User.DoesNotExist:
            pass

        if pk == None:
            return Response({'error': 'URL must include a primary key (pk) parameter indicating the user id.'}, status=status.HTTP_400_BAD_REQUEST)
        if not user:
            return Response({'error': 'Could not find user with id ' + str(pk)}, status= status.HTTP_404_NOT_FOUND)
        
        try:
            manager_group = Group.objects.get(name='Delivery Crew')
            user.groups.add(manager_group)
            user.save()
        except Exception as e:
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(status=status.HTTP_201_CREATED)

    if request.method == 'DELETE':
        user = None
        serializer = None
        try:
            user =  User.objects.get(pk=pk)
            serializer = UserSerializer(user)
        except User.DoesNotExist:
            pass

        if pk == None:
            return Response({'error': 'URL must include a primary key (pk) parameter indicating the user id.'}, status=status.HTTP_400_BAD_REQUEST)
        if not user:
            return Response({'error': 'Could not find user with id ' + str(pk)}, status= status.HTTP_404_NOT_FOUND)
        
        try:
            manager_group = Group.objects.get(name='Delivery Crew')
            if not user.groups.contains(manager_group):
                return Response({'error': 'User not in Delivery Crew group'}, status= status.HTTP_404_NOT_FOUND)

            user.groups.remove(manager_group)
            user.save()
        except Exception as e:
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(status=status.HTTP_200_OK)