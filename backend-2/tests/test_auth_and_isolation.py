from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.academics.models import Module, Semester, Subject, Topic, TopicProgress
from apps.assessments.models import Assessment, Mark
from apps.study.models import StudySession


User = get_user_model()


class AuthenticationTests(TestCase):
    def test_registration_requires_csrf_and_restores_session(self):
        client = APIClient(enforce_csrf_checks=True)
        response = client.get('/api/accounts/csrf/')
        token = response.data['csrfToken']

        response = client.post(
            '/api/accounts/register/',
            {
                'name': 'Study User',
                'email': 'study@example.com',
                'password': 'mC7!random-Garden-piano#',
            },
            format='json',
            HTTP_X_CSRFTOKEN=token,
        )

        self.assertEqual(response.status_code, 201)
        self.assertNotIn('password', response.data['user'])
        self.assertEqual(client.get('/api/accounts/session/').data['user']['email'], 'study@example.com')

        csrf = client.get('/api/accounts/csrf/').data['csrfToken']
        self.assertEqual(client.post('/api/accounts/logout/', {}, format='json', HTTP_X_CSRFTOKEN=csrf).status_code, 204)
        csrf = client.get('/api/accounts/csrf/').data['csrfToken']
        invalid = client.post(
            '/api/accounts/login/',
            {'email': 'study@example.com', 'password': 'wrong-password'},
            format='json',
            HTTP_X_CSRFTOKEN=csrf,
        )
        self.assertEqual(invalid.status_code, 400)
        csrf = client.get('/api/accounts/csrf/').data['csrfToken']
        valid = client.post(
            '/api/accounts/login/',
            {'email': 'study@example.com', 'password': 'mC7!random-Garden-piano#'},
            format='json',
            HTTP_X_CSRFTOKEN=csrf,
        )
        self.assertEqual(valid.status_code, 200)

    def test_private_api_rejects_anonymous_requests(self):
        response = APIClient().get('/api/academics/subjects/')
        self.assertIn(response.status_code, (401, 403))


class UserDataIsolationTests(TestCase):
    def setUp(self):
        self.first_user = User.objects.create_user(
            username='first@example.com', email='first@example.com', password='a-long-password-1'
        )
        self.second_user = User.objects.create_user(
            username='second@example.com', email='second@example.com', password='a-long-password-2'
        )
        semester = Semester.objects.create(number=3)
        subject = Subject.objects.create(semester=semester, name='Algorithms', code='ALG')
        module = Module.objects.create(subject=subject, number=1, name='Foundations')
        self.topic = Topic.objects.create(module=module, name='Graph traversal')
        self.assessment = Assessment.objects.create(
            subject=subject, name='CIA 1', assessment_type='internal_1', date='2026-10-26'
        )
        self.first_client = APIClient()
        self.first_client.force_authenticate(self.first_user)
        self.second_client = APIClient()
        self.second_client.force_authenticate(self.second_user)

    def test_topic_completion_is_per_user(self):
        response = self.first_client.post(
            f'/api/academics/topics/{self.topic.pk}/complete/',
            {'completed': True},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['completed'])
        self.assertFalse(self.second_client.get(f'/api/academics/topics/{self.topic.pk}/').data['completed'])
        subject_detail = self.first_client.get(f'/api/academics/subjects/{self.topic.module.subject_id}/syllabus/')
        other_detail = self.second_client.get(f'/api/academics/subjects/{self.topic.module.subject_id}/syllabus/')
        self.assertEqual(subject_detail.data['progress'], 100)
        self.assertEqual(subject_detail.data['modules'][0]['progress'], 100)
        self.assertEqual(other_detail.data['modules'][0]['progress'], 0)
        self.assertEqual(TopicProgress.objects.filter(topic=self.topic).count(), 1)

    def test_personal_records_ignore_client_supplied_owner(self):
        response = self.first_client.post(
            '/api/study/sessions/',
            {'topic': self.topic.pk, 'minutes': 35, 'user': self.second_user.pk},
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        session = StudySession.objects.get(pk=response.data['id'])
        self.assertEqual(session.user, self.first_user)
        self.assertEqual(len(self.first_client.get('/api/study/sessions/').data), 1)
        self.assertEqual(len(self.second_client.get('/api/study/sessions/').data), 0)
        session_url = f'/api/study/sessions/{session.pk}/'
        self.assertEqual(self.second_client.get(session_url).status_code, 404)
        self.assertEqual(self.second_client.patch(session_url, {'notes': 'intrusion'}, format='json').status_code, 404)
        self.assertEqual(self.second_client.delete(session_url).status_code, 404)

        response = self.first_client.post(
            '/api/assessments/marks/',
            {
                'assessment': self.assessment.pk,
                'score': 42,
                'user': self.second_user.pk,
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        mark = Mark.objects.get(pk=response.data['id'])
        self.assertEqual(mark.user, self.first_user)
        self.assertEqual(len(self.second_client.get('/api/assessments/marks/').data), 0)
        mark_url = f'/api/assessments/marks/{mark.pk}/'
        self.assertEqual(self.second_client.get(mark_url).status_code, 404)
        self.assertEqual(self.second_client.patch(mark_url, {'note': 'intrusion'}, format='json').status_code, 404)
        self.assertEqual(self.second_client.delete(mark_url).status_code, 404)

    def test_shared_syllabus_is_read_only(self):
        response = self.first_client.post(
            '/api/academics/subjects/',
            {'semester': 1, 'name': 'Injected', 'code': 'INJ'},
            format='json',
        )
        self.assertEqual(response.status_code, 405)

    def test_analytics_and_study_plan_use_only_current_user_data(self):
        TopicProgress.objects.create(user=self.first_user, topic=self.topic, completed=True)
        StudySession.objects.create(user=self.first_user, topic=self.topic, minutes=40)
        quiz = self.first_client.post(
            '/api/quizzes/attempts/',
            {'topic': self.topic.pk, 'questions': 10, 'correct': 8, 'user': self.second_user.pk},
            format='json',
        )
        self.assertEqual(quiz.status_code, 201)

        first_analytics = self.first_client.get('/api/analytics/dashboard/')
        second_analytics = self.second_client.get('/api/analytics/dashboard/')
        overview = self.first_client.get('/api/analytics/overview/')
        self.assertEqual(first_analytics.status_code, 200)
        self.assertEqual(second_analytics.status_code, 200)
        self.assertEqual(overview.status_code, 200)
        self.assertEqual(first_analytics.data['study_minutes_week'], 40)
        self.assertEqual(second_analytics.data['study_minutes_week'], 0)
        self.assertEqual(first_analytics.data['quiz_accuracy_week'], 80)
        self.assertEqual(second_analytics.data['quiz_accuracy_week'], 0)
        self.assertEqual(overview.data['study_minutes'], 40)
        self.assertEqual(first_analytics.data['subjects'][0]['progress'], 100)
        self.assertEqual(second_analytics.data['subjects'][0]['progress'], 0)

        first_plan = self.first_client.get('/api/ai/study-plan/?ai=0').data
        second_plan = self.second_client.get('/api/ai/study-plan/?ai=0').data
        first_topic_ids = {
            task['topic_id']
            for day in first_plan['week']
            for subject in day['subjects']
            for task in subject['tasks']
        }
        second_topic_ids = {
            task['topic_id']
            for day in second_plan['week']
            for subject in day['subjects']
            for task in subject['tasks']
        }
        self.assertNotIn(self.topic.pk, first_topic_ids)
        self.assertIn(self.topic.pk, second_topic_ids)