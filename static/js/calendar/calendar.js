document.addEventListener('DOMContentLoaded', function () {
    const calendarEl = document.getElementById('calendar');
    const eventsData = JSON.parse(calendarEl.dataset.events);

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay,listMonth'
        },
        locale: 'ru',
        timeZone: 'local',
        navLinks: true,
        editable: true,
        selectable: true,
        nowIndicator: true,
        dayMaxEvents: true,
        eventTimeFormat: {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        },
        events: eventsData,
        eventDidMount: function (info) {
            info.el.addEventListener('mouseover', function (e) {
                showEventTooltip(e, info.event);
            });
            info.el.addEventListener('mouseout', hideEventTooltip);
        },
        /*dateClick: function (info) {
            const date = info.dateStr;
            window.location.href = `/calendar/add/?date=${date}`;
        },*/
        eventDrop: function (info) {
            alert(`Событие "${info.event.title}" перемещено на ${info.event.startStr}`);
        },
        eventResize: function (info) {
            alert(`Продолжительность события "${info.event.title}" изменена`);
        }
    });

    calendar.render();

    function showEventTooltip(e, event) {
        const tooltip = document.getElementById('eventTooltip');
        tooltip.querySelector('.event-tooltip-title').textContent = event.title;
        tooltip.querySelector('.event-tooltip-type').textContent = event.extendedProps.event_type_display;

        toggleTooltipField('client', event.extendedProps.client);
        toggleTooltipField('studio', event.extendedProps.studio);
        toggleTooltipField('description', event.extendedProps.description);

        const timeText = event.allDay
            ? 'Весь день'
            : `${formatTime(event.start)} - ${formatTime(event.end)}`;
        tooltip.querySelector('.event-tooltip-time').textContent = timeText;
        tooltip.querySelector('.event-tooltip-time-container').style.display = 'block';

        tooltip.style.left = e.pageX + 10 + 'px';
        tooltip.style.top = e.pageY + 10 + 'px';
        tooltip.style.display = 'block';
    }

    function hideEventTooltip() {
        document.getElementById('eventTooltip').style.display = 'none';
    }

    function toggleTooltipField(fieldName, value) {
        const container = document.querySelector(`.event-tooltip-${fieldName}-container`);
        const span = document.querySelector(`.event-tooltip-${fieldName}`);
        if (value) {
            span.textContent = value;
            container.style.display = 'block';
        } else {
            container.style.display = 'none';
        }
    }

    function formatTime(date) {
        return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
});
