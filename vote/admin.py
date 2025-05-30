from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.contrib.auth.forms import UserChangeForm, AdminPasswordChangeForm
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.template.response import TemplateResponse
from django.utils.html import format_html
from rangefilter.filters import (
    DateRangeQuickSelectListFilterBuilder,
)
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import Candidate, User, District, Term, Vote


class UserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'district', 'birthdate', 'address')
        export_order = ('id', 'name', 'email', 'district', 'birthdate', 'address')

    def skip_row(self, instance, original, row, import_validation_errors=None):
        if not row.get('district') or row.get('district') == 'None' or row.get('district') == '':
            return True
        if not row.get('id') or row.get('id') == 'None' or row.get('id') == '':
            return True
        if not row.get('email') or row.get('email') == 'None' or row.get('email') == '':
            return True
        if not row.get('name') or row.get('name') == 'None' or row.get('name') == '':
            return True
        if not row.get('address') or row.get('address') == 'None' or row.get('address') == '':
            return True
        if not row.get('birthdate') or row.get('birthdate') == 'None' or row.get('birthdate') == '':
            return True
        if row.get('birthdate'):
            from datetime import datetime
            if (datetime.now() - row.get('birthdate')).days < 18 * 365:
                return True
        return super().skip_row(instance, original, row, import_validation_errors)


class CustomUserChangeList(ChangeList):
    def url_for_result(self, result):
        if result.is_staff and result != self.model_admin.request.user:
            return None
        return super().url_for_result(result)


class CandidateAdmin(admin.ModelAdmin):
    readonly_fields = ["image_tag"]
    list_display = ["name", "district", "image_tag", "vote_count"]
    list_filter = ["district"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.filter(district=request.user.district)
        return queryset.annotate(vote_count=Count('vote'))

    @admin.display(description="Votes", ordering='vote_count')
    def vote_count(self, obj):
        return obj.get_vote_count()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "district" and request.user.is_superuser:
            kwargs["queryset"] = District.objects.filter(id=request.user.district.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if obj.district is None:
            raise PermissionDenied("You must select a district for the candidate.")
        return super().save_model(request, obj, form, change)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'


class CustomUserAdmin(ImportExportModelAdmin):
    resource_classes = [UserResource]

    form = CustomUserChangeForm
    exclude = ["username"]
    list_display = ["id", "name", "email", "district", "show_voted"]
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

    def show_voted(self, obj):
        if obj.is_staff:
            return ""
        if obj.voted:
            return format_html('<img src="/static/admin/img/icon-yes.svg" alt="False">')
        return format_html('<img src="/static/admin/img/icon-no.svg" alt="False">')

    show_voted.short_description = "Voted"
    show_voted.admin_order_field = 'voted'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(Q(is_staff=False, is_superuser=False))
            queryset = queryset.filter(district=request.user.district)
        return queryset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "district" and not request.user.is_superuser and request.user.district is not None:
            kwargs["queryset"] = District.objects.filter(id=request.user.district.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if obj.district is None:
            raise PermissionDenied("You must select a district for the candidate.")
        return super().save_model(request, obj, form, change)


class VoteAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'timestamp']
    list_filter = [('timestamp', DateRangeQuickSelectListFilterBuilder())]
    search_fields = ['candidate__name']

    def has_add_permission(self, request):
        return False  # Disable adding votes through the admin interface

    def has_delete_permission(self, request, obj=None):
        return False  # Disable deleting votes through the admin interface


admin.site.register(Candidate, CandidateAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(District)
admin.site.register(Term)
