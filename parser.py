#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для парсинга книг с сайта books.toscrape.com
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import argparse
import time
import sys


def parse_price(price_text):
    """Извлекает числовое значение цены из строки."""
    return float(price_text.replace('£', '').replace('Â', '').strip())


def parse_rating(rating_class):
    """Преобразует текстовый рейтинг в число."""
    rating_map = {
        'One': 1,
        'Two': 2,
        'Three': 3,
        'Four': 4,
        'Five': 5
    }
    for key in rating_map:
        if key in rating_class:
            return rating_map[key]
    return 0


def fetch_page(url, retry=3, timeout=10):
    """
    Отправляет GET-запрос с повторными попытками при ошибке.

    Args:
        url: URL страницы для парсинга
        retry: количество повторных попыток
        timeout: таймаут запроса в секундах

    Returns:
        BeautifulSoup объект или None при ошибке
    """
    for attempt in range(retry):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе {url} (попытка {attempt + 1}/{retry}): {e}")
            if attempt < retry - 1:
                time.sleep(2)
            else:
                print(f"Не удалось загрузить страницу после {retry} попыток.")
                return None


def parse_books(base_url, num_pages):
    """
    Парсит книги с нескольких страниц сайта.

    Args:
        base_url: базовый URL сайта
        num_pages: количество страниц для парсинга

    Returns:
        pandas DataFrame с данными о книгах
    """
    all_books = []

    for page_num in range(1, num_pages + 1):
        if page_num == 1:
            url = f"{base_url}/catalogue/page-{page_num}.html"
        else:
            url = f"{base_url}/catalogue/page-{page_num}.html"

        print(f"Парсинг страницы {page_num}: {url}")
        soup = fetch_page(url)

        if soup is None:
            continue

        # Находим все книги на странице
        books = soup.find_all('article', class_='product_pod')

        for book in books:
            try:
                # Название книги
                title = book.h3.a['title']

                # Цена
                price_text = book.find('p', class_='price_color').text
                price = parse_price(price_text)

                # Ссылка
                link = base_url + '/catalogue/' + book.h3.a['href'].replace('../', '')

                # Рейтинг
                rating_class = book.find('p', class_='star-rating')['class']
                rating = parse_rating(rating_class)

                all_books.append({
                    'title': title,
                    'price': price,
                    'rating': rating,
                    'link': link
                })

            except Exception as e:
                print(f"Ошибка при парсинге книги: {e}")
                continue

        print(f"Найдено книг на странице {page_num}: {len(books)}")
        time.sleep(1)  # Пауза между запросами

    return pd.DataFrame(all_books)


def main():
    """Главная функция для запуска парсера."""
    parser = argparse.ArgumentParser(description='Парсер книг с books.toscrape.com')
    parser.add_argument('--pages', type=int, default=3, 
                        help='Количество страниц для парсинга (по умолчанию: 3)')
    parser.add_argument('--output', type=str, default='data/raw_data.csv',
                        help='Путь для сохранения результатов (по умолчанию: data/raw_data.csv)')

    args = parser.parse_args()

    base_url = 'https://books.toscrape.com'

    print(f"Начинаем парсинг {args.pages} страниц с {base_url}")
    print("-" * 60)

    df = parse_books(base_url, args.pages)

    if df.empty:
        print("Данные не были получены. Проверьте подключение к интернету.")
        sys.exit(1)

    # Сохраняем в CSV
    df.to_csv(args.output, index=False, encoding='utf-8')

    print("-" * 60)
    print(f"Парсинг завершён! Всего найдено книг: {len(df)}")
    print(f"Данные сохранены в: {args.output}")
    print(f"\nПервые 5 записей:")
    print(df.head())


if __name__ == '__main__':
    main()
