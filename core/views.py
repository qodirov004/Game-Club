from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Avg, F, ExpressionWrapper, fields
from django.db.models.functions import ExtractHour
from django.http import JsonResponse
from datetime import timedelta, date
import json
from .models import Game, GameSession, Statistic

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('game_list')
        else:
            messages.error(request, 'Noto\'g\'ri foydalanuvchi nomi yoki parol.')
    
    return render(request, 'games/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def game_list(request):
    if not request.user.is_authenticated :        
        return redirect('login')
    else:
        games = Game.objects.all()

        for game in games:
            game.active_session = game.sessions.filter(status='active').first()  # Faol sessiya bo‘lsa, uni saqlaymiz.

        return render(request, 'games/game_list.html', {'games': games})

def add_game(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        table_count = request.POST.get('table_count')
        standard_price = request.POST.get('standard_price')
        image = request.FILES.get('image')

        errors = {}
        if not name:
            errors['name'] = "O'yin nomini kiriting"
        if not table_count or not table_count.isdigit() or int(table_count) <= 0:
            errors['table_count'] = "Stollar sonini to'g'ri kiriting (musbat son)"
        if not standard_price:
            errors['standard_price'] = "Standart narxni kiriting"

        if errors:
            for field, error in errors.items():
                messages.error(request, error)
            return render(request, 'games/add_game.html', {
                'name': name,
                'table_count': table_count,
                'standard_price': standard_price,
                'errors': errors
            })

        table_count = int(table_count)

        for i in range(1, table_count + 1):
            game = Game(
                name=f"{name} - {i}-stol",
                table_count=1,  # Har bir stol uchun bitta obyekt
                standard_price=standard_price,
                image=image
            )
            game.save()

        messages.success(request, f"{table_count} ta '{name}' o'yin stoli yaratildi!")
        return redirect('game_list')

    return render(request, 'games/add_game.html')

def edit_game(request, pk):
    game = get_object_or_404(Game, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        table_count = request.POST.get('table_count')
        standard_price = request.POST.get('standard_price')
        image = request.FILES.get('image')

        errors = {}
        if not name:
            errors['name'] = "O'yin nomini kiriting"
        if not table_count:
            errors['table_count'] = "Stollar sonini kiriting"
        if not standard_price:
            errors['standard_price'] = "Standart narxni kiriting"

        if errors:
            for field, error in errors.items():
                messages.error(request, error)
            return render(request, 'games/edit_game.html', {
                'game': game,
                'errors': errors
            })

        game.name = name
        game.table_count = table_count
        game.standard_price = standard_price
        if image:
            game.image = image
        game.save()

        messages.success(request, "O'yin muvaffaqiyatli yangilandi!")
        return redirect('game_list')

    return render(request, 'games/edit_game.html', {'game': game})

def delete_game(request, pk):
    game = get_object_or_404(Game, pk=pk)
    
    if request.method == 'POST':
        game.delete()
        messages.success(request, "O'yin muvaffaqiyatli o'chirildi!")
        return redirect('game_list')
    
    return render(request, 'games/delete_game.html', {'game': game})    

def start_game(request, pk):
    game = get_object_or_404(Game, pk=pk)

    completed_sessions = GameSession.objects.filter(
        game=game,  # Faqat shu o‘yinga tegishli sessiyalar
        status='completed',
        created_by=request.user
    ).order_by('-end_time')

    total_cost = sum(session.get_cost() for session in completed_sessions)
    paid_amount = sum(session.get_cost() for session in completed_sessions if session.is_paid)
    unpaid_amount = total_cost - paid_amount

    if request.method == 'POST':
        if 'mark_as_paid' in request.POST:
            session_id = request.POST.get('session_id')
            session = get_object_or_404(GameSession, id=session_id, created_by=request.user)
            session.is_paid = True
            session.save()
            messages.success(request, "Sessiya to‘langan deb belgilandi!")
            return redirect('start_game', pk=game.pk)

        # Tariff endi yo‘q, shunchaki sessiyani yaratamiz
        session = GameSession(
            game=game,
            created_by=request.user
        )
        session.save()

        messages.success(request, f"{game.name} o‘yini boshlandi!")
        return redirect('active_session', pk=session.pk)

    context = {
        'game': game,
        'completed_sessions': completed_sessions,
        'total_cost': total_cost,
        'paid_amount': paid_amount,
        'unpaid_amount': unpaid_amount,
    }

    return render(request, 'games/start_game.html', context)

@login_required
def active_session(request, pk):
    session = get_object_or_404(GameSession, pk=pk, created_by=request.user)
    
    if session.status == 'completed':
        return redirect('start_game', pk=session.game.pk)
    
    return render(request, 'games/active_session.html', {'session': session})

@login_required
def pause_session(request, pk):
    session = get_object_or_404(GameSession, pk=pk, created_by=request.user)
    
    if session.status == 'active':
        session.pause()
        messages.info(request, f"{session.game.name} o'yini to'xtatildi.")
    
    return redirect('active_session', pk=session.pk)

@login_required
def resume_session(request, pk):
    session = get_object_or_404(GameSession, pk=pk, created_by=request.user)
    
    if session.status == 'paused':
        session.resume()
        messages.info(request, f"{session.game.name} o'yini davom ettirildi.")
    
    return redirect('active_session', pk=session.pk)

@login_required
def stop_session(request, pk):
    session = get_object_or_404(GameSession, pk=pk, created_by=request.user)
    
    if session.status in ['active', 'paused']:
        session.complete()
        messages.success(request, f"{session.game.name} o'yini yakunlandi. Umumiy narx: {session.get_cost():.2f} So'm")
    
    return redirect('start_game', pk = session.game.pk)

def stop_game(request, game_pk):
    game = get_object_or_404(Game, pk=game_pk)
    game.sessions.filter(status='active').update(status='stopped')  # Faol sessiyalarni to‘xtatish
    return redirect('start_game', game_pk)


@login_required
def completed_games(request):
    completed_sessions = GameSession.objects.filter(
        status='completed',
        created_by=request.user
    ).select_related('game').order_by('-end_time')
    
    # Calculate totals
    total_cost = sum(session.get_cost() for session in completed_sessions)
    paid_amount = sum(session.get_cost() for session in completed_sessions if session.is_paid)
    unpaid_amount = total_cost - paid_amount
    
    context = {
        'completed_sessions': completed_sessions,
        'total_cost': total_cost,
        'paid_amount': paid_amount,
        'unpaid_amount': unpaid_amount,
    }
    
    return render(request, 'games/completed_games.html', context)

@login_required
def mark_as_paid(request, pk):
    session = get_object_or_404(GameSession, pk=pk, created_by=request.user)
    
    if not session.is_paid:
        session.is_paid = True
        session.save()
        messages.success(request, f"{session.game.name} uchun to'lov qabul qilindi.")
    
    return redirect('start_game', pk=session.game.pk)

def statistics(request):
    # Davr parametrini olish (default: daily)
    period = request.GET.get('period', 'daily')
    
    # Davr uchun sana chegaralarini aniqlash
    today = timezone.now().date()
    
    if period == 'daily':
        start_date = today
        end_date = today
        period_display = "Kunlik"
    elif period == 'weekly':
        # Haftaning boshlanishi (dushanba)
        start_date = today - timedelta(days=today.weekday())
        end_date = today
        period_display = "Haftalik"
    elif period == 'monthly':
        # Oyning boshlanishi
        start_date = today.replace(day=1)
        end_date = today
        period_display = "Oylik"
    else:
        # Noto'g'ri parametr uchun default qiymat
        period = 'daily'
        start_date = today
        end_date = today
        period_display = "Kunlik"
    
    # Tanlangan davr uchun o'yin seanslari (faqat tugallangan seanslar)
    sessions = GameSession.objects.filter(
        start_time__date__gte=start_date,
        start_time__date__lte=end_date,
        status='completed'  # Faqat tugallangan seanslar
    )
    
    # Asosiy statistika
    games_count = sessions.count()
    
    # Umumiy o'ynalgan soatlar
    # get_duration() metodidan foydalanib, soatlarni hisoblaymiz
    total_hours = 0
    for session in sessions:
        # get_duration() sekund qaytaradi, soatga o'tkazamiz
        total_hours += session.get_duration() / 3600
    
    # Umumiy daromad
    # get_cost() metodidan foydalanib, daromadni hisoblaymiz
    revenue = 0
    for session in sessions:
        revenue += session.get_cost()
    
    # O'rtacha seanslar (kuniga)
    days_count = (end_date - start_date).days + 1
    average_session = round(games_count / days_count, 1) if days_count > 0 else 0
    
    # O'yin bo'yicha taqsimot
    game_stats = {}
    for session in sessions:
        game_name = session.game.name
        if game_name not in game_stats:
            game_stats[game_name] = {
                'count': 0,
                'revenue': 0
            }
        game_stats[game_name]['count'] += 1
        game_stats[game_name]['revenue'] += session.get_cost()
    
    # O'yin bo'yicha foizlar
    game_distribution = []
    if games_count > 0:
        # Game stats ni count bo'yicha tartiblash
        sorted_games = sorted(game_stats.items(), key=lambda x: x[1]['count'], reverse=True)
        
        for game_name, stats in sorted_games[:5]:  # Top 5 o'yinlar
            percentage = round((stats['count'] / games_count) * 100, 1)
            game_distribution.append({
                'name': game_name,
                'count': stats['count'],
                'percentage': percentage,
                'revenue': stats['revenue']
            })
    
    # Soatlik taqsimot
    hourly_stats = {}
    for session in sessions:
        hour = session.start_time.hour
        if hour not in hourly_stats:
            hourly_stats[hour] = 0
        hourly_stats[hour] += 1
    
    # Soatlik ma'lumotlarni Chart.js uchun formatlash
    hours = list(range(8, 24)) + list(range(0, 4))  # 8:00 dan 03:00 gacha
    hourly_data = [0] * len(hours)
    
    for hour, count in hourly_stats.items():
        if 8 <= hour < 24:
            hourly_data[hour - 8] = count
        elif 0 <= hour < 4:
            hourly_data[hour + 16] = count
    
    # Daromad taqsimoti uchun ma'lumotlar
    revenue_labels = [game['name'] for game in game_distribution]
    revenue_data = [game['revenue'] for game in game_distribution]
    
    # Agar ma'lumotlar bo'lmasa, default qiymatlar
    if not revenue_labels:
        revenue_labels = ['Ma\'lumot yo\'q']
        revenue_data = [0]
    
    # Statistika ma'lumotlarini yig'ish
    stats = {
        'games_count': games_count,
        'total_hours': round(total_hours, 1),  # O'nlik kasrga yaxlitlash
        'revenue': "{:,}".format(int(revenue)).replace(',', ' '),  # Raqamlarni formatlash
        'average_session': average_session
    }
    
    # Chart.js uchun ranglar
    chart_colors = [
        'rgba(99, 102, 241, 0.7)',
        'rgba(59, 130, 246, 0.7)',
        'rgba(16, 185, 129, 0.7)',
        'rgba(245, 158, 11, 0.7)',
        'rgba(239, 68, 68, 0.7)',
        'rgba(107, 114, 128, 0.7)'
    ]
    
    chart_border_colors = [
        'rgba(99, 102, 241, 1)',
        'rgba(59, 130, 246, 1)',
        'rgba(16, 185, 129, 1)',
        'rgba(245, 158, 11, 1)',
        'rgba(239, 68, 68, 1)',
        'rgba(107, 114, 128, 1)'
    ]
    
    # Soatlik ma'lumotlar uchun labellar
    hourly_labels = [f"{h}:00" for h in hours]
    
    context = {
        'period': period,
        'period_display': period_display,
        'stats': stats,
        'game_distribution': game_distribution,
        'revenue_labels': json.dumps(revenue_labels),
        'revenue_data': json.dumps(revenue_data),
        'chart_colors': json.dumps(chart_colors),
        'chart_border_colors': json.dumps(chart_border_colors),
        'hourly_labels': json.dumps(hourly_labels),
        'hourly_data': json.dumps(hourly_data)
    }
    
    return render(request, 'games/statistics.html', context)

# API endpoint for AJAX requests
def get_session_data(request, pk):
    session = get_object_or_404(GameSession, pk=pk, created_by=request.user)
    
    data = {
        'duration': session.get_duration(),
        'duration_display': session.get_duration_display(),
        'cost': session.get_cost(),
        'status': session.status,
    }
    
    return JsonResponse(data)