"""StudyOS planning and AI services.

The planner is intentionally hybrid:
- Django/Python owns hard constraints and all academic arithmetic.
- OpenAI is optional and is used to rank/explain already-known topics.
- If OPENAI_API_KEY is missing or the API fails, the deterministic planner still works.
"""

from datetime import date, datetime, timedelta
import json
import os

from django.db.models import Sum
from django.utils import timezone

from apps.academics.models import Semester, Subject, Topic, TopicProgress
from apps.study.models import StudySession, Revision
from apps.assessments.models import Assessment, Mark
from apps.quizzes.models import QuizAttempt
from apps.question_papers.models import Question


MAX_SUBJECTS_PER_DAY = 2
DEFAULT_DAILY_MINUTES = 180
DEFAULT_STUDY_DAYS_PER_WEEK = 5
HIGH_CREDIT_MIN = 3
HIGH_CREDIT_SESSIONS = 2
LOW_CREDIT_SESSIONS = 1


def current_semester():
    return Semester.objects.order_by('-number').first()


def topic_features(topic, user):
    attempts = list(topic.quiz_attempts.filter(user=user))
    total_questions = sum(a.questions for a in attempts)
    correct = sum(a.correct for a in attempts)
    accuracy = (correct / total_questions * 100) if total_questions else 0
    sessions = topic.study_sessions.filter(user=user)
    minutes = sessions.aggregate(x=Sum('minutes'))['x'] or 0
    revisions = topic.revisions.filter(user=user).count()
    progress = TopicProgress.objects.filter(user=user, topic=topic).first()
    completion = 100 if progress and progress.completed else 0
    last_studied = sessions.order_by('-studied_on').values_list('studied_on', flat=True).first()
    if last_studied is None and progress:
        last_studied = progress.last_studied
    study_score = min(100, minutes / 60 * 25)
    revision_score = min(100, revisions * 20)
    quiz_score = accuracy if total_questions else 35
    mastery = round(
        .35 * quiz_score
        + .20 * study_score
        + .15 * revision_score
        + .30 * completion,
        1,
    )
    frequency = sum(q.frequency for q in topic.past_questions.all())
    return {
        'topic': topic,
        'mastery': mastery,
        'completed': bool(progress and progress.completed),
        'last_studied': last_studied,
        'accuracy': round(accuracy, 1),
        'minutes': minutes,
        'revisions': revisions,
        'frequency': frequency,
        'question_count': topic.past_questions.count(),
        'importance': topic.importance,
    }


def sync_mastery(user):
    topics = Topic.objects.prefetch_related('past_questions')
    for topic in topics:
        features = topic_features(topic, user)
        TopicProgress.objects.update_or_create(
            user=user,
            topic=topic,
            defaults={
                'mastery': features['mastery'],
                'last_studied': features['last_studied'],
            },
        )


def _urgency(days_left):
    if days_left <= 0:
        return 100.0
    # 29 days -> moderate urgency, then accelerates as the exam approaches.
    return max(10.0, min(100.0, 100 - days_left * 3.0))


def priority_score(features, days_left=29, credit=3):
    weakness = 100 - features['mastery']
    importance = features['importance'] * 20
    frequency = min(100, features['frequency'] * 20)
    urgency = _urgency(days_left)

    if features['minutes'] == 0:
        stale = 100
    elif features['last_studied'] is None:
        stale = 70
    else:
        age = (timezone.now() - features['last_studied']).days
        stale = min(100, 20 + age * 8)

    credit_weight = min(100, credit * 25)

    score = (
        .30 * weakness
        + .22 * frequency
        + .18 * urgency
        + .14 * importance
        + .10 * stale
        + .06 * credit_weight
    )
    return round(score, 2)


def reason(features, days_left):
    parts = []
    if features['mastery'] < 60:
        parts.append('low mastery')
    if features['frequency']:
        parts.append(f"PYQs/repetitions {features['frequency']}×")
    if features['importance'] >= 4:
        parts.append('high syllabus importance')
    if days_left <= 14:
        parts.append('CIA is close')
    if features['minutes'] == 0:
        parts.append('not studied yet')
    return ' · '.join(parts) or 'balanced next-step coverage'


