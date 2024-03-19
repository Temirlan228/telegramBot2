import unittest
from unittest.mock import MagicMock
import random

from main import random_answer


class TestRandomAnswer(unittest.TestCase):
    def setUp(self):

        random.seed(42)

    def test_random_answer(self):

        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.return_value = ('Sample Question',)

        question_id = 1
        list_answer = ['Answer 1', 'Answer 2', 'Answer 3']

        question_text, shuffled_answers = random_answer(list_answer.copy(), question_id, mock_conn)

        self.assertEqual(question_text, 'Sample Question')
        self.assertNotEqual(list_answer, shuffled_answers, "Answers should be shuffled")
        self.assertEqual(set(list_answer), set(shuffled_answers), "Shuffled answers should contain the same elements")

    def tearDown(self):

        random.seed()


if __name__ == '__main__':
    unittest.main()
