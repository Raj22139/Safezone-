from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta

from crime.models import Area, CrimeRecord, SearchHistory
from accounts.models import UserProfile


def is_admin(user):
    return user.is_authenticated and (user.is_staff or
           (hasattr(user, 'profile') and user.profile.role == 'admin'))

admin_required = user_passes_test(is_admin, login_url='/accounts/login/')


@login_required
@admin_required
def admin_dashboard(request):
    """Admin dashboard — overview stats and recent data."""
    total_users   = User.objects.count()
    total_records = CrimeRecord.objects.count()
    total_areas   = Area.objects.count()
    pending       = CrimeRecord.objects.filter(status='pending').count()
    total_searches= SearchHistory.objects.count()

    recent_records = CrimeRecord.objects.select_related('area').order_by('-created_at')[:8]
    recent_users   = User.objects.select_related('profile').order_by('-date_joined')[:5]

    # Crime type breakdown
    crime_breakdown = (
        CrimeRecord.objects
        .values('crime_type')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Top high-risk areas
    high_risk_areas = Area.objects.filter(risk_level='high').order_by('-risk_score')[:5]

    context = {
        'total_users':    total_users,
        'total_records':  total_records,
        'total_areas':    total_areas,
        'pending':        pending,
        'total_searches': total_searches,
        'recent_records': recent_records,
        'recent_users':   recent_users,
        'crime_breakdown':crime_breakdown,
        'high_risk_areas':high_risk_areas,
    }
    return render(request, 'admin_panel/dashboard.html', context)


# ── CRIME RECORDS CRUD ──

@login_required
@admin_required
def crime_list(request):
    """List all crime records with search + filter."""
    records = CrimeRecord.objects.select_related('area').order_by('-created_at')

    q          = request.GET.get('q', '')
    risk_filter= request.GET.get('risk', '')
    type_filter= request.GET.get('type', '')

    if q:
        records = records.filter(
            Q(area__name__icontains=q) | Q(description__icontains=q)
        )
    if risk_filter:
        records = records.filter(area__risk_level=risk_filter)
    if type_filter:
        records = records.filter(crime_type=type_filter)

    context = {
        'records':     records,
        'q':           q,
        'risk_filter': risk_filter,
        'type_filter': type_filter,
        'crime_types': CrimeRecord.CRIME_TYPE_CHOICES,
    }
    return render(request, 'admin_panel/crime_list.html', context)


@login_required
@admin_required
def crime_add(request):
    """Add a new crime record."""
    areas = Area.objects.filter(is_active=True).order_by('name')

    if request.method == 'POST':
        area_id      = request.POST.get('area')
        crime_type   = request.POST.get('crime_type')
        description  = request.POST.get('description')
        incident_date= request.POST.get('incident_date')
        severity     = request.POST.get('severity')

        if not all([area_id, crime_type, description, incident_date, severity]):
            messages.error(request, 'All fields are required.')
        else:
            area = get_object_or_404(Area, id=area_id)
            CrimeRecord.objects.create(
                area=area,
                crime_type=crime_type,
                description=description,
                incident_date=incident_date,
                severity=int(severity),
                added_by_admin=request.user,
                status='approved',
            )
            messages.success(request, f'Crime record for {area.name} added successfully!')
            return redirect('admin_panel:crime_list')

    context = {'areas': areas, 'crime_types': CrimeRecord.CRIME_TYPE_CHOICES}
    return render(request, 'admin_panel/crime_form.html', context)


@login_required
@admin_required
def crime_edit(request, pk):
    """Edit an existing crime record."""
    record = get_object_or_404(CrimeRecord, pk=pk)
    areas  = Area.objects.filter(is_active=True).order_by('name')

    if request.method == 'POST':
        record.area          = get_object_or_404(Area, id=request.POST.get('area'))
        record.crime_type    = request.POST.get('crime_type')
        record.description   = request.POST.get('description')
        record.incident_date = request.POST.get('incident_date')
        record.severity      = int(request.POST.get('severity', 5))
        record.status        = request.POST.get('status', 'approved')
        record.save()
        messages.success(request, 'Crime record updated successfully!')
        return redirect('admin_panel:crime_list')

    context = {
        'record':      record,
        'areas':       areas,
        'crime_types': CrimeRecord.CRIME_TYPE_CHOICES,
        'edit':        True,
    }
    return render(request, 'admin_panel/crime_form.html', context)


@login_required
@admin_required
def crime_delete(request, pk):
    """Delete a crime record."""
    record = get_object_or_404(CrimeRecord, pk=pk)
    if request.method == 'POST':
        name = str(record)
        record.delete()
        messages.success(request, f'Record "{name}" deleted.')
        return redirect('admin_panel:crime_list')
    return render(request, 'admin_panel/confirm_delete.html', {'object': record, 'type': 'Crime Record'})


# ── AREA CRUD ──

@login_required
@admin_required
def area_list(request):
    areas = Area.objects.all().order_by('-risk_score')
    q = request.GET.get('q', '')
    if q:
        areas = areas.filter(Q(name__icontains=q) | Q(city__icontains=q))
    return render(request, 'admin_panel/area_list.html', {'areas': areas, 'q': q})


@login_required
@admin_required
def area_add(request):
    if request.method == 'POST':
        Area.objects.create(
            name       = request.POST.get('name'),
            city       = request.POST.get('city'),
            state      = request.POST.get('state', ''),
            pincode    = request.POST.get('pincode', ''),
            risk_score = int(request.POST.get('risk_score', 0)),
            description= request.POST.get('description', ''),
        )
        messages.success(request, 'Area added successfully!')
        return redirect('admin_panel:area_list')
    return render(request, 'admin_panel/area_form.html', {})


@login_required
@admin_required
def area_edit(request, pk):
    area = get_object_or_404(Area, pk=pk)
    if request.method == 'POST':
        area.name        = request.POST.get('name')
        area.city        = request.POST.get('city')
        area.state       = request.POST.get('state', '')
        area.pincode     = request.POST.get('pincode', '')
        area.risk_score  = int(request.POST.get('risk_score', 0))
        area.description = request.POST.get('description', '')
        area.save()
        messages.success(request, f'{area.name} updated!')
        return redirect('admin_panel:area_list')
    return render(request, 'admin_panel/area_form.html', {'area': area, 'edit': True})


@login_required
@admin_required
def area_delete(request, pk):
    area = get_object_or_404(Area, pk=pk)
    if request.method == 'POST':
        area.delete()
        messages.success(request, 'Area deleted.')
        return redirect('admin_panel:area_list')
    return render(request, 'admin_panel/confirm_delete.html', {'object': area, 'type': 'Area'})


# ── USER MANAGEMENT ──

@login_required
@admin_required
def user_list(request):
    users = User.objects.select_related('profile').order_by('-date_joined')
    q = request.GET.get('q', '')
    if q:
        users = users.filter(Q(username__icontains=q) | Q(email__icontains=q))
    return render(request, 'admin_panel/user_list.html', {'users': users, 'q': q})


@login_required
@admin_required
def user_toggle_active(request, pk):
    """Ban / unban a user via AJAX POST."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required.'}, status=405)
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        return JsonResponse({'error': 'Cannot ban yourself.'}, status=400)
    user.is_active = not user.is_active
    user.save()
    status = 'activated' if user.is_active else 'banned'
    return JsonResponse({'status': status, 'is_active': user.is_active})


# ── ANALYTICS ──

@login_required
@admin_required
def analytics(request):
    crime_by_type = (
        CrimeRecord.objects.values('crime_type')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    risk_dist = (
        Area.objects.values('risk_level')
        .annotate(count=Count('id'))
    )
    top_areas = Area.objects.order_by('-risk_score')[:10]
    searches_today = SearchHistory.objects.filter(
        searched_at__date=timezone.now().date()
    ).count()

    context = {
        'crime_by_type':  list(crime_by_type),
        'risk_dist':      list(risk_dist),
        'top_areas':      top_areas,
        'searches_today': searches_today,
    }
    return render(request, 'admin_panel/analytics.html', context)


# ── PENDING REPORTS ──

@login_required
@admin_required
def pending_reports(request):
    pending = CrimeRecord.objects.filter(status='pending').select_related('area', 'reported_by')
    return render(request, 'admin_panel/pending.html', {'pending': pending})


@login_required
@admin_required
def approve_report(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required.'}, status=405)
    record = get_object_or_404(CrimeRecord, pk=pk)
    record.status = 'approved'
    record.save()
    return JsonResponse({'status': 'approved'})


@login_required
@admin_required
def reject_report(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required.'}, status=405)
    record = get_object_or_404(CrimeRecord, pk=pk)
    record.status = 'rejected'
    record.save()
    return JsonResponse({'status': 'rejected'})


@login_required
@admin_required
def crime_import_redirect(request):
    """Redirect to the bulk import page."""
    return redirect('/dashboard/import-crimes/')


@login_required
@admin_required
def user_reports_list(request):
    """View all user-submitted crime reports."""
    from crime.models import CrimeReport
    reports = CrimeReport.objects.select_related('area','reported_by').order_by('-created_at')
    return render(request, 'admin_panel/user_reports.html', {'reports': reports})
