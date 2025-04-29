import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import datetime
from django.utils.timezone import make_aware
import logging

logger = logging.getLogger(__name__)

API_URL = 'http://37.9.4.22:8080/api'
SESSION_KEY = 'access_token'
# USER_INFO_KEY = 'user_info'


def validate_registration_data(data):
    if len(data.get('password', '')) < 8:
        raise ValidationError("Пароль должен содержать минимум 8 символов")


def make_api_request(method, endpoint, data=None, files=None, token=None, headers=None):
    request_headers = headers or {}
    if token:
        request_headers['Authorization'] = f'Bearer Bearer {token}'

    try:
        response = requests.request(
            method,
            f'{API_URL}{endpoint}',
            json=data,
            files=files,
            headers=request_headers,
            timeout=10
        )

        # Логируем запрос и ответ для отладки
        logger.info(f"Request to {endpoint}, status: {response.status_code}")
        logger.debug(f"Response content: {response.text[:200]}")

        if response.status_code in [200, 201]:
            # Пытаемся распарсить JSON, если не получается - возвращаем текст
            try:
                return response.json()
            except ValueError:
                return response.text
        else:
            # Обработка ошибок
            try:
                error_data = response.json()
                return {
                    'error': error_data.get('message', str(error_data)),
                    'status_code': response.status_code
                }
            except ValueError:
                return {
                    'error': response.text,
                    'status_code': response.status_code
                }

    except requests.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        return {'error': str(e)}


def start(request):
    return render(request, 'events/start.html')


@require_http_methods(["GET", "POST"])
def login_view(request):
    # Всегда инициализируем контекст с error=None
    context = {'error': None}

    if request.method == 'POST':
        login = request.POST.get('login', '').strip()
        password = request.POST.get('password', '').strip()

        if not login or not password:
            context['error'] = 'Логин и пароль обязательны для заполнения'
            return render(request, 'events/enter.html', context)

        response = make_api_request(
            'POST',
            '/auth/sign-in',
            data={'login': login, 'password': password}
        )

        # Обработка ответа от API
        if isinstance(response, str) and response.startswith('eyJ'):  # JWT токен
            request.session[SESSION_KEY] = response
            return redirect('profile')
        elif isinstance(response, dict):
            if 'access_token' in response:
                request.session[SESSION_KEY] = response['access_token']
                return redirect('profile')
            context['error'] = response.get('error', 'Неверный логин или пароль')
        else:
            context['error'] = 'Ошибка сервера, попробуйте позже'

    return render(request, 'events/enter.html', context)


def logout_view(request):
    request.session.flush()
    return redirect('start')


@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.method == 'POST':
        data = {
            'login': request.POST.get('login', '').strip(),
            'password': request.POST.get('password', '').strip(),
            'name': request.POST.get('name', '').strip(),
            'surname': request.POST.get('surname', '').strip(),
            'groupName': request.POST.get('group', '').strip(),
        }

        if not all(data.values()):
            messages.error(request, 'Все поля обязательны для заполнения')
            return render(request, 'events/register.html')

        result = make_api_request(
            'POST',
            '/auth/sign-up',
            data=data,
            headers={'X-Request-Source': 'web'}
        )

        if 'error' not in result:
            messages.success(request, 'Регистрация успешна! Войдите в систему')
            return redirect('enter')

        messages.error(request, result.get('error', 'Ошибка регистрации'))

    return render(request, 'events/register.html')


def profile_view(request):
    token = request.session.get(SESSION_KEY)
    if not token:
        return redirect('enter')

    # Получаем информацию о пользователе из сессии
    user_info = make_api_request('GET', '/users', token=token)

    # Если API вернуло ошибку (например, токен недействителен)
    if not user_info or isinstance(user_info, dict) and 'error' in user_info:
        del request.session[SESSION_KEY]
        return redirect('enter')

    # Получаем мероприятия
    events_result = make_api_request('GET', '/creator/events', token=token)
    events = events_result if isinstance(events_result, list) else []


    context = {
        'user': user_info,
        'events': events,
        'is_authenticated': True,
        'user_info': user_info
    }

    return render(request, 'events/profile.html', context)


@require_http_methods(["GET", "POST"])
def create_event(request):
    token = request.session.get(SESSION_KEY)
    if not token:
        return redirect('enter')

    if request.method == 'POST':
        try:
            event_date = make_aware(datetime.strptime(
                request.POST['date'],
                '%Y-%m-%d'
            )).isoformat()

            data = {
                "title": request.POST['title'],
                "description": request.POST['description'],
                "eventDate": event_date,
                "location": request.POST['location'],
                "participantLimit": int(request.POST.get('limit', 0)),
                "requestModeration": 'moderation' in request.POST,
            }

            result = make_api_request('POST', '/creator/events', data=data, token=token)

            if 'id' in result:
                if 'image' in request.FILES:
                    files = {'file': request.FILES['image']}
                    make_api_request(
                        'PATCH',
                        f'/creator/events/image/{result["id"]}',
                        files=files,
                        token=token
                    )
                messages.success(request, 'Мероприятие успешно создано!')
                return redirect('profile')

            messages.error(request, result.get('error', 'Ошибка при создании мероприятия'))

        except ValueError as e:
            messages.error(request, f'Неверный формат данных: {str(e)}')
        except Exception as e:
            messages.error(request, f'Ошибка: {str(e)}')

    return render(request, 'events/create_event.html')


@require_http_methods(["GET", "POST"])
def edit_event(request, event_id):
    token = request.session.get(SESSION_KEY)
    if not token:
        return redirect('enter')

    if request.method == 'POST':
        try:
            event_date = make_aware(datetime.strptime(
                request.POST['date'],
                '%Y-%m-%d'
            )).isoformat()

            data = {
                "title": request.POST['title'],
                "annotation": request.POST.get('annotation', ''),
                "description": request.POST['description'],
                "eventDate": event_date,
                "location": request.POST['location'],
                "participantLimit": int(request.POST.get('limit', 0)),
                "requestModeration": 'moderation' in request.POST,
                "stateAction": "SEND_TO_REVIEW"
            }

            result = make_api_request(
                'PATCH',
                f'/creator/events/{event_id}',
                data=data,
                token=token
            )

            if 'error' not in result:
                messages.success(request, 'Мероприятие успешно обновлено!')
                return redirect('profile')

            messages.error(request, result.get('error', 'Ошибка при обновлении мероприятия'))

        except ValueError as e:
            messages.error(request, f'Неверный формат данных: {str(e)}')

    # Получаем данные мероприятия для формы
    result = make_api_request('GET', f'/creator/events/{event_id}', token=token)

    if 'error' in result:
        messages.error(request, result['error'])
        return redirect('profile')

    return render(request, 'events/edit_event.html', {'event': result})


def delete_event(request, event_id):
    token = request.session.get(SESSION_KEY)
    if not token:
        return redirect('enter')

    result = make_api_request('DELETE', f'/creator/events/{event_id}', token=token)

    if 'error' not in result:
        messages.success(request, 'Мероприятие успешно удалено!')
    else:
        messages.error(request, result.get('error', 'Ошибка при удалении мероприятия'))

    return redirect('profile')