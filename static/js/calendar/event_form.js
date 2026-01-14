document.addEventListener('DOMContentLoaded', function() {
    const startDatepicker = flatpickr("#id_start_datetime", {
        enableTime: true,
        dateFormat: "Y-m-d H:i",
        locale: "ru",
        time_24hr: true,
        minuteIncrement: 15,
        onChange: function(selectedDates, dateStr) {
            endDatepicker.set('minDate', dateStr);
            if (endDatepicker.selectedDates[0] < selectedDates[0]) {
                const endDate = new Date(selectedDates[0]);
                endDate.setHours(endDate.getHours() + 1);
                endDatepicker.setDate(endDate);
            }
        }
    });

    const endDatepicker = flatpickr("#id_end_datetime", {
        enableTime: true,
        dateFormat: "Y-m-d H:i",
        locale: "ru",
        time_24hr: true,
        minuteIncrement: 15,
        minDate: startDatepicker.selectedDates[0] || new Date()
    });

    const allDayCheckbox = document.getElementById("id_is_all_day");
    allDayCheckbox.addEventListener('change', function() {
        const enable = !this.checked;
        startDatepicker.set('enableTime', enable);
        startDatepicker.set('dateFormat', enable ? "Y-m-d H:i" : "Y-m-d");
        endDatepicker.set('enableTime', enable);
        endDatepicker.set('dateFormat', enable ? "Y-m-d H:i" : "Y-m-d");
        startDatepicker.redraw();
        endDatepicker.redraw();
    });

    const colorInput = document.getElementById("id_color");
    const colorOptions = document.querySelectorAll('.color-option');
    colorOptions.forEach(option => {
        if (option.getAttribute('data-color') === colorInput.value) {
            option.classList.add('selected');
        }
        option.addEventListener('click', function() {
            colorOptions.forEach(opt => opt.classList.remove('selected'));
            this.classList.add('selected');
            colorInput.value = this.getAttribute('data-color');
        });
    });

    const urlParams = new URLSearchParams(window.location.search);
    const dateParam = urlParams.get('date');
    if (dateParam && !startDatepicker.selectedDates[0]) {
        startDatepicker.setDate(dateParam);
        const endDate = new Date(dateParam);
        endDate.setHours(endDate.getHours() + 1);
        endDatepicker.setDate(endDate);
    }

    const searchInput = document.getElementById('client-search');
    const clientSelect = document.getElementById('client-select');

    // При загрузке заполняем input текущим клиентом
    const selectedOption = clientSelect.querySelector('option:checked');
    if (selectedOption) {
        searchInput.value = selectedOption.textContent;
    }

    // Поиск по имени
    searchInput.addEventListener('keyup', function () {
        const text = searchInput.value.toLowerCase();
        let matched = false;

        Array.from(clientSelect.options).forEach(option => {
            const name = option.dataset.name.toLowerCase();
            if (name.includes(text)) {
                option.selected = true;
                matched = true;
            } else {
                option.selected = false;
            }
        });

        if (!matched) {
            clientSelect.value = '';
        }
    });





});
$(document).ready(function() {
        $('.select2').select2({
            placeholder: 'Начните вводить...',
            allowClear: true,
            width: '100%'
        });
    });