import re # Добавь этот импорт в начало файла!

def get_suppliers(request):
    # 1. Получаем параметры
    experience = request.GET.get('experience', 'ЛЮБОЙ')
    phone_only = request.GET.get('phone_only') == 'true'
    rating = request.GET.get('rating', 'ЛЮБОЙ')
    search = request.GET.get('search')
    city = request.GET.get('city', 'Махачкала')

    client = Client(
        host="https://ollama.com", # Проверь этот хост, обычно Ollama работает локально
        headers={'Authorization': 'Bearer ' + 'f211216e19154bdda1db4d033dd399b6.BbQ_gVPrB44_QomJcr2NRKzw'}
    )

    # Снизил количество до 10 для стабильности (20 часто обрываются)
    prompt = f"""
    Верни ТОЛЬКО JSON массив из 10 объектов. Без текста до и после.
    Данные о поставщиках: {search}, город {city}, опыт {experience}, рейтинг {rating}.
    Формат:
    [
      {{
        "name": "Название",
        "owner": "Имя",
        "phone": "Телефон",
        "email": "Email",
        "address": "Адрес",
        "city": "{city}",
        "experience": 5,
        "rating": 4.5,
        "reviews": 10,
        "description": "Описание"
      }}
    ]
    """

    try:
        # Убираем стрим (stream=False), так надежнее для получения чистого JSON
        response = client.chat(
            model='-oss:120b', 
            messages=[{'role': 'user', 'content': prompt}],
            stream=False 
        )
        
        full_content = response['message']['content']
        print("ОТВЕТ НЕЙРОСЕТИ:", full_content) # Для отладки в терминале

        # Умная очистка: ищем всё, что находится внутри [ и ]
        match = re.search(r'\[.*\]', full_content, re.DOTALL)
        if match:
            clean_json = match.group(0)
        else:
            clean_json = full_content

        data_list = json.loads(clean_json)
        return JsonResponse({"data": data_list}, safe=False)

    except json.JSONDecodeError as e:
        print(f"Ошибка парсинга: {e}")
        return JsonResponse({
            "error": "Нейросеть выдала неверный формат. Попробуйте еще раз.",
            "raw": full_content[:100] # Показываем начало ошибки
        }, status=500)
    except Exception as e:
        print(f"Общая ошибка: {e}")
        return JsonResponse({"error": str(e)}, status=500)
