import os
import json
import re  # Обязательно для очистки JSON
from django.http import JsonResponse
from django.shortcuts import render
from ollama import Client  # Убедись, что библиотека ollama установлена

def home(request):
    context = {
        'title': 'Главная'
    }
    return render(request, 'home.html', context)

def get_suppliers(request):
    # 1. Получаем параметры из запроса
    experience = request.GET.get('experience', 'ЛЮБОЙ')
    phone_only = request.GET.get('phone_only') == 'true'
    rating = request.GET.get('rating', 'ЛЮБОЙ')
    search = request.GET.get('search', 'Общие товары')
    city = request.GET.get('city', 'Махачкала')

    # Настройка клиента
    # ВАЖНО: Проверь этот адрес. Обычно Ollama работает на http://localhost:11434
    client = Client(
        host="https://ollama.com", 
        headers={'Authorization': 'Bearer f211216e19154bdda1db4d033dd399b6.BbQ_gVPrB44_QomJcr2NRKzw'}
    )

    # Улучшенный промпт (просим 10 штук для стабильности)
    prompt = f"""
    Верни ТОЛЬКО JSON массив из 10 объектов. Без лишнего текста.
    Параметры: специализация {search}, город {city}, опыт {experience}, рейтинг {rating}.
    
    Формат ответа:
    [
      {{
        "name": "Название компании",
        "owner": "Имя владельца",
        "phone": "+79000000000",
        "email": "info@example.com",
        "address": "Улица, дом",
        "city": "{city}",
        "experience": 5,
        "rating": 4.5,
        "reviews": 20,
        "description": "Краткое описание деятельности"
      }}
    ]
    """

    try:
        # Запрос к нейросети (без стриминга для стабильности)
        response = client.chat(
            model='-oss:120b',
            messages=[{'role': 'user', 'content': prompt}],
            stream=False
        )

        full_content = response['message']['content']
        
        # Печатаем в терминал для проверки (полезно для диплома)
        print("--- ОТВЕТ НЕЙРОСЕТИ ---")
        print(full_content)
        print("-----------------------")

        # Очистка: ищем текст внутри квадратных скобок [ ... ]
        match = re.search(r'\[.*\]', full_content, re.DOTALL)
        if match:
            clean_json = match.group(0)
        else:
            clean_json = full_content.strip()

        # Превращаем строку в реальный список данных
        data_list = json.loads(clean_json)

        return JsonResponse({"data": data_list}, safe=False)

    except json.JSONDecodeError as e:
        # Если ИИ все-таки выдал кривой JSON
        print(f"Ошибка парсинга JSON: {e}")
        return JsonResponse({
            "error": "Ошибка формата данных от ИИ",
            "details": str(e)
        }, status=500)
        
    except Exception as e:
        # Любая другая ошибка (интернет, API и т.д.)
        print(f"Системная ошибка: {e}")
        return JsonResponse({"error": str(e)}, status=500)
