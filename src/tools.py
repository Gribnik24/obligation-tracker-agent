from datetime import datetime
from zoneinfo import ZoneInfo
import json
import requests
from typing import Optional
from langchain_core.tools import tool


@tool
def get_current_time(timezone: str = 'UTC') -> str:
    """
    Возвращает текущие дату и время для указанного часового пояса в формате IANA.
    Args:
        timezone: Имя часового пояса в формате IANA (например 'Europe/Moscow', 'Asia/Novosibirsk', 'UTC'). По умолчанию 'UTC'.
    Returns:
        Строка в формате JSON с полями:
            `date`: дата в формате (YYYY-MM-DD) в указанном часовом поясе
            `time`: время в формате (HH:MM:SS) в указанном часовом поясе
    """
    try:
        tz = ZoneInfo(timezone)
        now = datetime.now(tz)
        result = {'date': now.strftime('%Y-%m-%d'), 'time': now.strftime('%H:%M:%S')}
        return json.dumps(result, ensure_ascii=False)
    except Exception:
        return json.dumps({'error': 'Ошибка Получения текущего времени'}, ensure_ascii=False)


@tool
def get_obligations(status=Optional[str], category=Optional[str]) -> str:
    """
    Возвращает список финансовых обязательств пользователя.
    Args:
        `status`: статус платежа (может принимать значения: 
                                            `active` - платеж запланирован и активен;
                                            `inactive` - платеж неактивен;
                                            `paused` - использование данной подписки приостановлено на текущий момент
                                            )
        `category`: категория сервиса, товара или услуги (может принимать значения:
                                                            `subscription` - подписка на сервис;
                                                            `sport` - спорт;
                                                            `health` - здоровье;
                                                            `software` - программное обеспечение;
                                                            `utility` - служебная программаж
                                                            `vehicle` - автомобиль)
    Returns:
        Список со строкми в формате JSON с полями:
            `id`: id операции
            `title`: название сервиса, товара или услуги
            `amount`: цена сервиса, товара или услуги
            `currency`: валюта, в которой измеряется цена
            `category`: категория сервиса, товара или услуги
            `status`: статус платежа
    """
    try:
        data = json.load('../data/subscriptions.json')
        result = []
    except Exception as e:
        return json.dumps({'error': 'Ошибка чтений файла с данными'}, ensure_ascii=False)
    
    try:
        if status is not None and category is not None:
            for record in data:
                if record['status'] == status and record['category'] == category:
                    result.append(record)
        elif status is None and category is not None:
            for record in data:
                if record['category'] == category:
                    result.append(record)     
        elif status is not None and category is None:
            for record in data:
                if record['status'] == status:
                    result.append(record)
    except Exception as e:
        return json.dumps({'error': 'Ошибка фильтрования данных'}, ensure_ascii=False)
                
    return result

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
    
    return json.dumps({'need_currency_amount': to_currency_value * amount}, ensure_ascii=False)


tools_list = [get_current_time, get_obligations, convert_currency]