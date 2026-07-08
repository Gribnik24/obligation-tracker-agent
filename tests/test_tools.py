import json
import pytest
from unittest.mock import patch, MagicMock

from src.tools import get_current_time, get_obligations, convert_currency


#  Тесты для get_current_time
class TestGetCurrentTime:

    def test_returns_valid_json_with_required_fields(self):
        """Должен возвращать JSON с полями date, time, day_of_week"""
        result = get_current_time.invoke({"timezone": "Europe/Moscow"})
        data = json.loads(result)

        assert "date" in data
        assert "time" in data
        assert "day_of_week" in data
        # Дата в формате YYYY-MM-DD
        assert len(data["date"]) == 10
        # Время в формате HH:MM:SS
        assert len(data["time"]) == 8

    def test_invalid_timezone_returns_error(self):
        """Несуществующий часовой пояс должен вернуть ошибку"""
        result = get_current_time.invoke({"timezone": "Invalid/Nowhere"})
        data = json.loads(result)

        assert "error" in data

    def test_utc_timezone(self):
        """UTC должен работать и возвращать корректную дату"""
        result = get_current_time.invoke({"timezone": "UTC"})
        data = json.loads(result)

        assert "date" in data
        assert "time" in data


#  Тесты для get_obligations
class TestGetObligations:

    def test_filter_by_status_active(self):
        """Фильтр по status=active должен вернуть только активные платежи"""
        result = get_obligations.invoke({"status": "active"})
        data = json.loads(result)

        assert len(data) > 0
        assert all(item["status"] == "active" for item in data)

    def test_filter_by_category_subscription(self):
        """Фильтр по category=subscription должен вернуть только подписки"""
        result = get_obligations.invoke({"category": "subscription"})
        data = json.loads(result)

        assert len(data) > 0
        assert all(item["category"] == "subscription" for item in data)

    def test_filter_by_date_range(self):
        """Фильтр по диапазону дат должен вернуть платежи в этом диапазоне"""
        result = get_obligations.invoke({
            "lower_date": "2026-07-01",
            "upper_date": "2026-07-31"
        })
        data = json.loads(result)

        assert len(data) > 0
        for item in data:
            assert "2026-07-01" <= item["next_payment_date"] <= "2026-07-31"

    def test_filter_by_currency(self):
        """Фильтр по валюте должен вернуть платежи только в этой валюте"""
        result = get_obligations.invoke({"currency": "RUB"})
        data = json.loads(result)

        assert len(data) > 0
        assert all(item["currency"] == "RUB" for item in data)

    def test_no_results_returns_empty_list(self):
        """Несуществующая категория должна вернуть пустой список"""
        result = get_obligations.invoke({"category": "nonexistent"})
        data = json.loads(result)

        assert data == []

    def test_combined_filters(self):
        """Комбинированный фильтр: status + category + date"""
        result = get_obligations.invoke({
            "status": "active",
            "category": "subscription",
            "lower_date": "2026-07-01",
            "upper_date": "2026-07-31"
        })
        data = json.loads(result)

        assert len(data) > 0
        for item in data:
            assert item["status"] == "active"
            assert item["category"] == "subscription"
            assert "2026-07-01" <= item["next_payment_date"] <= "2026-07-31"



#  Тесмты для convert_currency
class TestConvertCurrency:

    @patch('src.tools.requests.get')
    def test_convert_usd_to_rub_returns_number(self, mock_get):
        """Конвертация USD → RUB должна вернуть число."""
        mock_response = MagicMock()
        mock_response.json.return_value = [{"rate": 76.5}]
        mock_get.return_value = mock_response

        result = convert_currency.invoke({
            "amount": 10.0,
            "from_currency": "USD",
            "to_currency": "RUB"
        })
        data = json.loads(result)

        assert "need_currency_amount" in data
        assert isinstance(float(data["need_currency_amount"]), float)

    @patch('src.tools.requests.get')
    def test_convert_usd_to_rub(self, mock_get):
        """Конвертация USD в RUB должна вернуть корректную сумму"""
        mock_response = MagicMock()
        mock_response.json.return_value = [{"rate": 76.5}]
        mock_get.return_value = mock_response

        result = convert_currency.invoke({
            "amount": 10.0,
            "from_currency": "USD",
            "to_currency": "RUB"
        })
        data = json.loads(result)

        assert "need_currency_amount" in data
        assert float(data["need_currency_amount"]) == pytest.approx(765.0)

    @patch('src.tools.requests.get')
    def test_convert_handles_api_error(self, mock_get):
        """При ошибке сети должен вернуть JSON с полем error."""
        mock_get.side_effect = Exception("Connection error")

        result = convert_currency.invoke({
            "amount": 10.0,
            "from_currency": "USD",
            "to_currency": "RUB"
        })
        data = json.loads(result)

        assert "error" in data

    @patch('src.tools.requests.get')
    def test_convert_missing_rate_field(self, mock_get):
        """Если в ответе API нет поля rate, должен вернуться error."""
        mock_response = MagicMock()
        mock_response.json.return_value = [{"unexpected": "data"}]
        mock_get.return_value = mock_response

        result = convert_currency.invoke({
            "amount": 10.0,
            "from_currency": "USD",
            "to_currency": "RUB"
        })
        data = json.loads(result)

        assert "error" in data