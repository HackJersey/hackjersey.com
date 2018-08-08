from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.utils.translation import gettext_lazy as _

from django import forms
from django_extensions.admin import ForeignKeyAutocompleteAdmin

# Register your models here.
from .models import *

from tastypie.admin import ApiKeyInline


class MyAdminSite(AdminSite):
    site_header = 'New Jersey Crime Data'
    site_title = 'Database admin'

    def index(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}

        return super(MyAdminSite, self).index(request, extra_context)

    def login(self, request, redirect_field_name=None, extra_context=None):
        """
        Displays the login form for the given HttpRequest.
        """
        from django.contrib.auth.views import login
        from django.urls import reverse

        context = {}

        qd = request.GET.getlist('next')

        try:
            if qd[0]==u'/admin/docs/index.html':
                redirect_field_name="/admin/docs/index.html"
            else:
                redirect_field_name = "/admin/"
        except IndexError:
            redirect_field_name = "/admin/"

        context['next']=redirect_field_name

        defaults = {
            'extra_context': context,
            #'current_app': self.name,
            'authentication_form': self.login_form or AdminAuthenticationForm,
            'template_name': 'admin/login.html',
        }

        return login(request, **defaults)

admin_site = MyAdminSite(name='Crime')

class UserModelAdmin(UserAdmin):
    inlines = UserAdmin.inlines + [ApiKeyInline]

admin.site.unregister(User)
admin_site.register(User,UserModelAdmin)
admin_site.register(Group, GroupAdmin)


# Define a new FlatPageAdmin
class FlatPageAdmin(FlatPageAdmin):
    fieldsets = (
        (None, {'fields': ('url', 'title', 'content', 'sites')}),
        (_('Advanced options'), {
            'classes': ('collapse', ),
            'fields': (
                'enable_comments',
                'registration_required',
                'template_name',
            ),
        }),
    )

# Re-register FlatPageAdmin
#admin_site.unregister(FlatPage)
admin_site.register(FlatPage, FlatPageAdmin)


class StateAdmin(admin.ModelAdmin):
    list_display=('name',)
    ordering=('name',)
    search_fields = ['name',]

admin_site.register(State, StateAdmin)

class CountyAdmin(admin.ModelAdmin):
    form = forms.ModelForm
    list_display=('name', 'state')
    ordering=('state', 'name',)
    search_fields = ['name', 'state__name']

admin_site.register(County, CountyAdmin)

class CityAdmin(ForeignKeyAutocompleteAdmin):
    form=forms.ModelForm
    def state_list(obj):
        if obj.county:
            state = obj.county.state.name
        else:
            state = ""
        return state

    def save_model(self, request, obj, form, change):
        if change==True:
            changed="changed"
            obj.save()
        else:
            obj.save()
            changed="added"
        name = obj.__unicode__()
        user = request.user.username
        id = obj.id
        update_slack_task.delay(user=user, change=changed, model = "city", name=name, id=id)
        return

    state_list.admin_order_field = 'county__state__name'
    exclude = ('fips', 'abbrev')
    related_search_fields = {'county': ('name', 'state__name')}
    list_display=('name', state_list)
    ordering=('county__state__name', 'name',)
    search_fields = ['name', 'county__state__name']

admin_site.register(City, CityAdmin)

class ReleaseAdmin(admin.ModelAdmin):
    form = forms.ModelForm
    list_display=('file_name', 'frequency_type', 'file_type', 'date_released')
    ordering=('date_released', 'file_name',)
    search_fields = ['frequency_type', 'year_of_data']

admin_site.register(Release, ReleaseAdmin)

class DocumentationAdmin(admin.ModelAdmin):
    exclude=['slug',]
    list_display = ('title', 'help_type', 'chapter', 'author')
    ordering = ('help_type', 'chapter')
admin_site.register(Documentation, DocumentationAdmin)


class HJUserAdmin(admin.ModelAdmin):
    def user_name(self, obj):
        if obj.user.first_name:
            first_name = obj.user.first_name
        else:
            first_name = ''
        if obj.user.last_name:
            last_name = obj.user.last_name
        else:
            last_name = ''
        user_name = '{0} {1}'.format(first_name, last_name)
        return user_name

    user_name.short_description = 'Name'

    list_display=('user', 'user_name')
    exclude=('last_update',)
    search_fields = ['user__last_name', 'user__first_name']

admin_site.register(HJUser, HJUserAdmin)

class AgencyAdmin(ForeignKeyAutocompleteAdmin):
    form=forms.ModelForm
    list_display=('name', 'website')
    ordering=('name',)
    search_fields = ['name','cities__name', 'counties__name']

admin_site.register(Agency, AgencyAdmin)