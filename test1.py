import unittest

from main import timetable
from main import test1


class Test(unittest.TestCase):


    def test_test1(self):
        self.assertEqual(test1('Зиганшин Амир'), '306150')





if __name__ == "__main__":
    unittest.main()