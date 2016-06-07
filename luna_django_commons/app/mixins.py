# coding: utf-8

# Copyright Luna Technology 2015


# DJANGO
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)
from django.utils.decorators import method_decorator


def get_login_context(request):
    context = {}

    user = request.user

    context['logged_in'] = user.is_authenticated()

    if context['logged_in']:
        context['current_user'] = user
        context['current_user_id'] = user.id

    if is_vpn_access(request):
        context['vpn_access'] = True

    return context


def is_vpn_access(request):
    ip = request.META['REMOTE_ADDR']
    if ip == '127.0.0.1' or ip.startswith('10.63.89.') or ip.startswith('192.168.'):
        return True
    else:
        return False


def vpn_only_method(func):
    def inner(request, *args, **kwargs):
        if is_vpn_access(request):
            return func(request, *args, **kwargs)
        else:
            raise Http404()
    return inner


class VPNOnlyMixin(object):

    @method_decorator(vpn_only_method)
    def dispatch(self, *args, **kwargs):
        return super(VPNOnlyMixin, self).dispatch(*args, **kwargs)


class ForceAuthenticatedMixin(object):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ForceAuthenticatedMixin, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ''' Add login data to the context'''
        context = super(ForceAuthenticatedMixin, self).get_context_data(**kwargs)
        context.update(get_login_context(self.request))
        return context


class AuthenticatedListView(ForceAuthenticatedMixin, ListView):
    pass


class AuthenticatedDetailView(ForceAuthenticatedMixin, DetailView):
    pass


class AuthenticatedCreateView(ForceAuthenticatedMixin, CreateView):
    pass


class AuthenticatedUpdateView(ForceAuthenticatedMixin, UpdateView):
    pass


class AuthenticatedDeleteView(ForceAuthenticatedMixin, DeleteView):
    pass


class AuthenticatedFormView(ForceAuthenticatedMixin, FormView):
    pass


class AuthenticatedTemplateView(ForceAuthenticatedMixin, TemplateView):
    pass


class AuthenticatedView(ForceAuthenticatedMixin, View):
    pass


class VPNOnlyMixinListView(VPNOnlyMixin, ForceAuthenticatedMixin, ListView):
    pass