def next_assessment(semester=None):
    semester = semester or current_semester()
    if not semester:
        return None

    today = timezone.localdate()
    candidates = []
    if semester.cia1_start_date:
        candidates.append(('CIA-1', semester.cia1_start_date, semester.cia1_end_date, 'cia'))
    if semester.cia2_start_date:
        candidates.append(('CIA-2', semester.cia2_start_date, semester.cia2_end_date, 'cia'))
    if semester.see_start_date:
        candidates.append(('SEE', semester.see_start_date, semester.see_start_date, 'see'))

    active = [
        item for item in candidates
        if item[1] <= today and item[2] and today <= item[2]
    ]
    if active:
        name, start, end, kind = sorted(active, key=lambda x: x[1], reverse=True)[0]
        return {
            'name': name,
            'type': kind,
            'start_date': str(start),
            'end_date': str(end),
            'days_left': 0,
            'status': 'in_progress',
        }

    future = [item for item in candidates if item[1] > today]
    if not future:
        return None
    name, start, end, kind = sorted(future, key=lambda x: x[1])[0]
    return {
        'name': name,
        'type': kind,
        'start_date': str(start),
        'end_date': str(end),
        'days_left': max(0, (start - today).days),
        'status': 'upcoming',
    }


def assessment_scope(subject, assessment_name):
    """Return the topic queryset for the current assessment.

    CIE-1 follows the user's current planning rule of approximately 2.5 modules:
    all topics from Modules 1 and 2 plus the first half of Module 3.
    CIA-2 uses the remaining half of Module 3 plus Modules 4 and 5.
    SEE uses the full syllabus.
    """
    modules = list(subject.modules.prefetch_related('topics').order_by('number'))
    if not modules:
        return []

    if assessment_name == 'CIA-1':
        selected = modules[:2]
        if len(modules) >= 3:
            half = (len(modules[2].topics.all()) + 1) // 2
            selected_topics = [*modules[0].topics.all(), *modules[1].topics.all()]
            selected_topics += list(modules[2].topics.all())[:half]
            return selected_topics
        return [topic for module in selected for topic in module.topics.all()]

    if assessment_name == 'CIA-2':
        selected_topics = []
        if len(modules) >= 3:
            topics = list(modules[2].topics.all())
            half = (len(topics) + 1) // 2
            selected_topics.extend(topics[half:])
            selected_topics.extend(topic for module in modules[3:] for topic in module.topics.all())
            return selected_topics
        return [topic for module in modules[2:] for topic in module.topics.all()]

    return [topic for module in modules for topic in module.topics.all()]


def _candidate_rows(semester, assessment, subjects, user):
    rows = []
    days_left = assessment['days_left'] if assessment else 29
    assessment_name = assessment['name'] if assessment else 'CIA-1'

    for subject in subjects:
        topics = assessment_scope(subject, assessment_name)
        for topic in topics:
            features = topic_features(topic, user)
            if features['completed']:
                continue
            score = priority_score(features, days_left, subject.credits)
            rows.append({
                'topic_id': topic.id,
                'topic': topic.name,
                'subject_id': subject.id,
                'subject': subject.name,
                'code': subject.code,
                'credits': subject.credits,
                'module': topic.module.number,
                'module_name': topic.module.name,
                'estimated_minutes': topic.estimated_minutes,
                'mastery': features['mastery'],
                'frequency': features['frequency'],
                'question_count': features['question_count'],
                'questions': [q.text for q in sorted(topic.past_questions.all(), key=lambda q: q.frequency, reverse=True)[:3]],
                'importance': features['importance'],
                'priority': score,
                'reason': reason(features, days_left),
            })
    rows.sort(key=lambda row: (-row['priority'], -row['frequency'], row['subject']))
    return rows


