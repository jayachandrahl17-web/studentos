from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
import os
from apps.academics.models import Subject, Topic
from apps.ai_engine.services import (
    build_plan,
    performance_prediction,
    chat,
    sync_mastery,
    topic_features,
    priority_score,
    current_semester,
    next_assessment,
)
from .models import AIInteraction


@api_view(['GET'])
def overview(request):
    sync_mastery(request.user)
    topics = []
    assessment = next_assessment()
    days_left = assessment['days_left'] if assessment else 29
    for t in Topic.objects.select_related('module__subject').prefetch_related('quiz_attempts', 'revisions', 'past_questions'):
        f = topic_features(t, request.user)
        topics.append({
            'id': t.id,
            'topic': t.name,
            'subject': t.module.subject.name,
            'mastery': f['mastery'],
            'priority': priority_score(f, days_left, t.module.subject.credits),
            'frequency': f['frequency'],
        })
    topics.sort(key=lambda x: x['priority'], reverse=True)
    return Response({'topics': topics[:20], 'next_plan': build_plan(user=request.user)})


@api_view(['GET'])
def mastery(request):
    sync_mastery(request.user)
    return Response([
        {'id': t.id, 'topic': t.name, 'subject': t.module.subject.name, 'mastery': topic_features(t, request.user)['mastery']}
        for t in Topic.objects.select_related('module__subject')
    ])


@api_view(['GET'])
def risk(request):
    sync_mastery(request.user)
    data = []
    for t in Topic.objects.select_related('module__subject'):
        mastery = topic_features(t, request.user)['mastery']
        if mastery < 45:
            risk_level = 'high'
        elif mastery < 70:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        data.append({'id': t.id, 'topic': t.name, 'subject': t.module.subject.name, 'mastery': mastery, 'risk': risk_level})
    return Response(data)


@api_view(['GET'])
def study_plan(request):
    minutes = int(request.query_params.get('minutes', 180))
    days = int(request.query_params.get('days', 5))
    use_ai = request.query_params.get('ai', '1') != '0'
    return Response(build_plan(max(60, min(minutes, 600)), max(4, min(days, 5)), use_ai=use_ai, user=request.user))


@api_view(['GET'])
def prediction(request):
    return Response(performance_prediction(request.query_params.get('subject_id'), user=request.user))


@api_view(['POST'])
def chat_api(request):
    message = str(request.data.get('message', '')).strip()
    history = request.data.get('history', [])
    result = chat(message, history=history if isinstance(history, list) else [], user=request.user)
    item = AIInteraction.objects.create(
        user=request.user,
        question=message,
        answer=result.get('answer', ''),
    )
    return Response({
        **result,
        'id': item.id,
    })


@api_view(['POST'])
def classify_question(request):
    """Map a past-paper question to an existing syllabus topic.

    This is deliberately constrained to topics already stored in StudyOS. When
    OpenAI is configured it performs semantic classification; otherwise a small
    local keyword-overlap fallback keeps the endpoint usable offline.
    """
    text = str(request.data.get('question', '')).strip()
    subject_id = request.data.get('subject_id')
    if not text or not subject_id:
        return Response({'detail': 'question and subject_id are required.'}, status=400)

    subject = Subject.objects.get(id=subject_id)
    assessment = next_assessment()
    candidates = assessment_scope(subject, assessment['name'] if assessment else 'SEE')
    if not candidates:
        return Response({'detail': 'No syllabus topics are available for this subject.'}, status=400)

    candidate_data = [{'id': t.id, 'topic': t.name, 'module': t.module.number, 'module_name': t.module.name} for t in candidates]
    result = None
    ai_used = False

    api_key = os.getenv('OPENAI_API_KEY', '').strip()
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            schema = {
                'type': 'object',
                'additionalProperties': False,
                'properties': {
                    'topic_id': {'type': 'integer'},
                    'confidence': {'type': 'number'},
                    'reason': {'type': 'string'},
                },
                'required': ['topic_id', 'confidence', 'reason'],
            }
            response = client.responses.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-5.6-luna'),
                input=[
                    {'role': 'system', 'content': 'Map the question to exactly one supplied StudyOS topic. Never invent a topic ID. Return low confidence when the evidence is weak.'},
                    {'role': 'user', 'content': json.dumps({'question': text, 'topics': candidate_data})},
                ],
                text={'format': {'type': 'json_schema', 'name': 'question_topic_match', 'strict': True, 'schema': schema}},
            )
            payload = json.loads(response.output_text)
            if payload['topic_id'] in {x['id'] for x in candidate_data}:
                result = payload
                ai_used = True
        except Exception:
            result = None

    if result is None:
        words = {word.lower() for word in text.replace('?', ' ').replace(',', ' ').split() if len(word) > 3}
        scored = []
        for candidate in candidate_data:
            topic_words = {word.lower() for word in candidate['topic'].replace('-', ' ').split() if len(word) > 3}
            overlap = len(words & topic_words)
            scored.append((overlap, candidate))
        scored.sort(key=lambda item: item[0], reverse=True)
        best = scored[0][1]
        result = {'topic_id': best['id'], 'confidence': 0.25 if scored[0][0] == 0 else min(0.85, 0.35 + scored[0][0] * 0.15), 'reason': 'Local keyword fallback.'}

    topic = Topic.objects.get(id=result['topic_id'])
    return Response({
        'topic_id': topic.id,
        'topic': topic.name,
        'module': topic.module.number,
        'confidence': result['confidence'],
        'reason': result['reason'],
        'ai_used': ai_used,
        'created_question_id': None,
    })


@api_view(['POST'])
def target(request):
    target_sgpa = float(request.data.get('target_sgpa', 9.5))
    subjects = list(Subject.objects.all())
    total = sum(s.credits for s in subjects)
    return Response({
        'target_sgpa': target_sgpa,
        'credits': total,
        'message': f'For a {target_sgpa:.1f} SGPA target, StudyOS will prioritize high-credit subjects and high-priority topics. Exact grade requirements depend on your college grading map.',
    })
