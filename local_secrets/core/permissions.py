from rest_framework.permissions import IsAuthenticated


class IsAuthenticatedForPost(IsAuthenticated):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return super(IsAuthenticatedForPost, self).has_permission(request, view)
        else:
            return True
