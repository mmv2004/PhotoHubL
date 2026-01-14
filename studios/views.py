from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.db.models import Q
import json

from .models import Studio, StudioImage
from .forms import StudioForm, StudioImageForm, StudioSearchForm
from .geocoding import reverse_geocode_yandex

class StudioListView(LoginRequiredMixin, ListView):
    """
    Представление для отображения списка студий и мест для съемок
    """
    model = Studio
    template_name = 'studios/studio_list.html'
    context_object_name = 'studios'

    def get_queryset(self):
        """
        Показываем публичные студии и студии, созданные пользователем
        """
        return Studio.objects.filter(is_public=True) | Studio.objects.filter(created_by=self.request.user)

    def get_context_data(self, **kwargs):
        """
        Добавляем форму поиска в контекст
        """
        context = super().get_context_data(**kwargs)
        context['search_form'] = StudioSearchForm(self.request.GET)

        # Добавляем JSON данные для карты
        studios_data = []
        for studio in context['studios']:
            if studio.latitude and studio.longitude:
                main_image = studio.images.filter(is_main=True).first()
                if not main_image:
                    main_image = studio.images.first()

                studios_data.append({
                    'id': studio.id,
                    'name': studio.name,
                    'latitude': studio.latitude,
                    'longitude': studio.longitude,
                    'location_type': studio.location_type,
                    'city': studio.city,
                    'address': studio.get_full_address(),
                    'image_url': main_image.image.url if main_image else None,
                })

        context['studios_json'] = json.dumps(studios_data)
        return context

class StudioDetailView(LoginRequiredMixin, DetailView):
    """
    Представление для отображения деталей студии
    """
    model = Studio
    template_name = 'studios/studio_detail.html'
    context_object_name = 'studio'

    def get_queryset(self):
        """
        Показываем публичные студии и студии, созданные пользователем
        """
        return Studio.objects.filter(is_public=True) | Studio.objects.filter(created_by=self.request.user)

    def get_context_data(self, **kwargs):
        """
        Добавляем изображения студии в контекст
        """
        context = super().get_context_data(**kwargs)
        context['images'] = self.object.images.all()
        return context

class StudioCreateView(LoginRequiredMixin, CreateView):
    """
    Представление для создания новой студии
    """
    model = Studio
    form_class = StudioForm
    template_name = 'studios/studio_form.html'

    def form_valid(self, form):
        """
        Устанавливаем текущего пользователя как создателя
        """
        form.instance.created_by = self.request.user

        # Координаты и полный адрес должны быть заполнены на фронтенде.
        # Если город и район не заполнены (например, из-за ошибки геокодирования на фронте),
        # пытаемся определить их по координатам.
        if form.instance.latitude and form.instance.longitude and not form.instance.city:
            city, district = reverse_geocode_yandex(form.instance.latitude, form.instance.longitude)
            form.instance.city = city
            form.instance.district = district

        messages.success(self.request, 'Студия успешно добавлена!')
        return super().form_valid(form)

    def get_success_url(self):
        """
        Перенаправляем на страницу добавления изображений
        """
        return reverse('studios:studio_add_image', kwargs={'studio_id': self.object.pk})

class StudioUpdateView(LoginRequiredMixin, UpdateView):
    """
    Представление для редактирования студии
    """
    model = Studio
    form_class = StudioForm
    template_name = 'studios/studio_form.html'

    def get_queryset(self):
        """
        Разрешаем редактировать только студии, созданные пользователем
        """
        return Studio.objects.filter(created_by=self.request.user)

    def form_valid(self, form):
        """
        Добавляем сообщение об успешном обновлении
        """
        # Координаты и полный адрес должны быть заполнены на фронтенде.
        # Если город и район не заполнены (например, из-за ошибки геокодирования на фронте),
        # пытаемся определить их по координатам.
        if form.instance.latitude and form.instance.longitude and not form.instance.city:
            city, district = reverse_geocode_yandex(form.instance.latitude, form.instance.longitude)
            form.instance.city = city
            form.instance.district = district

        messages.success(self.request, 'Данные студии успешно обновлены!')
        return super().form_valid(form)

    def get_success_url(self):
        """
        Возвращаем URL для перенаправления после успешного обновления
        """
        return reverse('studios:studio_detail', kwargs={'pk': self.object.pk})

