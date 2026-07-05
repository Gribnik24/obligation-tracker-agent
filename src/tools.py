from datetime import datetime
from zoneinfo import ZoneInfo
import json
import os
import requests
import numexpr
from typing import Optional
from langchain_core.tools import tool

@tool
def calculator(expression: str) -> str:
    """
    Кулькулятор. Инструмент для вычисления математических выражений
    Args:
        expression: математическое выражение (например '2+2')
    Returns:
        Строка в формате JSON с полями:
            `answer`: ответ на математичесоке выражение
    """
    try:
        return json.dumps({'answer': str(numexpr.evaluate(expression))})
    except Exception as e:
        return json.dumps({'error': 'Ошибка вычислений'}, ensure_ascii=False)


@tool
def get_current_time(timezone: str = 'UTC') -> str:
    """
    Возвращает текущие дату и время для указанного часового пояса в формате IANA.
    Args:
        timezone: Имя часового пояса в формате IANA (например 'Europe/Moscow', 'Asia/Novosibirsk', 'UTC'). По умолчанию 'UTC'.
    Returns:
        Строка в формате JSON с полями:
            `date`: текущую дату в формате (YYYY-MM-DD) в указанном часовом поясе
            `time`: текущее время в формате (HH:MM:SS) в указанном часовом поясе
            `day_of_week`: текущий день недели в указанном часовом поясе
    """
    try:
        tz = ZoneInfo(timezone)
        now = datetime.now(tz)
        result = {'date': now.strftime('%Y-%m-%d'),
                  'time': now.strftime('%H:%M:%S'),
                  'day_of_week': now.strftime('%A')
                  }
        return json.dumps(result, ensure_ascii=False)
    except Exception:
        return json.dumps({'error': 'Ошибка получения текущего времени'}, ensure_ascii=False)


@tool
def get_obligations(currency: Optional[str] = None,
                    category: Optional[str] = None,
                    lower_date: Optional[str] = None, upper_date:Optional[str] = None,
                    status: Optional[str] = None) -> str:
    """
    Возвращает список финансовых обязательств пользователя.
    Args:
        `currency`: название валюты, в которой принимается оплата (например 'USD' или 'RUB')
        `category`: категория сервиса, товара или услуги (может принимать значения:
                                                            `subscription` - подписка на сервис;
                                                            `sport` - спорт;
                                                            `health` - здоровье;
                                                            `software` - программное обеспечение;
                                                            `utility` - служебная программаж
                                                            `vehicle` - автомобиль)
        `lower_date`: нижняя граница даты, по которой нужно вести поиск в формате YYYY-MM-DD
        `upper_date`: верхняя граница даты, по которой нужно вести поиск в формате YYYY-MM-DD
        `status`: статус платежа (может принимать значения: 
                                    `active` - платеж запланирован и активен;
                                    `inactive` - платеж неактивен;
                                    `paused` - использование данной подписки приостановлено на текущий момент
                                    )
    Returns:
        Список со строками в формате JSON с полями:
            `id`: id операции
            `title`: название сервиса, товара или услуги
            `amount`: цена сервиса, товара или услуги
            `currency`: валюта, в которой измеряется цена
            `category`: категория сервиса, товара или услуги
            `status`: статус платежа
    """
    try:
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'subscriptions.json')
        with open(data_dir, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return json.dumps({'error': f'Ошибка чтений файла с данными {e}'}, ensure_ascii=False)
    
    # Создаем копию данных для фильтрации
    result = data.copy()
    
    # Фильтр по статусу (обычно мало уникальных значений)
    if status is not None:
        result = [item for item in result if item.get('status') == status]
        if not result:
            return json.dumps([], ensure_ascii=False)
    
    # Фильтр по категории
    if category is not None:
        result = [item for item in result if item.get('category') == category]
        if not result:
            return json.dumps([], ensure_ascii=False)
    
    # Фильтр по валюте
    if currency is not None:
        result = [item for item in result if item.get('currency') == currency]
        if not result:
            return json.dumps([], ensure_ascii=False)
    
    # Фильтр по дате (диапазон)
    if lower_date is not None or upper_date is not None:
        filtered_by_date = []
        for item in result:
            payment_date = item.get('next_payment_date', '')
            if not payment_date:
                continue
            
            # Проверяем нижнюю границу
            if lower_date is not None and payment_date < lower_date:
                continue
            
            # Проверяем верхнюю границу
            if upper_date is not None and payment_date > upper_date:
                continue
            
            filtered_by_date.append(item)
        
        result = filtered_by_date
        if not result:
            return json.dumps([], ensure_ascii=False)
    
    return json.dumps(result, ensure_ascii=False)

@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """
    Преобразует указанную сумму из одной денежной валюты в другую
    Args:
        `amount` - сумма денег в валюте, из которой нужно перевести
        `from_currency` - название валюты, из которой нужно перевести (например 'USD' или 'RUB')
        `to_currency` - название валюты, в которую нужно перевести (например 'USD' или 'RUB')
    Returns:
        Список со строкми в формате JSON с полями:
            `need_currency_amount`: сумма денег в валюте, в которую нужно перевести
        
    """
    try:
        url = 'https://api.frankfurter.app/latest/'
        params = {
            'from': from_currency,
            'to': to_currency.upper()
        }
        response = requests.get(url, params)
        data = response.json()
    except Exception as e:
        return json.dumps({'error': 'Ошибка получения данных'}, ensure_ascii=False)
    
    to_currency_value = data.get('rates', {}).get(to_currency.upper(), None)
    if to_currency_value is None:
        return json.dumps({'error': 'Ошибка получения данных'}, ensure_ascii=False)
    
    return json.dumps({'need_currency_amount': str(to_currency_value * amount)}, ensure_ascii=False)


tools_list = [calculator, get_current_time, get_obligations, convert_currency]