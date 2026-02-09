#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для анализа спарсенных данных о книгах
"""

import pandas as pd
import argparse
import sys
import os
from tabulate import tabulate


def load_data(filepath):
    """
    Загружает данные из CSV файла.

    Args:
        filepath: путь к CSV файлу

    Returns:
        pandas DataFrame
    """
    if not os.path.exists(filepath):
        print(f"Ошибка: файл {filepath} не найден!")
        print("Сначала запустите parser.py для сбора данных.")
        sys.exit(1)

    try:
        df = pd.read_csv(filepath, encoding='utf-8')
        return df
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        sys.exit(1)


def filter_by_price(df, max_price):
    """Фильтрует книги по максимальной цене."""
    if max_price:
        df = df[df['price'] <= max_price]
        print(f"Фильтр: цена <= £{max_price}")
    return df


def filter_by_keyword(df, keyword):
    """Фильтрует книги по ключевому слову в названии."""
    if keyword:
        df = df[df['title'].str.contains(keyword, case=False, na=False)]
        print(f"Фильтр: ключевое слово '{keyword}' в названии")
    return df


def filter_by_rating(df, min_rating):
    """Фильтрует книги по минимальному рейтингу."""
    if min_rating:
        df = df[df['rating'] >= min_rating]
        print(f"Фильтр: рейтинг >= {min_rating}")
    return df


def sort_data(df, sort_by, ascending):
    """
    Сортирует данные по указанному полю.

    Args:
        df: DataFrame для сортировки
        sort_by: поле для сортировки ('price' или 'rating')
        ascending: порядок сортировки (True - по возрастанию)
    """
    if sort_by in df.columns:
        df = df.sort_values(by=sort_by, ascending=ascending)
        order = "возрастанию" if ascending else "убыванию"
        print(f"Сортировка: по {sort_by} по {order}")
    return df


def display_results(df, top_n=10):
    """
    Выводит результаты в виде красивой таблицы.

    Args:
        df: DataFrame для отображения
        top_n: количество записей для вывода
    """
    if df.empty:
        print("\nНет записей, соответствующих критериям фильтрации.")
        return

    # Ограничиваем количество записей
    display_df = df.head(top_n).copy()

    # Форматируем цену
    display_df['price'] = display_df['price'].apply(lambda x: f"£{x:.2f}")

    # Сокращаем длинные названия для красивого вывода
    display_df['title'] = display_df['title'].apply(
        lambda x: x[:50] + '...' if len(x) > 50 else x
    )

    # Сокращаем ссылки
    display_df['link'] = display_df['link'].apply(
        lambda x: x[:40] + '...' if len(x) > 40 else x
    )

    print(f"\n{'=' * 80}")
    print(f"Найдено записей: {len(df)} | Показано: {len(display_df)}")
    print('=' * 80)
    print(tabulate(display_df, headers='keys', tablefmt='grid', showindex=False))

    # Статистика
    print(f"\n{'=' * 80}")
    print("СТАТИСТИКА:")
    print(f"  Средняя цена: £{df['price'].mean():.2f}")
    print(f"  Минимальная цена: £{df['price'].min():.2f}")
    print(f"  Максимальная цена: £{df['price'].max():.2f}")
    print(f"  Средний рейтинг: {df['rating'].mean():.2f}")
    print('=' * 80)


def main():
    """Главная функция для запуска анализатора."""
    parser = argparse.ArgumentParser(description='Анализ спарсенных данных о книгах')
    parser.add_argument('--input', type=str, default='data/raw_data.csv',
                        help='Путь к CSV файлу с данными (по умолчанию: data/raw_data.csv)')
    parser.add_argument('--max_price', type=float, default=None,
                        help='Максимальная цена для фильтрации')
    parser.add_argument('--min_rating', type=int, default=None, choices=[1, 2, 3, 4, 5],
                        help='Минимальный рейтинг (1-5)')
    parser.add_argument('--keyword', type=str, default=None,
                        help='Ключевое слово для поиска в названии')
    parser.add_argument('--sort', type=str, default='price', choices=['price', 'rating'],
                        help='Сортировать по полю (price или rating)')
    parser.add_argument('--order', type=str, default='asc', choices=['asc', 'desc'],
                        help='Порядок сортировки (asc - по возрастанию, desc - по убыванию)')
    parser.add_argument('--top', type=int, default=10,
                        help='Количество записей для вывода (по умолчанию: 10)')

    args = parser.parse_args()

    print("Загрузка данных...")
    df = load_data(args.input)
    print(f"Загружено записей: {len(df)}")
    print("-" * 80)

    # Применяем фильтры
    df = filter_by_price(df, args.max_price)
    df = filter_by_keyword(df, args.keyword)
    df = filter_by_rating(df, args.min_rating)

    # Сортируем
    ascending = (args.order == 'asc')
    df = sort_data(df, args.sort, ascending)

    # Выводим результаты
    display_results(df, args.top)


if __name__ == '__main__':
    main()