class StudioDeleteView(LoginRequiredMixin, DeleteView):
    """
    Представление для удаления студии
    """
    model = Studio
    template_name = 'studios/studio_confirm_delete.html'
    success_url = reverse_lazy('studios:studio_list')

    def get_queryset(self):
        """
        Разрешаем удалять только студии, созданные пользователем
        """
        return Studio.objects.filter(created_by=self.request.user)

    def delete(self, request, *args, **kwargs):
        """
        Добавляем сообщение об успешном удалении
        """
        messages.success(self.request, 'Студия успешно удалена!')
        return super().delete(request, *args, **kwargs)

class StudioImageCreateView(LoginRequiredMixin, CreateView):
    """
    Представление для добавления изображений к студии
    """
    model = StudioImage
    form_class = StudioImageForm
    template_name = 'studios/studio_image_form.html'

    def dispatch(self, request, *args, **kwargs):
        """
        Получаем студию и проверяем права доступа
        """
        self.studio = get_object_or_404(Studio, pk=kwargs['studio_id'])
        if not self.studio.is_public and self.studio.created_by != request.user:
            messages.error(request, 'У вас нет прав для добавления изображений к этой студии!')
            return redirect('studios:studio_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Устанавливаем студию для изображения
        """
        form.instance.studio = self.studio
        messages.success(self.request, 'Изображение успешно добавлено!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """
        Добавляем студию в контекст
        """
        context = super().get_context_data(**kwargs)
        context['studio'] = self.studio
        return context

    def get_success_url(self):
        """
        Возвращаем URL для перенаправления после успешного добавления
        """
        return reverse('studios:studio_detail', kwargs={'pk': self.studio.pk})

class StudioImageDeleteView(LoginRequiredMixin, DeleteView):
    """
    Представление для удаления изображения студии
    """
    model = StudioImage
    template_name = 'studios/studio_image_confirm_delete.html'

    def get_queryset(self):
        """
        Разрешаем удалять только изображения студий, созданных пользователем
        """
        return StudioImage.objects.filter(studio__created_by=self.request.user)

    def get_success_url(self):
        """
        Возвращаем URL для перенаправления после успешного удаления
        """
        messages.success(self.request, 'Изображение успешно удалено!')
        return reverse('studios:studio_detail', kwargs={'pk': self.object.studio.pk})

@login_required
def set_main_image(request, pk):
    """
    Функция для установки главного изображения студии
    """
    image = get_object_or_404(StudioImage, pk=pk)

    # Проверяем права доступа
    if image.studio.created_by != request.user:
        messages.error(request, 'У вас нет прав для изменения этого изображения!')
        return redirect('studios:studio_list')

    # Снимаем флаг главного изображения со всех изображений студии
    StudioImage.objects.filter(studio=image.studio).update(is_main=False)

    # Устанавливаем текущее изображение как главное
    image.is_main = True
    image.save()

    messages.success(request, 'Главное изображение успешно установлено!')
    return redirect('studios:studio_detail', pk=image.studio.pk)

@login_required
def studio_search(request):
    """
    Представление для поиска студий
    """
    form = StudioSearchForm(request.GET)
    studios = Studio.objects.filter(is_public=True) | Studio.objects.filter(created_by=request.user)

    if form.is_valid():
        query = form.cleaned_data.get('query')
        location_type = form.cleaned_data.get('location_type')
        city = form.cleaned_data.get('city')

        if query:
            studios = studios.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(city__icontains=query) |
                Q(street__icontains=query)
            )

        if location_type and location_type != 'all':
            studios = studios.filter(location_type=location_type)

        if city:
            studios = studios.filter(city__icontains=city)

    return render(request, 'studios/studio_search.html', {
        'form': form,
        'studios': studios
    })