def _ai_rank_candidates(candidates, assessment):
    """Optionally let OpenAI reorder the deterministic candidates.

    The model can only select IDs already supplied by StudyOS. This prevents the
    AI from inventing syllabus topics or dates. If no API key is configured,
    the local ranking is used unchanged.
    """
    api_key = os.getenv('OPENAI_API_KEY', '').strip()
    if not api_key or not candidates:
        return candidates, False

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        model = os.getenv('OPENAI_MODEL', 'gpt-5.6-luna')
        compact = [
            {
                'id': c['topic_id'],
                'subject': c['subject'],
                'credits': c['credits'],
                'module': c['module'],
                'topic': c['topic'],
                'estimated_minutes': c['estimated_minutes'],
                'pyq_frequency': c['frequency'],
                'mastery': c['mastery'],
                'importance': c['importance'],
                'local_priority': c['priority'],
            }
            for c in candidates[:40]
        ]
        schema = {
            'type': 'object',
            'additionalProperties': False,
            'properties': {
                'ordered_topic_ids': {'type': 'array', 'items': {'type': 'integer'}},
                'reasons': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'additionalProperties': False,
                        'properties': {
                            'topic_id': {'type': 'integer'},
                            'reason': {'type': 'string'},
                        },
                        'required': ['topic_id', 'reason'],
                    },
                },
            },
            'required': ['ordered_topic_ids', 'reasons'],
        }
        response = client.responses.create(
            model=model,
            input=[
                {
                    'role': 'system',
                    'content': (
                        'You are the ranking layer of StudyOS. Rank only the supplied topic IDs. '
                        'Prioritize repeated/high-frequency past questions, low mastery, urgency, '
                        'importance and reasonable study time. Never invent topics, dates or IDs. '
                        'Do not change the supplied exam scope.'
                    ),
                },
                {
                    'role': 'user',
                    'content': json.dumps({'assessment': assessment, 'topics': compact}),
                },
            ],
            text={'format': {'type': 'json_schema', 'name': 'studyos_topic_ranking', 'strict': True, 'schema': schema}},
        )
        payload = json.loads(response.output_text)
        valid_ids = {c['topic_id'] for c in candidates}
        ordered_ids = [x for x in payload['ordered_topic_ids'] if x in valid_ids]
        if not ordered_ids:
            return candidates, False

        by_id = {c['topic_id']: c for c in candidates}
        reasons = {r['topic_id']: r['reason'] for r in payload.get('reasons', []) if r['topic_id'] in valid_ids}
        ranked = []
        for topic_id in ordered_ids:
            row = dict(by_id[topic_id])
            if topic_id in reasons:
                row['ai_reason'] = reasons[topic_id]
            ranked.append(row)
        ranked.extend(c for c in candidates if c['topic_id'] not in {r['topic_id'] for r in ranked})
        return ranked, True
    except Exception:
        # A missing package, invalid key, quota error, unavailable model, or schema
        # issue must never break the academic planner.
        return candidates, False


def _weekly_slots(subjects, days_per_week=DEFAULT_STUDY_DAYS_PER_WEEK):
    """Allocate subject slots under the user's 2-subject/day constraint.

    Five weekdays provide ten subject slots. The current Semester 3 curriculum
    has five subjects at >=3 credits (10 requested slots) plus two 1-credit
    subjects (2 requested slots), so all requested minimums cannot fit at once.
    High-credit minimums are protected and low-credit subjects are reported as
    a rotating overflow rather than silently breaking the two-subject rule.
    """
    study_days = max(4, min(5, int(days_per_week)))
    weekday_dates = []
    start = timezone.localdate()
    if start.weekday() >= 5:
        start += timedelta(days=(7 - start.weekday()))
    else:
        start -= timedelta(days=start.weekday())
    for offset in range(7):
        d = start + timedelta(days=offset)
        if d.weekday() < study_days:
            weekday_dates.append(d)

    high = [s for s in subjects if s.credits >= HIGH_CREDIT_MIN]
    low = [s for s in subjects if s.credits < HIGH_CREDIT_MIN]
    requested = len(high) * HIGH_CREDIT_SESSIONS + len(low) * LOW_CREDIT_SESSIONS
    capacity = len(weekday_dates) * MAX_SUBJECTS_PER_DAY

    # Protect every high-credit subject's twice-weekly requirement first.
    slots = []
    for subject in high:
        slots.extend([subject, subject])

    # If there is spare capacity, add the lower-credit subjects. With the current
    # 7-subject Semester 3 data there is no spare capacity, so they rotate.
    for subject in low:
        if len(slots) < capacity:
            slots.append(subject)

    # Balance the high-credit sequence so a subject is not placed twice on the same day.
    schedule = {d: [] for d in weekday_dates}
    cursor = 0
    for subject in slots:
        placed = False
        for _ in range(len(weekday_dates)):
            d = weekday_dates[cursor % len(weekday_dates)]
            cursor += 1
            if len(schedule[d]) < MAX_SUBJECTS_PER_DAY and subject.id not in [x.id for x in schedule[d]]:
                schedule[d].append(subject)
                placed = True
                break
        if not placed:
            break

    overflow = [s.name for s in low if sum(1 for day in schedule.values() for x in day if x.id == s.id) == 0]
    return schedule, {
        'requested_subject_sessions': requested,
        'available_subject_slots': capacity,
        'constraint_conflict': requested > capacity,
        'overflow_low_credit_subjects': overflow,
        'study_days_per_week': study_days,
    }


