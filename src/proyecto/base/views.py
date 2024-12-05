from lib2to3.fixes.fix_input import context

from django.shortcuts import render, redirect
# from django.http import HttpResponse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView

# estas dos son para generar el registro de usuarios
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from django.contrib.auth.views import LoginView

# el mixins entre otras cosas sirve para restrigir acceso solo a usuarios logueados
from django.contrib.auth.mixins import LoginRequiredMixin

from django.urls import reverse_lazy
from .models import Tarea


class IniciaSesion(LoginView):
    template_name = 'base/login.html'
    field = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('pendientes')

class PaginaRegistro(FormView):
    template_name = 'base/registro.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('pendientes')

    # esto hace que cuando un usuario se registra ya quede logueado
    def form_valid(self, form):
        usuario = form.save()
        if usuario is not None:
            login(self.request, usuario)
        return super(PaginaRegistro, self).form_valid(form)

    # hace que si ya está logueado no puede entrar a la página de registro
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('pendientes')
        return super(PaginaRegistro, self).get(*args, **kwargs)


# def lista_pendientes(pedido):
#     return HttpResponse('Lista de pendientes')

class ListaPendientes(LoginRequiredMixin, ListView):
    model = Tarea
    context_object_name = 'tareas'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tareas'] = context['tareas'].filter(usuario=self.request.user)
        context['count'] = context['tareas'].filter(completo=False).count()
        # hace que solo se vean las tareas del usuario loiguieado en ese momento

        valor_buscado = self.request.GET.get('area_buscar') or ''
        if valor_buscado:
            context['tareas'] = context['tareas'].filter(titulo__icontains=valor_buscado)
        context['valor_buscado'] = valor_buscado
        return context

class DetalleTarea(LoginRequiredMixin, DetailView):
    model = Tarea
    # el model es la base de datos de donde saca la info
    context_object_name = 'tarea'
    template_name = 'base/tarea.html'

class CrearTarea(LoginRequiredMixin, CreateView):
    model = Tarea
    # fields = '__all__'
    fields = ['titulo', 'descripcion', 'completo']
    # como agregue el metodo def form_valid(self, form): no puedo poner todos los campos
    # me a a poner como creador de la tarea a quien esté logueado en ese momento
    success_url = reverse_lazy('pendientes')

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super(CrearTarea, self).form_valid(form)
    # este metodo hace que el usuario logueado pueda generar ua tarea sin que elusuario
    # tenga que ser elegido del combo del form

class EditarTarea(LoginRequiredMixin, UpdateView):
    model = Tarea
    template_name = 'base/tarea_editar.html'
    fields = ['titulo', 'descripcion', 'completo']
    success_url = reverse_lazy('pendientes')

class EliminarTarea(LoginRequiredMixin, DeleteView):
    model = Tarea
    context_object_name = 'ttt'
    success_url = reverse_lazy('pendientes')