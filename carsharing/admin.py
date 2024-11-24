from django.contrib import admin
from django.contrib.auth.models import Group

from carsharing.models import User, Document, Order, Car


admin.site.unregister(Group)
admin.site.unregister(User)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff')
    readonly_fields = ('date_joined', 'last_login', 'is_superuser', 'groups', 'user_permissions')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('password',)
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if not change:
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)


admin.site.register(Document)
admin.site.register(Order)
admin.site.register(Car)
