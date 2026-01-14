"""
Модуль для работы с геокодированием адресов через Яндекс.Карты API
"""
import requests
from typing import Tuple, Optional

# API ключ Яндекс Карт. В реальном проекте должен храниться в настройках Django.
# Используем тестовый ключ для примера.
YANDEX_API_KEY = "6b266f03-65da-43a8-9ff9-d0232b97e81b"


def reverse_geocode_yandex(latitude: float, longitude: float) -> Tuple[str, str]:
    """
    Получает город и район по координатам через Яндекс.Карты API.

    Args:
        latitude: Широта.
        longitude: Долгота.

    Returns:
        Кортеж (city, district).
    """
    url = "https://geocode-maps.yandex.ru/1.x/"

    params = {
        'apikey': YANDEX_API_KEY,
        'format': 'json',
        'geocode': f"{longitude},{latitude}",
        'kind': 'locality',  # Ищем населенный пункт
        'results': 1
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        city = ""
        district = ""

        # Парсинг ответа Яндекса
        geo_object = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']
        meta_data = geo_object['metaDataProperty']['GeocoderMetaData']
        address_details = meta_data['Address']['Components']

        for component in address_details:
            if component['kind'] == 'locality':
                city = component['name']
            elif component['kind'] == 'district':
                district = component['name']

        return city, district

    except (requests.RequestException, ValueError, KeyError, IndexError) as e:
        print(f"Ошибка обратного геокодирования Яндекса: {e}")
        return "", ""

# Удаляем старую функцию geocode_address, так как она больше не нужна
# def geocode_address(address: str) -> Optional[Tuple[float, float]]:
#     ...
