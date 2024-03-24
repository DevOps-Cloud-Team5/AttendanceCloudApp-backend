from rest_framework import permissions


class IsRole(permissions.BasePermission):
    role_list = []
    def has_permission(self, request, _=None):
        # return True # For debugging, full open permission is given
        return hasattr(request.user, "role") and request.user.role in self.role_list

class IsStudent(IsRole): role_list = ["admin", "teacher", "student"]
class IsTeacher(IsRole): role_list = ["admin", "teacher"]
class IsAdmin(IsRole):   role_list = ["admin"]