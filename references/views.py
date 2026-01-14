from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import ReferenceCategory, Reference
from .forms import CategoryForm, ReferenceForm, ReferenceSearchForm

class CategoryListView(LoginRequiredMixin, ListView):
    """
    Представление для отображения списка категорий референсов
    """
    model = ReferenceCategory
    template_name = 'references/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        """
        Фильтрация категорий по текущему пользователю
        """
        return ReferenceCategory.objects.filter(photographer=self.request.user)

class CategoryCreateView(LoginRequiredMixin, CreateView):
    """
    Представление для создания новой категории референсов
    """
    model = ReferenceCategory
    form_class = CategoryForm
    template_name = 'references/category_form.html'
    success_url = reverse_lazy('references:category_list')
    
    def form_valid(self, form):
        """
        Устанавливаем текущего пользователя как фотографа
        """
        form.instance.photographer = self.request.user
        messages.success(self.request, 'Категория успешно создана!')
        return super().form_valid(form)

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    """
    Представление для редактирования категории референсов
    """
    model = ReferenceCategory
    form_class = CategoryForm
    template_name = 'references/category_form.html'
    success_url = reverse_lazy('references:category_list')
    
    def get_queryset(self):
        """
        Фильтрация категорий по текущему пользователю
        """
        return ReferenceCategory.objects.filter(photographer=self.request.user)
    
    def form_valid(self, form):
        """
        Добавляем сообщение об успешном обновлении
        """
        messages.success(self.request, 'Категория успешно обновлена!')
        return super().form_valid(form)

class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    """
    Представление для удаления категории референсов
    """
    model = ReferenceCategory
    template_name = 'references/category_confirm_delete.html'
    success_url = reverse_lazy('references:category_list')
    
    def get_queryset(self):
        """
        Фильтрация категорий по текущему пользователю
        """
        return ReferenceCategory.objects.filter(photographer=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        """
        Добавляем сообщение об успешном удалении
        """
        messages.success(self.request, 'Категория успешно удалена!')
        return super().delete(request, *args, **kwargs)

class ReferenceListView(LoginRequiredMixin, ListView):
    """
    Представление для отображения списка референсов
    """
    model = Reference
    template_name = 'references/reference_list.html'
    context_object_name = 'references'
    
    def get_queryset(self):
        """
        Фильтрация референсов по текущему пользователю
        """
        return Reference.objects.filter(photographer=self.request.user)
    
    def get_context_data(self, **kwargs):
        """
        Добавляем категории в контекст
        """
        context = super().get_context_data(**kwargs)
        context['categories'] = ReferenceCategory.objects.filter(photographer=self.request.user)
        return context

class ReferencesByCategoryView(LoginRequiredMixin, ListView):
    """
    Представление для отображения референсов по категории
    """
    model = Reference
    template_name = 'references/reference_list.html'
    context_object_name = 'references'
    
    def get_queryset(self):
        """
        Фильтрация референсов по категории и текущему пользователю
        """
        self.category = get_object_or_404(ReferenceCategory, pk=self.kwargs['category_id'], photographer=self.request.user)
        return Reference.objects.filter(photographer=self.request.user, category=self.category)
    
    def get_context_data(self, **kwargs):
        """
        Добавляем категории и текущую категорию в контекст
        """
        context = super().get_context_data(**kwargs)
        context['categories'] = ReferenceCategory.objects.filter(photographer=self.request.user)
        context['current_category'] = self.category
        return context

class ReferenceDetailView(LoginRequiredMixin, DetailView):
    """
    Представление для отображения деталей референса
    """
    model = Reference
    template_name = 'references/reference_detail.html'
    context_object_name = 'reference'
    
    def get_queryset(self):
        """
        Фильтрация референсов по текущему пользователю
        """
        return Reference.objects.filter(photographer=self.request.user)
    
    def get_context_data(self, **kwargs):
        """
        Добавляем похожие референсы в контекст
        """
        context = super().get_context_data(**kwargs)
        reference = self.object
        
        # Получаем похожие референсы (из той же категории, исключая текущий)
        related_references = []
        if reference.category:
            related_references = Reference.objects.filter(
                photographer=self.request.user,
                category=reference.category
            ).exclude(pk=reference.pk)[:4]
        
        # Если недостаточно похожих референсов, добавляем другие
        if len(related_references) < 4:
            other_references = Reference.objects.filter(
                photographer=self.request.user
            ).exclude(pk=reference.pk)
            
            if reference.category:
                other_references = other_references.exclude(category=reference.category)
            
            related_references = list(related_references) + list(other_references[:4 - len(related_references)])
        
        context['related_references'] = related_references
        return context

class ReferenceCreateView(LoginRequiredMixin, CreateView):
    """
    Представление для создания нового референса
    """
    model = Reference
    form_class = ReferenceForm
    template_name = 'references/reference_form.html'
    
    def get_form(self, form_class=None):
        """
        Фильтрация категорий по текущему пользователю
        """
        form = super().get_form(form_class)
        form.fields['category'].queryset = ReferenceCategory.objects.filter(photographer=self.request.user)
        return form
    
    def form_valid(self, form):
        """
        Устанавливаем текущего пользователя как фотографа
        """
        form.instance.photographer = self.request.user
        messages.success(self.request, 'Референс успешно добавлен!')
        return super().form_valid(form)
    
    def get_success_url(self):
        """
        Возвращаем URL для перенаправления после успешного создания
        """
        return reverse('references:reference_detail', kwargs={'pk': self.object.pk})

class ReferenceUpdateView(LoginRequiredMixin, UpdateView):
    """
    Представление для редактирования референса
    """
    model = Reference
    form_class = ReferenceForm
    template_name = 'references/reference_form.html'
    
    def get_queryset(self):
        """
        Фильтрация референсов по текущему пользователю
        """
        return Reference.objects.filter(photographer=self.request.user)
    
    def get_form(self, form_class=None):
        """
        Фильтрация категорий по текущему пользователю
        """
        form = super().get_form(form_class)
        form.fields['category'].queryset = ReferenceCategory.objects.filter(photographer=self.request.user)
        return form
    
    def form_valid(self, form):
        """
        Добавляем сообщение об успешном обновлении
        """
        messages.success(self.request, 'Референс успешно обновлен!')
        return super().form_valid(form)
    
    def get_success_url(self):
        """
        Возвращаем URL для перенаправления после успешного обновления
        """
        return reverse('references:reference_detail', kwargs={'pk': self.object.pk})

class ReferenceDeleteView(LoginRequiredMixin, DeleteView):
    """
    Представление для удаления референса
    """
    model = Reference
    template_name = 'references/reference_confirm_delete.html'
    success_url = reverse_lazy('references:reference_list')
    
    def get_queryset(self):
        """
        Фильтрация референсов по текущему пользователю
        """
        return Reference.objects.filter(photographer=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        """
        Добавляем сообщение об успешном удалении
        """
        messages.success(self.request, 'Референс успешно удален!')
        return super().delete(request, *args, **kwargs)

@login_required
def reference_search(request):
    """
    Представление для поиска референсов
    """
    form = ReferenceSearchForm(request.GET, user=request.user)
    references = Reference.objects.filter(photographer=request.user)

    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')

        if query:
            references = references.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )

        if category:
            references = references.filter(category=category)

    return render(request, 'references/reference_search.html', {
        'form': form,
        'references': references,
        'categories': ReferenceCategory.objects.filter(photographer=request.user)
    })

