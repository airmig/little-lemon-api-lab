from django.urls import path
from .views import MenuItemView, MenuItemSingle, getManagers, getCrew, CartMenuItems, OrderItems

urlpatterns = [
    path('menu-items/', MenuItemSingle.as_view()),
    path('menu-items', MenuItemSingle.as_view()),
    path('menu-items/<int:pk>', MenuItemView.as_view()),
    path('menu-items/<int:pk>/', MenuItemView.as_view()),
    path('groups/manager/users', getManagers),
    path('groups/manager/users/', getManagers),
    path('groups/manager/users/<int:pk>', getManagers),
    path('groups/manager/users/<int:pk>/', getManagers),
    path('groups/delivery-crew/users', getCrew),
    path('groups/delivery-crew/users/', getCrew),
    path('groups/delivery-crew/users/<int:pk>', getCrew),
    path('groups/delivery-crew/users/<int:pk>/', getCrew),
    path('cart/menu-items', CartMenuItems.as_view()),
    path('orders', OrderItems.as_view()),
    path('orders/', OrderItems.as_view()),
    path('orders/<int:pk>', OrderItems.as_view()),
    path('orders/<int:pk>/', OrderItems.as_view())
]