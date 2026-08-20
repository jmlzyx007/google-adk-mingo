"""Module 22 - state scopes and memory: personal learning tutor.

One state dict, four scopes decided by key prefix:

    user:foo   -> persists across ALL sessions of this user (per app)
    (no prefix) -> this session only
    temp:foo   -> this invocation only, never persisted
    app:foo    -> shared by every user of the app (global config)

`search_past_lessons` simulates memory retrieval from user: state;
production would use a semantic memory service (VertexAiMemoryBankService).
"""

from typing import Any, Dict

from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext


def set_user_preferences(
    language: str, difficulty_level: str, tool_context: ToolContext
) -> Dict[str, Any]:
    """Set user learning preferences (stored persistently across sessions).

    Args:
        language: Preferred language code, e.g. "en" or "fr".
        difficulty_level: One of "beginner", "intermediate", "advanced".
    """
    tool_context.state["user:language"] = language
    tool_context.state["user:difficulty_level"] = difficulty_level
    return {
        "status": "success",
        "message": f"Preferences saved: {language}, {difficulty_level} level",
    }


def record_topic_completion(
    topic: str, quiz_score: int, tool_context: ToolContext
) -> Dict[str, Any]:
    """Record a completed topic and its quiz score (persistent).

    Args:
        topic: The topic that was completed.
        quiz_score: Score out of 100.
    """
    topics = list(tool_context.state.get("user:topics_covered", []))
    scores = dict(tool_context.state.get("user:quiz_scores", {}))

    if topic not in topics:
        topics.append(topic)
    scores[topic] = quiz_score
    tool_context.state["user:topics_covered"] = topics
    tool_context.state["user:quiz_scores"] = scores

    return {
        "status": "success",
        "topics_count": len(topics),
        "message": f"Recorded: {topic} with score {quiz_score}/100",
    }


def get_user_progress(tool_context: ToolContext) -> Dict[str, Any]:
    """Retrieve the user's persistent learning progress."""
    language = tool_context.state.get("user:language", "en")
    difficulty = tool_context.state.get("user:difficulty_level", "beginner")
    topics = tool_context.state.get("user:topics_covered", [])
    scores = tool_context.state.get("user:quiz_scores", {})

    avg_score = sum(scores.values()) / len(scores) if scores else 0

    return {
        "status": "success",
        "language": language,
        "difficulty_level": difficulty,
        "topics_completed": len(topics),
        "topics": topics,
        "average_quiz_score": round(avg_score, 1),
        "all_scores": scores,
    }


def start_learning_session(topic: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Begin a learning session on a topic (session-scoped state).

    Args:
        topic: The topic to study in this session.
    """
    tool_context.state["current_topic"] = topic

    difficulty = tool_context.state.get("user:difficulty_level", "beginner")

    return {
        "status": "success",
        "topic": topic,
        "difficulty_level": difficulty,
        "message": f"Started learning session: {topic} at {difficulty} level",
    }


def calculate_quiz_grade(
    correct_answers: int, total_questions: int, tool_context: ToolContext
) -> Dict[str, Any]:
    """Calculate a quiz grade (intermediates in temp: state, discarded after the turn).

    Args:
        correct_answers: Number of correct answers.
        total_questions: Total number of questions.
    """
    percentage = (correct_answers / total_questions) * 100
    tool_context.state["temp:raw_score"] = correct_answers
    tool_context.state["temp:quiz_percentage"] = percentage

    if percentage >= 90:
        grade = "A"
    elif percentage >= 80:
        grade = "B"
    elif percentage >= 70:
        grade = "C"
    elif percentage >= 60:
        grade = "D"
    else:
        grade = "F"

    return {
        "status": "success",
        "score": f"{correct_answers}/{total_questions}",
        "percentage": round(percentage, 1),
        "grade": grade,
        "message": f"Quiz grade: {grade} ({percentage:.1f}%)",
    }


def search_past_lessons(query: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Search the user's past learning sessions for a topic.

    Args:
        query: Topic keyword to look for in past lessons.
    """
    topics = tool_context.state.get("user:topics_covered", [])
    relevant = [t for t in topics if query.lower() in t.lower()]

    if relevant:
        return {
            "status": "success",
            "found": True,
            "relevant_topics": relevant,
            "message": f'Found {len(relevant)} past sessions related to "{query}"',
        }
    return {
        "status": "success",
        "found": False,
        "message": f'No past sessions found for "{query}"',
    }


root_agent = Agent(
    name="personal_tutor",
    model="gemini-3.6-flash",
    description="Personal learning tutor tracking progress and preferences",
    instruction="""
    You are a personalized learning tutor with memory of user progress
    (Course Version {app:course_version?}).

    CAPABILITIES:
    - Set and remember user preferences (language, difficulty level)
    - Track completed topics and quiz scores across sessions
    - Start new learning sessions on specific topics
    - Calculate quiz grades and store results
    - Search past learning sessions for context
    - Adapt teaching based on the user's level and history

    WORKFLOW:
    1. If new user, ask about preferences (language, difficulty).
    2. For learning requests, start a session and teach the topic.
    3. After teaching, record completion with quiz score.
    4. When asked, search past lessons to provide context.

    Always be encouraging and adapt to the user's learning pace!
    """,
    tools=[
        set_user_preferences,
        record_topic_completion,
        get_user_progress,
        start_learning_session,
        calculate_quiz_grade,
        search_past_lessons,
    ],
    output_key="last_tutor_response",
)
