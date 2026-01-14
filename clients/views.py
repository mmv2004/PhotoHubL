from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Client
from .forms import ClientForm

class ClientListView(LoginRequiredMixin, ListView):
    """
    Представление для отображения списка клиентов
    """
    model = Client
    template_name = 'clients/client_list.html'
    context_object_name = 'clients'
    
    def get_queryset(self):
        """
        Фильтрация клиентов по текущему пользователю и поисковому запросу
        """
        queryset = Client.objects.filter(photographer=self.request.user)
        
        # Поиск по запросу
        query = self.request.GET.get('query')
        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query) | 
                Q(last_name__icontains=query) | 
                Q(email__icontains=query) | 
                Q(phone_number__icontains=query)
            )
            
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Добавляем форму поиска в контекст
        """
        context = super().get_context_data(**kwargs)

        return context

class ClientDetailView(LoginRequiredMixin, DetailView):
    """
    Представление для отображения деталей клиента
    """
    model = Client
    template_name = 'clients/client_detail.html'
    context_object_name = 'client'
    
    def get_queryset(self):
        """
        Фильтрация клиентов по текущему пользователю
        """
        return Client.objects.filter(photographer=self.request.user)

class ClientCreateView(LoginRequiredMixin, CreateView):
    """
    Представление для создания нового клиента
    """
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('clients:client_list')
    
    def form_valid(self, form):
        """
        Устанавливаем текущего пользователя как фотографа
        """
        form.instance.photographer = self.request.user
        messages.success(self.request, 'Клиент успешно добавлен!')
        return super().form_valid(form)

class ClientUpdateView(LoginRequiredMixin, UpdateView):
    """
    Представление для редактирования клиента
    """
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    
    def get_queryset(self):
        """
        Фильтрация клиентов по текущему пользователю
        """
        return Client.objects.filter(photographer=self.request.user)
    
    def get_success_url(self):
        """
        Возвращаем URL для перенаправления после успешного обновления
        """
        messages.success(self.request, 'Данные клиента успешно обновлены!')
        return reverse_lazy('clients:client_detail', kwargs={'pk': self.object.pk})

class ClientDeleteView(LoginRequiredMixin, DeleteView):
    """
    Представление для удаления клиента
    """
    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('clients:client_list')
    
    def get_queryset(self):
        """
        Фильтрация клиентов по текущему пользователю
        """
        return Client.objects.filter(photographer=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        """
        Добавляем сообщение об успешном удалении
        """
        messages.success(self.request, 'Клиент успешно удален!')
        return super().delete(request, *args, **kwargs)


