"""Небольшие вспомогательные скрипты"""
import random

from flask import abort




def booking_link_checker(path, teacher):
    """Проверяет корректность URL в роуте booking"""
    to_check_list = path.split('/')[-4:]
    weekDay = to_check_list[1]
    time = to_check_list[2]


    if weekDay in teacher.get_free():
        times_range = teacher.get_free()[weekDay]
        if time in times_range:
            return True
    abort(404)


def random_list(count, sliced):
    """Перемешивает все id и возращает sliced первых id"""
    shuffled_figures = [i for i in range(count)]
    random.shuffle(shuffled_figures)
    return shuffled_figures[:sliced]