def _tasks_for_subject(candidate_rows, subject, minutes_budget):
    rows = [r for r in candidate_rows if r['subject_id'] == subject.id]
    tasks = []
    remaining = max(30, minutes_budget)
    for row in rows:
        if remaining <= 0 or len(tasks) >= 4:
            break
        minutes = min(row['estimated_minutes'], remaining, 60)
        minutes = max(20, minutes)
        task = dict(row)
        task['minutes'] = minutes
        task['practice_questions'] = min(5, max(1, row['frequency'] or 1))
        task['questions'] = row.get('questions', [])
        task['practice_note'] = (
            f"Practice {task['practice_questions']} PYQ(s), prioritizing repeated questions."
            if row['frequency']
            else 'Practice 3 representative questions after learning the topic.'
        )
        task['completed'] = False
        tasks.append(task)
        remaining -= minutes
    return tasks


def build_plan(minutes=DEFAULT_DAILY_MINUTES, days_per_week=DEFAULT_STUDY_DAYS_PER_WEEK, use_ai=True, *, user):
    sync_mastery(user)
    semester = current_semester()
    today = timezone.localdate()
    assessment = next_assessment(semester)
    subjects = list(
        Subject.objects.filter(semester=semester)
        .prefetch_related('modules__topics')
        .order_by('-credits', 'name')
    ) if semester else []

    candidates = _candidate_rows(semester, assessment, subjects, user) if semester else []
    ai_used = False
    if use_ai:
        candidates, ai_used = _ai_rank_candidates(candidates, assessment)

    schedule, constraints = _weekly_slots(subjects, days_per_week)
    days = []
    today_entry = None

    for d in sorted(schedule):
        day_subjects = []
        active_subjects = schedule[d]
        per_subject = max(30, minutes // max(1, len(active_subjects)))
        for subject in active_subjects:
            tasks = _tasks_for_subject(candidates, subject, per_subject)
            day_subjects.append({
                'subject_id': subject.id,
                'subject': subject.name,
                'code': subject.code,
                'credits': subject.credits,
                'tasks': tasks,
                'minutes': sum(t['minutes'] for t in tasks),
            })
        entry = {
            'date': str(d),
            'day': d.strftime('%A'),
            'is_today': d == today,
            'is_study_day': True,
            'subjects': day_subjects,
            'total_minutes': sum(s['minutes'] for s in day_subjects),
        }
        days.append(entry)
        if d == today:
            today_entry = entry

    # If today is a weekend/rest day, expose a clear next-study-day pointer.
    if today_entry is None:
        next_day = next((d for d in days if d['date'] > str(today)), None)
        today_entry = {
            'date': str(today),
            'day': today.strftime('%A'),
            'is_today': True,
            'is_study_day': False,
            'subjects': [],
            'total_minutes': 0,
            'rest_day': True,
            'next_study_day': next_day['date'] if next_day else None,
        }

    return {
        'date': str(today),
        'semester': {
            'id': semester.id if semester else None,
            'number': semester.number if semester else None,
            'name': semester.name if semester else None,
        },
        'next_assessment': assessment,
        'days_until_next_assessment': assessment['days_left'] if assessment else None,
        'daily_minutes_target': minutes,
        'max_subjects_per_day': MAX_SUBJECTS_PER_DAY,
        'study_days_per_week': constraints['study_days_per_week'],
        'ai_used': ai_used,
        'constraint_status': constraints,
        'today': today_entry,
        'week': days,
    }


def subject_progress(subject, user):
    topics = Topic.objects.filter(module__subject=subject)
    total = topics.count()
    done = TopicProgress.objects.filter(user=user, topic__in=topics, completed=True).count()
    return round(done / total * 100, 1) if total else 0


def performance_prediction(subject_id=None, *, user):
    qs = Mark.objects.filter(user=user).select_related('assessment__subject')
    if subject_id:
        qs = qs.filter(assessment__subject_id=subject_id)
    marks = [m.score / m.assessment.max_marks * 100 for m in qs]
    if len(marks) >= 2:
        recent = sum(marks[-3:]) / min(3, len(marks))
        return {'method': 'weighted recent average', 'prediction': round(recent, 1), 'sample_size': len(marks)}
    topics = Topic.objects.filter(module__subject_id=subject_id) if subject_id else Topic.objects.all()
    feature_rows = [topic_features(topic, user)['mastery'] for topic in topics]
    mastery = sum(feature_rows) / len(feature_rows) if feature_rows else 0
    return {
        'method': 'mastery baseline',
        'prediction': round(mastery, 1),
        'sample_size': len(marks),
        'note': 'Need more marks for a personalized prediction.',
    }


def _assistant_context(user):
    """Build a compact, factual snapshot for the conversational AI coach.

    The LLM receives only data already stored in StudyOS. Academic arithmetic
    and hard scheduling constraints remain owned by the deterministic planner.
    """
    sync_mastery(user)
    semester = current_semester()
    assessment = next_assessment(semester)
    plan = build_plan(use_ai=False, user=user) if semester else {}

    subject_rows = []
    if semester:
        for subject in Subject.objects.filter(semester=semester).prefetch_related('modules__topics').order_by('-credits', 'name'):
            topics = list(Topic.objects.filter(module__subject=subject))
            total = len(topics)
            features = [topic_features(topic, user) for topic in topics]
            done = sum(1 for row in features if row['completed'])
            avg_mastery = round(sum(row['mastery'] for row in features) / total, 1) if total else 0
            subject_rows.append({
                'code': subject.code,
                'name': subject.name,
                'credits': subject.credits,
                'progress_percent': round(done / total * 100, 1) if total else 0,
                'average_mastery': avg_mastery,
                'topics_remaining': total - done,
            })

    topic_rows = []
    if semester:
        for topic in Topic.objects.select_related('module__subject').prefetch_related('past_questions'):
            features = topic_features(topic, user)
            if features['completed']:
                continue
            topic_rows.append({
                'id': topic.id,
                'subject': topic.module.subject.name,
                'code': topic.module.subject.code,
                'module': topic.module.number,
                'topic': topic.name,
                'mastery': features['mastery'],
                'quiz_accuracy': features['accuracy'],
                'pyq_frequency': features['frequency'],
                'importance': features['importance'],
                'estimated_minutes': topic.estimated_minutes,
                'priority': priority_score(
                    features,
                    assessment['days_left'] if assessment else 29,
                    topic.module.subject.credits,
                ),
            })
        topic_rows.sort(key=lambda x: (-x['priority'], -x['pyq_frequency']))
        topic_rows = topic_rows[:25]

    return {
        'semester': {
            'number': semester.number if semester else None,
            'name': semester.name if semester else None,
            'academic_year': semester.academic_year if semester else None,
        },
        'next_assessment': assessment,
        'subjects': subject_rows,
        'top_unfinished_topics': topic_rows,
        'today_plan': plan.get('today', {}),
        'weekly_constraints': {
            'study_days_per_week': plan.get('study_days_per_week', DEFAULT_STUDY_DAYS_PER_WEEK),
            'max_subjects_per_day': MAX_SUBJECTS_PER_DAY,
            'constraint_status': plan.get('constraint_status', {}),
        },
    }


def _local_chat(message, user):
    """Useful offline fallback when OpenAI is not configured."""
    text = message.lower().strip()
    context = _assistant_context(user)

    if any(k in text for k in ['what should i study', 'what do i study', 'study today', 'today']):
        items = [task for subject in context['today_plan'].get('subjects', []) for task in subject.get('tasks', [])]
        if not items:
            next_day = context['today_plan'].get('next_study_day')
            return (
                'Today is a planned rest day.'
                + (f' Your next study day is {next_day}.' if next_day else '')
            )
        return 'Today I would focus on: ' + '; '.join(
            f"{x['subject']} — {x['topic']} ({x['minutes']} min)" for x in items
        ) + '.'

    if 'weak' in text or 'weakest' in text:
        rows = sorted(
            [(x['mastery'], x['subject'], x['topic']) for x in context['top_unfinished_topics']],
            key=lambda x: x[0],
        )
        return (
            'Your weakest unfinished tracked topics are: '
            + '; '.join(f'{s} — {n} ({m:.0f}% mastery)' for m, s, n in rows[:5])
            + '.'
            if rows else 'No topic performance data is available yet.'
        )

    if 'exam' in text or 'internal' in text or 'cia' in text:
        assessment = context['next_assessment']
        if not assessment:
            return 'No upcoming semester assessment is recorded.'
        return (
            f"Your next assessment window is {assessment['name']} from "
            f"{assessment['start_date']} to {assessment['end_date']}. "
            f"It is {assessment['days_left']} days away."
        )

    if 'progress' in text or 'how am i doing' in text:
        rows = context['subjects']
        return (
            'Current subject progress: '
            + '; '.join(f"{x['name']} {x['progress_percent']:.0f}%" for x in rows)
            + '.'
            if rows else 'No subject data is available yet.'
        )

    if 'cgpa' in text or 'sgpa' in text:
        return (
            'StudyOS can use your subject credits, topic mastery and recorded performance '
            'to allocate attention. Exact grade requirements still need your college grading map.'
        )

    if 'hello' in text or text in {'hi', 'hey'}:
        return (
            'Hey! I am your StudyOS academic coach. Ask me what to study, teach me a topic, '
            'quiz me, analyze my weak areas, explain the plan, or analyze repeated PYQs.'
        )

    return (
        'I can help with your StudyOS plan, syllabus topics, weak areas, exam timing, '
        'PYQ priorities, quizzes and SGPA planning. OpenAI becomes active when your backend '
        'has an OPENAI_API_KEY.'
    )


def chat(message, history=None, *, user):
    """Conversational academic coach.

    OpenAI is used only for language/reasoning over the supplied StudyOS data.
    If the API is unavailable, the deterministic local assistant remains usable.
    """
    message = str(message or '').strip()
    if not message:
        return {
            'answer': 'Ask me something about your study plan, syllabus, PYQs or performance.',
            'ai_used': False,
        }

    context = _assistant_context(user)
    api_key = os.getenv('OPENAI_API_KEY', '').strip()
    if not api_key:
        return {'answer': _local_chat(message, user), 'ai_used': False, 'model': None}

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        model = os.getenv('OPENAI_MODEL', 'gpt-5.6-luna')
        safe_history = []
        for item in (history or [])[-8:]:
            role = item.get('role')
            content = str(item.get('content', '')).strip()
            if role in {'user', 'assistant'} and content:
                safe_history.append({'role': role, 'content': content})

        instructions = (
            'You are StudyOS, a personal academic coach for a college student. '
            'Use the supplied StudyOS context as the source of truth for dates, syllabus, '
            'progress, mastery, PYQ frequency and the generated plan. Never invent a topic, '
            'exam date, question frequency, mark, or college rule. '
            'The deterministic planner owns hard constraints such as maximum 2 subjects/day '
            'and 4-5 study days/week; explain those constraints rather than overriding them. '
            'When asked what to study, recommend concrete stored topics and explain the evidence. '
            'When asked to teach, teach clearly from basics and connect to the stored syllabus. '
            'When asked to quiz, generate questions from the stored topics and do not claim they '
            'are actual PYQs unless they are listed as such. Keep answers practical and concise.'
        )

        user_payload = {
            'studyos_context': context,
            'conversation': safe_history,
            'current_message': message,
        }

        response = client.responses.create(
            model=model,
            instructions=instructions,
            input=json.dumps(user_payload),
        )

        answer = (response.output_text or '').strip()
        if not answer:
            raise RuntimeError('OpenAI returned an empty response.')

        return {'answer': answer, 'ai_used': True, 'model': model}
    except Exception:
        return {
            'answer': _local_chat(message, user),
            'ai_used': False,
            'model': None,
            'fallback': True,
        }
