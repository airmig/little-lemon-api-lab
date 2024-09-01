from rest_framework.permissions import BasePermission

class IsManagerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is in the 'manager' or 'superuser' group
        return request.user.groups.filter(name__in=['Manager']).exists() or request.user.is_superuser
    

class IsDeliveryCrew(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is in the 'delivery crew' group
        return request.user.groups.filter(name__in=['Delivery Crew']).exists()