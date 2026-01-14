document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing map...');

    const locationTypeFilter = document.getElementById('location-type-filter');
    const cityFilter = document.getElementById('city-filter');
    const searchInput = document.getElementById('studio-search');
    const studiosContainer = document.getElementById('studios-container');
    const studioItems = document.querySelectorAll('.studio-item');
    const mapToggleBtn = document.getElementById('map-toggle-btn');
    const fullscreenBtn = document.getElementById('fullscreen-btn');
    const closeFullscreenTop = document.getElementById('close-fullscreen-top');
    const mapContainer = document.getElementById('map-container');
    const fullscreenOverlay = document.getElementById('fullscreen-overlay');

    console.log('Studios data received:', studiosData);

    // Убираем дубликаты городов в фильтре
    const cityOptions = new Set();
    const options = cityFilter.querySelectorAll('option');
    options.forEach(option => {
        if (option.value === 'all') return;
        if (cityOptions.has(option.value)) {
            option.remove();
        } else {
            cityOptions.add(option.value);
        }
    });

    // Инициализация карты
    let map = null;
    let markers = {};
    let mapVisible = true;
    let isFullscreen = false;

    // Ждем полной загрузки API карт
    if (typeof ymaps !== 'undefined') {
        console.log('Yandex Maps API loaded, initializing...');
        ymaps.ready(initMap);
    } else {
        console.error('Yandex Maps API not loaded');
    }

    function initMap() {
        try {
            console.log('Initializing map...');

            // Центр по умолчанию - Челябинск
            let center = [55.1603236, 61.3683525];
            let zoom = 12;

            // Пытаемся получить местоположение пользователя
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        center = [position.coords.latitude, position.coords.longitude];
                        zoom = 12;
                        createMap(center, zoom);
                    },
                    function(error) {
                        console.log('Geolocation error, using default center');
                        createMap(center, zoom);
                    }
                );
            } else {
                createMap(center, zoom);
            }

        } catch (error) {
            console.error('Error initializing map:', error);
        }
    }

    function createMap(center, zoom) {
        map = new ymaps.Map('map', {
            center: center,
            zoom: zoom,
            controls: ['zoomControl', 'fullscreenControl']
        });

        console.log('Map created with center:', center);

        // Добавляем маркеры для каждой студии
        studiosData.forEach(studio => {
            if (studio.latitude && studio.longitude) {
                addMarker(studio);
            } else {
                console.log('Studio missing coordinates:', studio.name);
            }
        });

        console.log('Markers added, map should be visible now');

        // Принудительный ресайз карты
        setTimeout(() => {
            if (map) {
                map.container.fitToViewport();
                console.log('Map resized');
            }
        }, 500);
    }

    function addMarker(studio) {
        try {
            const placemark = new ymaps.Placemark(
                [parseFloat(studio.latitude), parseFloat(studio.longitude)],
                {
                    balloonContentHeader: studio.name,
                    balloonContentBody: `
                        <div style="max-width: 250px;">
                            <p><strong>Адрес:</strong> ${studio.address || ''}</p>
                            <p><strong>Город:</strong> ${studio.city || ''}</p>
                        </div>
                    `,
                    hintContent: studio.name
                },
                {
                    preset: studio.location_type === 'studio' ? 'islands#blueHomeIcon' : 'islands#greenIcon',
                    iconColor: studio.location_type === 'studio' ? '#0095b6' : '#56db40'
                }
            );

            // При клике на маркер прокручиваем к карточке
            placemark.events.add('click', function() {
                scrollToStudioCard(studio.id);
                // Открываем балун при клике
                placemark.balloon.open();
            });

            if (map) {
                map.geoObjects.add(placemark);
                markers[studio.id] = placemark;
                console.log('Marker added for:', studio.name);
            }
        } catch (error) {
            console.error('Error adding marker for studio:', studio.id, error);
        }
    }

    // ФУНКЦИИ ДЛЯ ПОЛНОЭКРАННОГО РЕЖИМА
    function enterFullscreen() {
        mapContainer.classList.add('fullscreen');
        document.body.classList.add('map-fullscreen');
        fullscreenOverlay.classList.add('active');
        closeFullscreenTop.style.display = 'flex';
        isFullscreen = true;

        // Ресайз карты после входа в полноэкранный режим
        setTimeout(() => {
            if (map) {
                map.container.fitToViewport();
            }
        }, 300);
    }

    function exitFullscreen() {
        mapContainer.classList.remove('fullscreen');
        document.body.classList.remove('map-fullscreen');
        fullscreenOverlay.classList.remove('active');
        closeFullscreenTop.style.display = 'none';
        isFullscreen = false;

        // Ресайз карты после выхода из полноэкранного режима
        setTimeout(() => {
            if (map) {
                map.container.fitToViewport();
            }
        }, 300);
    }

    // Обработчик кнопки полноэкранного режима
    fullscreenBtn.addEventListener('click', function() {
        enterFullscreen();
    });

    // Обработчик кнопки закрытия полноэкранного режима (вверху страницы)
    closeFullscreenTop.addEventListener('click', function() {
        exitFullscreen();
    });

    // Выход из полноэкранного режима по ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && isFullscreen) {
            exitFullscreen();
        }
    });

    // Выход из полноэкранного режима по клику на оверлей
    fullscreenOverlay.addEventListener('click', function() {
        if (isFullscreen) {
            exitFullscreen();
        }
    });

    function scrollToStudioCard(studioId) {
        const studioCard = document.querySelector(`[data-studio-id="${studioId}"]`);
        if (studioCard) {
            highlightCard(studioId);

            const headerOffset = 100;
            const elementPosition = studioCard.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });
        }
    }

    function highlightCard(studioId) {
        studioItems.forEach(item => {
            item.classList.remove('highlighted');
        });

        const studioCard = document.querySelector(`[data-studio-id="${studioId}"]`);
        if (studioCard) {
            studioCard.classList.add('highlighted');
            setTimeout(() => {
                studioCard.classList.remove('highlighted');
            }, 3000);
        }
    }

    // При наведении на карточку подсвечиваем маркер
    studioItems.forEach(item => {
        const studioId = parseInt(item.dataset.studioId);

        item.addEventListener('mouseenter', function() {
            if (markers[studioId]) {
                markers[studioId].options.set('iconColor', '#e8b4c8');
            }
        });

        item.addEventListener('mouseleave', function() {
            if (markers[studioId]) {
                const studio = studiosData.find(s => s.id === studioId);
                if (studio) {
                    const originalColor = studio.location_type === 'studio' ? '#0095b6' : '#56db40';
                    markers[studioId].options.set('iconColor', originalColor);
                }
            }
        });
    });

    // Обратная навигация: "Показать на карте"
    document.querySelectorAll('.show-on-map-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const studioId = parseInt(this.dataset.studioId);
            showStudioOnMap(studioId);
        });
    });

    function showStudioOnMap(studioId) {
        const studio = studiosData.find(s => s.id === studioId);
        const marker = markers[studioId];

        if (!studio || !marker || !map) return;

        // 1. Карта плавно скроллится вверх (если она скрыта)
        if (mapContainer.classList.contains('hidden')) {
            mapContainer.classList.remove('hidden');
            mapToggleBtn.innerHTML = '<i class="fas fa-eye-slash"></i> Скрыть карту';
            mapVisible = true;
            // Даем время на анимацию
            setTimeout(() => {
                map.container.fitToViewport();
                centerAndHighlightMarker(studio, marker);
            }, 300);
        } else {
            centerAndHighlightMarker(studio, marker);
        }

        // 2. Скроллим к карте (только если не в полноэкранном режиме)
        if (!isFullscreen) {
            window.scrollTo({
                top: mapContainer.offsetTop - 80,
                behavior: 'smooth'
            });
        }
    }

    function centerAndHighlightMarker(studio, marker) {
        // 3. Карта центрируется на маркере этой студии
        map.setCenter([studio.latitude, studio.longitude], 15, {
            duration: 500
        });

        // 4. Маркер этой студии подсвечивается
        const originalColor = studio.location_type === 'studio' ? '#0095b6' : '#56db40';
        marker.options.set('iconColor', '#e8b4c8');
        marker.options.set('preset', 'islands#redIcon');

        // 5. Через 3 секунды подсветка снимается
        setTimeout(() => {
            const originalPreset = studio.location_type === 'studio' ? 'islands#blueHomeIcon' : 'islands#greenIcon';
            marker.options.set('iconColor', originalColor);
            marker.options.set('preset', originalPreset);
        }, 3000);
    }

    // Кнопка скрытия/показа карты
    if (mapToggleBtn) {
        mapToggleBtn.addEventListener('click', function() {
            // Не позволяем скрыть карту в полноэкранном режиме
            if (isFullscreen) {
                exitFullscreen();
                return;
            }

            mapVisible = !mapVisible;

            if (mapVisible) {
                mapContainer.classList.remove('hidden');
                mapToggleBtn.innerHTML = '<i class="fas fa-eye-slash"></i> Скрыть карту';
                // Ресайз при показе карты
                setTimeout(() => {
                    if (map) {
                        map.container.fitToViewport();
                    }
                }, 300);
            } else {
                mapContainer.classList.add('hidden');
                mapToggleBtn.innerHTML = '<i class="fas fa-eye"></i> Показать карту';
            }
        });
    }

    // Фильтрация студий
    function filterStudios() {
        const locationType = locationTypeFilter.value;
        const city = cityFilter.value;
        const searchText = searchInput.value.toLowerCase();

        studioItems.forEach(item => {
            const itemLocationType = item.dataset.locationType;
            const itemCity = item.dataset.city;
            const itemText = item.textContent.toLowerCase();
            const studioId = parseInt(item.dataset.studioId);

            const locationTypeMatch = locationType === 'all' || itemLocationType === locationType;
            const cityMatch = city === 'all' || itemCity === city;
            const searchMatch = searchText === '' || itemText.includes(searchText);

            const isVisible = locationTypeMatch && cityMatch && searchMatch;

            item.style.display = isVisible ? '' : 'none';

            // Скрываем/показываем маркеры на карте
            if (markers[studioId]) {
                markers[studioId].options.set('visible', isVisible);
            }
        });

        // Показываем сообщение, если ничего не найдено
        const visibleItems = Array.from(studioItems).filter(i => i.style.display !== 'none');
        let noResultsElement = document.getElementById('no-results-message');

        if (visibleItems.length === 0) {
            if (!noResultsElement) {
                noResultsElement = document.createElement('div');
                noResultsElement.id = 'no-results-message';
                noResultsElement.className = 'col-12';
                noResultsElement.innerHTML = `
                    <div class="alert alert-info">
                        <p class="mb-0 text-center">По вашему запросу ничего не найдено</p>
                    </div>
                `;
                studiosContainer.appendChild(noResultsElement);
            }
        } else if (noResultsElement) {
            noResultsElement.remove();
        }

        // Обновляем границы карты для видимых маркеров
        updateMapBounds();
    }

    function updateMapBounds() {
        if (!map) return;

        const visibleBounds = [];

        studiosData.forEach(studio => {
            if (!studio.latitude || !studio.longitude) return;

            const studioCard = document.querySelector(`[data-studio-id="${studio.id}"]`);
            if (studioCard && studioCard.style.display !== 'none') {
                visibleBounds.push([parseFloat(studio.latitude), parseFloat(studio.longitude)]);
            }
        });

        if (visibleBounds.length > 0) {
            map.setBounds(visibleBounds, {
                checkZoomRange: true,
                zoomMargin: 50,
                duration: 500
            });
        } else {
            // Если ничего не видно, возвращаем к виду по умолчанию
            const center = [55.1603236, 61.3683525];
            map.setCenter(center, 10);
        }
    }

    // Обработчики событий для фильтров
    if (locationTypeFilter) locationTypeFilter.addEventListener('change', filterStudios);
    if (cityFilter) cityFilter.addEventListener('change', filterStudios);
    if (searchInput) searchInput.addEventListener('input', filterStudios);
});