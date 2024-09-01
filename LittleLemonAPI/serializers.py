from rest_framework import serializers
from .models import MenuItem, Category, Cart, Order, OrderItem
from django.contrib.auth.models import User

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['menuitem', 'quantity', 'unit_price', 'price']

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(source='orderitem_set', many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date', 'order_items']

class StatusSerializer(serializers.Serializer):
    status = serializers.BooleanField()
    def validate_status(self, value):
        if value == 1:
            return value
        if value == 0:
            return value
        else:
            raise serializers.ValidationError({"error": "item can be 0 or 1"})

class CartItemSerializer(serializers.Serializer):
    user = serializers.IntegerField()
    menuitem  =  serializers.IntegerField()
    quantity = serializers.IntegerField()

    def validate(self, data):
        user = data.get('user')
        menuitem = data.get('menuitem')
        # Check for uniqueness constraint
        if Cart.objects.filter(user=user, menuitem=menuitem).exists():
            raise serializers.ValidationError('The combination of user and menuitem must be unique.')
        return data

    def validate_item(self, value):
        try:
            item = MenuItem.objects.get(pk=value)
            if item:
                return value
            else:
                raise serializers.ValidationError({"error": "item not found invalid primary key value (pk)"})
        except:
            raise serializers.ValidationError({"error": "invalid item key please use the primary key value (pk)"})

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("quantity must be a non-negative integer.")
        if value > 100:
            raise serializers.ValidationError("quantity must be less than or equal to 100.")
        return value

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['user', 'menuitem', 'quantity', 'unit_price', 'price']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'slug']

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        category = CategorySerializer(read_only=True)
        category_id = serializers.IntegerField(write_only=True)
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email',  'first_name', 'last_name']