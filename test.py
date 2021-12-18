import unittest
from main import timetable
class Testtimetable(unittest.TestCase):
    def test_area(self):
        self.assertEqual(timetable('Зиганшин Амир'),'306150')
        self.assertEqal(timetable('Гаврилов Степан Сергеевич'),'306134')
        self.assertEqal(timetable('Вася Пупкин',''))
    #проверка на человека
    def test_types:
        self.assertRaises(TypeError, timetable,'')
        self.assertRaises(TypeError, timetable, '23+12')
    #проверка на неправильный ввод данных
from main import exams
class Testexams(unittest.TestCase):
    def test_area(self):
        self.assertEqual(exams(),1)
    # есть экзамен за последние 2 месяца
        self.assertEqual(exams(),0)
    #нет экзаменов в блжайших 2 месяца
    
