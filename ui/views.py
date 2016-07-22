import os

from django.conf import settings
from django.contrib.auth import logout as django_logout
from django.contrib.sites.models import Site
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View, TemplateView

from luna_django_commons.app.mixins import get_login_context


from .forms import (
    B2DropProviderForm,
    DatafileForm,
    DatafileUpdateForm,
    DatasetAddFileForm,
    DatasetForm,
    DropboxProviderForm,
    FolderForm,
    ForgotPasswordForm,
    GDriveProviderForm,
    LoginForm,
    PasswordChangeForm,
    RegisterForm,
    ResetPasswordForm,
    S3ProviderForm,
    WLWebdavProviderForm,
)


class Root(TemplateView):

    def get_template_names(self):
        """
        Returns a list of template names to be used for the request. Must return
        a list. May not be called if render_to_response is overridden.
        """
        domain = Site.objects.get_current().domain
        if "west-life" in domain:
            return ['static_pages/landing_westlife.html']
        elif "pype" in domain:
            return ['static_pages/landing_pype.html']
        return ['static_pages/landing_westlife.html']


def westlife_services(request):
    context = get_login_context(request)
    return render(request, 'static_pages/westlife/services.html', context)


def legal(request):
    context = get_login_context(request)
    return render(request, 'static_pages/cgv.html', context)


def internet_explorer(request):
    context = get_login_context(request)
    return render(request, 'static_pages/internet_explorer.html', context)


def westlife_static_page(request, page_name='fweh.html'):
    context = get_login_context(request)
    return render(request, 'static_pages/westlife/%s' % page_name, context)


#
# Debug information
#
class BuildInfo(View):
    def get(self, *args, **kwargs):
        version_file_path = os.path.join(settings.BASE_DIR, 'build_info.txt')
        try:
            with open(version_file_path, 'r') as f:
                data = f.read()
        except IOError:
            data = 'No build information found. Probably means we are in development mode.'

        return HttpResponse(data, content_type='text/plain')


class MainPage(TemplateView):
    template_name = 'main.html'

    def get_context_data(self, **kwargs):
        context = super(MainPage, self).get_context_data(**kwargs)

        user = self.request.user

        context.update({
            'INTERCOM_APP_ID': settings.INTERCOM_APP_ID,

            'b2dropprovider_form': B2DropProviderForm(),
            'wlwebdavprovider_form': WLWebdavProviderForm(),
            'change_password_form': PasswordChangeForm(user=user),
            'datafile_form': DatafileForm(),
            'datafile_update_form': DatafileUpdateForm(),
            'dataset_add_file_form': DatasetAddFileForm(),
            'dataset_form': DatasetForm(),
            'dropboxprovider_form': DropboxProviderForm(),
            'folder_form': FolderForm(),
            'forgot_password_form': ForgotPasswordForm(),
            'gdriveprovider_form': GDriveProviderForm(),
            'login_form': LoginForm(),
            'register_form': RegisterForm(),
            'reset_password_form': ResetPasswordForm(),
            's3provider_form': S3ProviderForm(),
        })

        return context


def whoami(request):
    return HttpResponse(request.user.username)


def logout(request):
    django_logout(request)
    return HttpResponse('Logged out!')