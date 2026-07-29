import calendar
from datetime import date, timedelta
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View
from django.utils import timezone
from django.http import HttpResponse
from events.models import Event, Calendar as FamilyCalendar

class LoginView(auth_views.LoginView):
    template_name = 'web/login.html'
    next_page = reverse_lazy('dashboard')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().get(request, *args, **kwargs)

logout_view = auth_views.LogoutView.as_view(next_page=reverse_lazy('login'))

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'web/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        now = timezone.now()
        calendars = FamilyCalendar.objects.filter(family__members__user=self.request.user)
        ctx['calendars'] = calendars
        if self.request.GET.get('partial') == 'today':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
            events = Event.objects.filter(calendar__in=calendars, start_time__gte=start, start_time__lt=end, is_cancelled=False).order_by('start_time')
            ctx['today_events'] = events
            return render(self.request, 'web/partials/today_events.html', ctx)
        if self.request.GET.get('partial') == 'upcoming':
            events = Event.objects.filter(calendar__in=calendars, start_time__gte=now, is_cancelled=False).exclude(start_time__date=now.date()).order_by('start_time')[:10]
            ctx['upcoming_events'] = events
            return render(self.request, 'web/partials/upcoming_events.html', ctx)
        return ctx

class MonthCalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'web/calendar.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        year = int(self.request.GET.get('year', timezone.now().year))
        month = int(self.request.GET.get('month', timezone.now().month))

        cal = calendar.Calendar()
        month_days = cal.monthdays2calendar(year, month)

        calendars = FamilyCalendar.objects.filter(family__members__user=self.request.user)
        month_start = date(year, month, 1)
        if month == 12:
            month_end = date(year + 1, 1, 1)
        else:
            month_end = date(year, month + 1, 1)

        events = Event.objects.filter(
            calendar__in=calendars,
            start_time__gte=timezone.make_aware(timezone.datetime.combine(month_start, timezone.datetime.min.time())),
            start_time__lt=timezone.make_aware(timezone.datetime.combine(month_end, timezone.datetime.min.time())),
            is_cancelled=False,
        )

        events_by_day = {}
        for e in events:
            d = e.start_time.astimezone(timezone.get_current_timezone()).day
            events_by_day.setdefault(d, []).append(e)

        ctx.update({
            'year': year,
            'month': month,
            'month_name': calendar.month_name[month],
            'month_days': month_days,
            'events_by_day': events_by_day,
            'prev_month': month - 1 if month > 1 else 12,
            'prev_year': year if month > 1 else year - 1,
            'next_month': month + 1 if month < 12 else 1,
            'next_year': year if month < 12 else year + 1,
            'today': timezone.now().astimezone(timezone.get_current_timezone()).date(),
        })
        return ctx

class EventCreateHtmxView(LoginRequiredMixin, View):
    def post(self, request):
        from django.utils.dateparse import parse_datetime
        try:
            title = request.POST.get('title', '')
            start_str = request.POST.get('start_time', '')
            end_str = request.POST.get('end_time', '')
            description = request.POST.get('description', '')
            calendars = FamilyCalendar.objects.filter(family__members__user=request.user)
            if not calendars.exists():
                return HttpResponse('No tenes calendarios disponibles', status=400)
            cal = calendars.first()
            start = parse_datetime(start_str)
            end = parse_datetime(end_str)
            if not start or not end:
                return HttpResponse('Fechas invalidas', status=400)
            Event.objects.create(
                calendar=cal,
                title=title,
                description=description,
                start_time=start,
                end_time=end,
                created_by=request.user,
            )
            messages.success(request, 'Evento creado!')
            return HttpResponse(status=201)
        except Exception as e:
            return HttpResponse(f'Error: {e}', status=400)
