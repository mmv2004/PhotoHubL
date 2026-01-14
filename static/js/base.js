document.addEventListener('DOMContentLoaded', function() {
            // Переключение боковой панели
            const sidebar = document.getElementById('sidebar');
            const sidebarToggle = document.getElementById('sidebar-toggle');
            const sidebarText = document.querySelectorAll('.sidebar-text');
            const content = document.querySelector('.content');

            if (sidebarToggle) {
                sidebarToggle.addEventListener('click', function() {
                    if (sidebar.classList.contains('sidebar-expanded')) {
                        sidebar.classList.remove('sidebar-expanded');
                        sidebar.classList.add('sidebar-collapsed');
                        sidebarToggle.innerHTML = '<i class="fas fa-chevron-right"></i>';
                        sidebarText.forEach(text => text.style.display = 'none');
                        content.style.width = 'calc(100% - 60px)';
                    } else {
                        sidebar.classList.remove('sidebar-collapsed');
                        sidebar.classList.add('sidebar-expanded');
                        sidebarToggle.innerHTML = '<i class="fas fa-chevron-left"></i>';
                        sidebarText.forEach(text => text.style.display = 'inline');
                        content.style.width = 'calc(100% - 250px)';
                    }
                });
            }

            // Мобильное меню
            const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');

            if (mobileMenuToggle) {
                mobileMenuToggle.addEventListener('click', function() {
                    sidebar.classList.toggle('show');
                });
            }

            // Слайдер для изображений студий
            const sliders = document.querySelectorAll('.studio-slider');

            sliders.forEach(slider => {
                const inner = slider.querySelector('.studio-slider-inner');
                const items = slider.querySelectorAll('.studio-slider-item');
                const prevBtn = slider.querySelector('.studio-slider-prev');
                const nextBtn = slider.querySelector('.studio-slider-next');
                let currentIndex = 0;

                if (prevBtn && nextBtn) {
                    prevBtn.addEventListener('click', function() {
                        if (currentIndex > 0) {
                            currentIndex--;
                            updateSlider();
                        }
                    });

                    nextBtn.addEventListener('click', function() {
                        if (currentIndex < items.length - 1) {
                            currentIndex++;
                            updateSlider();
                        }
                    });

                    function updateSlider() {
                        inner.style.transform = `translateX(-${currentIndex * 100}%)`;
                    }
                }
            });
        });