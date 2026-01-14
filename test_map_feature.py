"""
Тестовый скрипт для проверки функциональности карты
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'photohub.settings')
django.setup()

from studios.models import Studio
from studios.geocoding import geocode_address

def test_geocoding():
    """Тест геокодирования адреса"""
    print("=== Тест геокодирования ===")
    
    test_address = "Москва, Тверская улица, 1"
    print(f"Тестовый адрес: {test_address}")
    
    coords = geocode_address(test_address)
    
    if coords:
        print(f"✓ Координаты успешно получены: {coords[0]}, {coords[1]}")
        return True
    else:
        print("✗ Не удалось получить координаты")
        return False

def test_model_fields():
    """Тест наличия полей latitude и longitude в модели"""
    print("\n=== Тест модели Studio ===")
    
    try:
        # Проверяем наличие полей
        fields = [f.name for f in Studio._meta.get_fields()]
        
        if 'latitude' in fields and 'longitude' in fields:
            print("✓ Поля latitude и longitude присутствуют в модели")
            return True
        else:
            print("✗ Поля latitude и/или longitude отсутствуют в модели")
            return False
    except Exception as e:
        print(f"✗ Ошибка при проверке модели: {e}")
        return False

def main():
    print("Запуск тестов для функциональности карты...\n")
    
    results = []
    
    # Тест 1: Геокодирование
    results.append(test_geocoding())
    
    # Тест 2: Модель
    results.append(test_model_fields())
    
    # Итоги
    print("\n=== Итоги тестирования ===")
    passed = sum(results)
    total = len(results)
    print(f"Пройдено тестов: {passed}/{total}")
    
    if passed == total:
        print("✓ Все тесты пройдены успешно!")
    else:
        print("✗ Некоторые тесты не пройдены")

if __name__ == '__main__':
    main()
