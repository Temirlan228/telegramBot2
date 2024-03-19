import unittest
from unittest.mock import MagicMock

from main import show_answer


class TestShowAnswer(unittest.TestCase):
    def test_show_answer_with_answers(self):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = [(1, 2, 'Answer 1'), (2, 2, 'Answer 2')]

        question_id = 2
        question_text, answers = show_answer(question_id, mock_conn)

        self.assertEqual(question_text, "Question Text")
        self.assertListEqual(answers, ['Answer 1', 'Answer 2'])

    def test_show_answer_no_answers(self):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = []

        question_id = 2
        question_text, answers = show_answer(question_id, mock_conn)

        self.assertEqual(question_text, "В базе данных нет вопросов.")
        self.assertListEqual(answers, [])

if __name__ == '__main__':
    unittest.main()
