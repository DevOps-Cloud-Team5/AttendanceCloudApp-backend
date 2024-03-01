from rest_framework import permissions

class IsRole(permissions.BasePermission):
    role_list = []
    def has_permission(self, request, _):
        return hasattr(request.user, "role") and request.user.role in self.role_list

class IsStudent(IsRole): role_list = ["Admin", "Teacher", "Student"]
class IsTeacher(IsRole): role_list = ["Admin", "Teacher"]
class IsAdmin(IsRole):   role_list = ["Admin"]