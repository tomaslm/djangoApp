import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Question


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date is in the future
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date is mode than 1 day ago
        """
        time_older_than_one_day = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time_older_than_one_day)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_publichsed_recently() returns True for questions whse pub_date is less than 1 day ago
        """
        time_less_than_one_day_ago = timezone.now() - datetime.timedelta(hours=15)
        recent_question = Question(pub_date=time_less_than_one_day_ago)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    """
        Create a question with the given text and published in a given number of days
        offset to now (negative for published in the past or positive to those not yet published)
        """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls available")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_future_question(self):
        """
        Questions with a pub_date in the future are not displayed
        """
        create_question("Future question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertEquals(response.status_code, 200)
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_future_questions_and_past_question(self):
        """
        If past and future exists, should show only past
        """
        create_question("Future question", days=30)
        create_question("Past question", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"], ["<Question: Past question>"]
        )

    def test_two_past_questions(self):
        """
        All past questions should be showed
        """
        create_question("Past question 1", days=-30)
        create_question("Past question 2", days=-31)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            ["<Question: Past question 1>", "<Question: Past question 2>"],
        )

