"""
API Permissions - Phase 2

Custom permission classes for REST API endpoints.
Integrates with the role-based permission system from accounts app.
"""

from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permission check for admin users only.
    """
    message = "Only administrators can perform this action."

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_admin
        )


class IsLocationManager(permissions.BasePermission):
    """
    Permission check for location managers and admins.
    """
    message = "Only location managers and administrators can perform this action."

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_location_manager
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Admin users can perform any action.
    Other authenticated users can only read (GET, HEAD, OPTIONS).
    """
    message = "Only administrators can modify this resource."

    def has_permission(self, request, view):
        # Allow read-only access for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Write access only for admins
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_admin
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission.
    - Owner of the object can modify it
    - Admin users can modify any object
    - Anyone can read
    """
    message = "You can only modify your own resources."

    def has_object_permission(self, request, view, obj):
        # Read permissions for anyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Admin can do anything
        if request.user.is_admin:
            return True

        # Check if user is owner (for objects with created_by field)
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user

        # Check if user is responsible person (for Asset model)
        if hasattr(obj, 'responsible_person'):
            return obj.responsible_person == request.user

        return False


class IsOwnerOrLocationManager(permissions.BasePermission):
    """
    Object-level permission.
    - Owner can modify
    - Location managers can modify
    - Admins can modify
    - Anyone can read
    """
    message = "You must be the owner or a location manager to modify this resource."

    def has_object_permission(self, request, view, obj):
        # Read permissions for anyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Admin or location manager can do anything
        if request.user.is_location_manager:
            return True

        # Check if user is owner
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user

        if hasattr(obj, 'initiated_by'):
            return obj.initiated_by == request.user

        return False
