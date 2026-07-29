import calendar
from datetime import date, timedelta
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout
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

def logout_view(request):
    auth_logout(request)
    return redirect("login")

class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        now = timezone.now()
        calendars = FamilyCalendar.objects.filter(family__members__user=request.user)
        partial = request.GET.get('partial')

        if partial == 'today':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
            events = Event.objects.filter(calendar__in=calendars, start_time__gte=start, start_time__lt=end, is_cancelled=False).order_by('start_time')
            return render(request, 'web/partials/today_events.html', {'today_events': events})

        if partial == 'upcoming':
            events = Event.objects.filter(calendar__in=calendars, start_time__gte=now, is_cancelled=False).exclude(start_time__date=now.date()).order_by('start_time')[:10]
            return render(request, 'web/partials/upcoming_events.html', {'upcoming_events': events})

        return render(request, 'web/dashboard.html', {'calendars': calendars})

class MonthCalendarView(LoginRequiredMixin, View):
    def get(self, request):
        year = int(request.GET.get('year', timezone.now().year))
        month = int(request.GET.get('month', timezone.now().month))

        cal = calendar.Calendar()
        month_days = cal.monthdays2calendar(year, month)

        calendars = FamilyCalendar.objects.filter(family__members__user=request.user)
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

        ctx = {
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
        }
        return render(request, 'web/calendar.html', ctx)

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

class FamilyListView(LoginRequiredMixin, View):
    def get(self, request):
        from accounts.models import Family, FamilyMember
        memberships = FamilyMember.objects.filter(user=request.user).select_related('family', 'user')
        families = {}
        for m in memberships:
            all_members = FamilyMember.objects.filter(family=m.family).select_related('user')
            families[m.family] = all_members
        return render(request, 'web/family.html', {'families': families})

import requests
from django.conf import settings
from django.urls import reverse
from sync.models import SyncProvider

class SettingsView(LoginRequiredMixin, View):
    def get(self, request):
        providers = SyncProvider.objects.filter(user=request.user)
        return render(request, 'web/settings.html', {'providers': providers})

class GoogleAuthStartView(LoginRequiredMixin, View):
    def get(self, request):
        from urllib.parse import urlencode
        params = {
            'client_id': settings.GOOGLE_CLIENT_ID,
            'redirect_uri': settings.GOOGLE_REDIRECT_URI,
            'response_type': 'code',
            'scope': 'https://www.googleapis.com/auth/calendar.readonly email',
            'access_type': 'offline',
            'prompt': 'consent',
            'state': request.user.id,
        }
        url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urlencode(params)
        return redirect(url)

class GoogleAuthCallbackView(View):
    def get(self, request):
        code = request.GET.get('code')
        error = request.GET.get('error')
        if error or not code:
            return redirect(reverse('settings') + '?error=' + (error or 'no_code'))

        try:
            resp = requests.post('https://oauth2.googleapis.com/token', data={
                'client_id': settings.GOOGLE_CLIENT_ID,
                'client_secret': settings.GOOGLE_CLIENT_SECRET,
                'redirect_uri': settings.GOOGLE_REDIRECT_URI,
                'grant_type': 'authorization_code',
                'code': code,
            }, timeout=30)
            data = resp.json()
            if 'access_token' not in data:
                return redirect(reverse('settings') + '?error=token_exchange_failed')

            from django.contrib.auth import login
            user_id = request.GET.get('state')
            if user_id:
                from django.contrib.auth.models import User
                user = User.objects.filter(id=user_id).first()
                if user and not request.user.is_authenticated:
                    login(request, user)

            user = request.user
            if not user.is_authenticated:
                return redirect(reverse('login'))

            provider, created = SyncProvider.objects.get_or_create(
                user=user,
                provider_type='google',
                defaults={
                    'sync_mode': 'import',
                    'is_enabled': True,
                }
            )
            provider.credentials = {
                'access_token': data.get('access_token'),
                'refresh_token': data.get('refresh_token'),
                'expires_in': data.get('expires_in', 3600),
                'scope': data.get('scope', ''),
            }
            provider.provider_user = data.get('email', data.get('access_token', '')[:20])
            provider.save()

            return redirect(reverse('settings') + '?success=google_connected')

        except Exception as e:
            return redirect(reverse('settings') + '?error=' + str(e))

class GoogleDisconnectView(LoginRequiredMixin, View):
    def post(self, request):
        SyncProvider.objects.filter(user=request.user, provider_type='google').delete()
        return redirect(reverse('settings') + '?success=google_disconnected')
