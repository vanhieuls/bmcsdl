from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.core.exceptions import PermissionDenied
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm, AdminPasswordChangeForm
from django.template.response import TemplateResponse
from django.core.exceptions import PermissionDenied
from rangefilter.filters import (
    DateRangeFilterBuilder,
    DateTimeRangeFilterBuilder,
    NumericRangeFilterBuilder,
    DateRangeQuickSelectListFilterBuilder,
)


from .models import Candidate, User, District, Term, Vote


class CandidateAdmin(admin.ModelAdmin):
    readonly_fields = ["votes", "image_tag"]
    list_display = ["name", "district", "image_tag", "get_vote_count"]
    list_filter = ["district"]


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'


class CustomUserAdmin(admin.ModelAdmin):
    form = CustomUserChangeForm
    # readonly_fields = ["groups"]
    exclude = ["username"]
    list_display = ["id", "name", "email", "district"]
    fields = [
        "id",
        "name",
        "password",
        "birthdate",
        "address",
        "district",
        "email",
        "groups",
        "is_staff",
    ]
    filter_horizontal = ('groups', 'user_permissions',)

    def change_password(self, request, user_id, form_url=''):
        user = self.get_object(request, user_id)
        if not self.has_change_permission(request, user):
            raise PermissionDenied

        if request.method == 'POST':
            form = AdminPasswordChangeForm(user, request.POST)
            if form.is_valid():
                form.save()
                return self.response_change(request, user)
        else:
            form = AdminPasswordChangeForm(user)

        fieldsets = [(None, {'fields': list(form.base_fields)})]
        admin_form = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            'title': f'Change password: {user.email}',
            'adminForm': admin_form,
            'form_url': form_url,
            'form': form,
            'is_popup': "_popup" in request.POST or "_popup" in request.GET,
            'opts': self.model._meta,
            'original': user,
            'save_as': False,
            'show_save': True,
            **self.admin_site.each_context(request),
        }

        return TemplateResponse(request, 'admin/auth/user/change_password.html', context)

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<user_id>/password/',
                self.admin_site.admin_view(self.change_password),
                name='auth_user_password_change',
            ),
        ]
        return custom_urls + urls


class VoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'candidate', 'timestamp']
    list_filter = [('timestamp', DateRangeQuickSelectListFilterBuilder())]
    search_fields = ['user__id', 'candidate__name']

    def has_add_permission(self, request):
        return False  # Disable adding votes through the admin interface

    def has_delete_permission(self, request, obj=None):
        return False  # Disable deleting votes through the admin interface


admin.site.register(Candidate, CandidateAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(District)
admin.site.register(Term)
admin.site.register(Vote, VoteAdmin)
