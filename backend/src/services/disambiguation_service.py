"""
Disambiguation Service
This module handles disambiguation of complex or ambiguous user requests in the AI chatbot.
"""
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel
import logging
import re
from ..models.task import Task
from sqlmodel import Session, select
from ..database import sync_engine


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DisambiguationRequest(BaseModel):
    """Request model for disambiguation service"""
    user_id: str
    user_input: str
    context: Optional[Dict] = None
    existing_entities: Optional[List[Dict]] = None


class DisambiguationResponse(BaseModel):
    """Response model for disambiguation service"""
    is_ambiguous: bool
    clarifying_questions: List[str]
    resolved_entities: Optional[Dict] = None
    confidence: float


class DisambiguationService:
    """Service class for handling ambiguous user requests."""

    @staticmethod
    def analyze_request(request: DisambiguationRequest) -> DisambiguationResponse:
        """
        Analyze a user request to identify ambiguity and provide clarifying questions.

        Args:
            request: DisambiguationRequest with user input and context

        Returns:
            DisambiguationResponse with analysis results
        """
        user_input = request.user_input.lower().strip()
        user_id = request.user_id

        # Identify potential ambiguities
        ambiguities = DisambiguationService._identify_ambiguities(user_input, user_id)

        if not ambiguities:
            # No ambiguities found, try to resolve entities directly
            resolved_entities = DisambiguationService._resolve_entities(user_input, user_id, request.context)
            return DisambiguationResponse(
                is_ambiguous=False,
                clarifying_questions=[],
                resolved_entities=resolved_entities,
                confidence=0.9 if resolved_entities else 0.3
            )

        # Generate clarifying questions based on identified ambiguities
        clarifying_questions = []
        for ambiguity in ambiguities:
            question = DisambiguationService._generate_clarifying_question(ambiguity, user_input)
            clarifying_questions.append(question)

        return DisambiguationResponse(
            is_ambiguous=True,
            clarifying_questions=clarifying_questions,
            resolved_entities=None,
            confidence=0.0  # Low confidence when ambiguous
        )

    @staticmethod
    def _identify_ambiguities(user_input: str, user_id: str) -> List[Dict]:
        """
        Identify potential ambiguities in user input.

        Args:
            user_input: Raw user input string
            user_id: ID of the user making the request

        Returns:
            List of ambiguity dictionaries
        """
        ambiguities = []

        # Check for ambiguous pronouns (this, that, it)
        pronoun_pattern = r'\b(this|that|it|these|those)\b'
        pronoun_matches = re.findall(pronoun_pattern, user_input, re.IGNORECASE)
        if pronoun_matches:
            ambiguities.append({
                "type": "pronoun_reference",
                "matches": pronoun_matches,
                "message": f"Unclear reference: '{', '.join(set(pronoun_matches))}'"
            })

        # Check for ambiguous task references (e.g., "the meeting task" when multiple meeting tasks exist)
        with Session(sync_engine) as session:
            all_tasks = session.exec(
                select(Task).where(Task.user_id == user_id)
            ).all()

            # Look for common task descriptors that might be ambiguous
            ambiguous_descriptors = [
                "the meeting", "the task", "the project", "the appointment",
                "that one", "this one", "the thing", "the item"
            ]

            for descriptor in ambiguous_descriptors:
                if descriptor in user_input:
                    # Find tasks that might match this descriptor
                    matching_tasks = []
                    for task in all_tasks:
                        if descriptor.replace("the ", "") in task.title.lower() or \
                           descriptor.replace("the ", "") in (task.description or "").lower():
                            matching_tasks.append(task.title)

                    if len(matching_tasks) > 1:
                        ambiguities.append({
                            "type": "task_reference",
                            "descriptor": descriptor,
                            "matching_tasks": matching_tasks,
                            "message": f"Ambiguous reference to '{descriptor}' - multiple tasks match: {', '.join(matching_tasks[:3])}"
                        })

        # Check for time ambiguity (e.g., "tomorrow" vs specific date)
        time_indicators = ["today", "tomorrow", "yesterday", "this week", "next week", "this month"]
        time_matches = [indicator for indicator in time_indicators if indicator in user_input]
        if time_matches:
            ambiguities.append({
                "type": "time_reference",
                "matches": time_matches,
                "message": f"Ambiguous time reference: {', '.join(time_matches)} - specific dates would be clearer"
            })

        # Check for priority ambiguity (e.g., "important task" without specification)
        priority_indicators = ["important", "urgent", "critical", "high priority", "top priority"]
        priority_matches = [indicator for indicator in priority_indicators if indicator in user_input]
        if priority_matches:
            # Check if user has many high-priority tasks
            with Session(sync_engine) as session:
                high_priority_tasks = session.exec(
                    select(Task).where(
                        Task.user_id == user_id,
                        Task.priority == "high"
                    )
                ).all()

                if len(high_priority_tasks) > 3:
                    ambiguities.append({
                        "type": "priority_specification",
                        "matches": priority_matches,
                        "message": f"Ambiguous priority reference: You have {len(high_priority_tasks)} high-priority tasks. Which specific task do you mean?"
                    })

        # Check for action ambiguity (unclear what action to take)
        action_ambiguities = DisambiguationService._identify_action_ambiguities(user_input)
        if action_ambiguities:
            ambiguities.extend(action_ambiguities)

        return ambiguities

    @staticmethod
    def _identify_action_ambiguities(user_input: str) -> List[Dict]:
        """
        Identify ambiguities related to unclear actions.

        Args:
            user_input: Raw user input string

        Returns:
            List of action ambiguity dictionaries
        """
        ambiguities = []

        # Look for commands that could mean different things
        ambiguous_phrases = [
            ("remind me", "about what and when?"),
            ("help me", "with what specifically?"),
            ("do this", "what specifically?"),
            ("handle that", "which task?"),
            ("finish it", "which task?"),
            ("update that", "what needs updating?")
        ]

        for phrase, clarification in ambiguous_phrases:
            if phrase in user_input:
                ambiguities.append({
                    "type": "action_specification",
                    "phrase": phrase,
                    "message": f"Ambiguous action: '{phrase}' - {clarification}"
                })

        # Check for multiple possible interpretations of commands
        if any(word in user_input for word in ["add", "create", "make"]) and \
           any(word in user_input for word in ["update", "change", "modify"]):
            ambiguities.append({
                "type": "action_conflict",
                "message": "Unclear whether to add/create or update/modify"
            })

        return ambiguities

    @staticmethod
    def _generate_clarifying_question(ambiguity: Dict, user_input: str) -> str:
        """
        Generate a clarifying question based on identified ambiguity.

        Args:
            ambiguity: Ambiguity dictionary
            user_input: Original user input

        Returns:
            Clarifying question string
        """
        ambiguity_type = ambiguity["type"]

        if ambiguity_type == "pronoun_reference":
            return "Could you please specify what you're referring to? Which task or item do you mean?"
        elif ambiguity_type == "task_reference":
            matching_tasks = ambiguity["matching_tasks"][:3]  # Limit to first 3
            return f"I found multiple tasks that might match '{ambiguity['descriptor']}'. Did you mean: {', '.join(matching_tasks)}?"
        elif ambiguity_type == "time_reference":
            return "Could you specify a more precise date or time frame?"
        elif ambiguity_type == "priority_specification":
            return f"You have multiple high-priority tasks. Could you specify which one you're referring to?"
        elif ambiguity_type == "action_specification":
            return f"What specifically would you like me to do with '{ambiguity['phrase'].split()[-1]}'?"
        elif ambiguity_type == "action_conflict":
            return "Are you asking me to add/create something or to update/modify something?"
        else:
            return "Could you please provide more details to clarify your request?"

    @staticmethod
    def _resolve_entities(user_input: str, user_id: str, context: Optional[Dict] = None) -> Optional[Dict]:
        """
        Attempt to resolve entities from user input based on context.

        Args:
            user_input: Raw user input string
            user_id: ID of the user making the request
            context: Optional conversation context

        Returns:
            Dictionary with resolved entities or None if ambiguous
        """
        entities = {}

        # Try to extract task references from user input
        with Session(sync_engine) as session:
            all_tasks = session.exec(
                select(Task).where(Task.user_id == user_id)
            ).all()

        # Look for task titles in the input
        task_matches = []
        for task in all_tasks:
            if task.title.lower() in user_input:
                task_matches.append(task)

        if len(task_matches) == 1:
            entities["task"] = {
                "id": task_matches[0].id,
                "title": task_matches[0].title,
                "confidence": 0.9
            }
        elif len(task_matches) > 1:
            # Too ambiguous to resolve
            return None
        # If no exact matches, try fuzzy matching
        else:
            # Look for partial matches
            partial_matches = []
            for task in all_tasks:
                task_words = set(task.title.lower().split())
                input_words = set(user_input.split())

                # Calculate similarity
                common_words = task_words.intersection(input_words)
                similarity = len(common_words) / len(task_words) if task_words else 0

                if similarity > 0.3:  # Threshold for considering a match
                    partial_matches.append((task, similarity))

            if len(partial_matches) == 1:
                task, similarity = partial_matches[0]
                entities["task"] = {
                    "id": task.id,
                    "title": task.title,
                    "confidence": min(0.8, similarity * 2)  # Adjust confidence based on similarity
                }
            elif len(partial_matches) > 1:
                # Still ambiguous
                return None

        # Extract priority if mentioned
        priority_keywords = {
            "high": ["high", "urgent", "important", "critical", "top", "priority"],
            "medium": ["medium", "moderate", "normal", "regular"],
            "low": ["low", "low-priority", "later", "whenever"]
        }

        for priority, keywords in priority_keywords.items():
            if any(keyword in user_input for keyword in keywords):
                entities["priority"] = {
                    "value": priority,
                    "confidence": 0.7
                }
                break

        # Extract dates if mentioned
        date_patterns = [
            r'today',
            r'tomorrow',
            r'next\s+(week|month|year)',
            r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            r'(\d{1,2}[/-]\d{1,2}([/-]\d{2,4})?)'  # MM/DD or MM/DD/YYYY format
        ]

        for pattern in date_patterns:
            matches = re.findall(pattern, user_input, re.IGNORECASE)
            if matches:
                entities["due_date"] = {
                    "value": matches[0] if isinstance(matches[0], str) else matches[0][0],
                    "confidence": 0.6
                }
                break

        # Extract action if clearly specified
        action_keywords = {
            "create": ["add", "create", "make", "new"],
            "update": ["update", "change", "modify", "edit"],
            "complete": ["complete", "done", "finish", "mark as done"],
            "delete": ["delete", "remove", "cancel"]
        }

        for action, keywords in action_keywords.items():
            if any(keyword in user_input for keyword in keywords):
                entities["action"] = {
                    "value": action,
                    "confidence": 0.8
                }
                break

        return entities if entities else None

    @staticmethod
    def resolve_with_user_feedback(user_input: str, clarifying_answer: str, original_context: Dict) -> Dict:
        """
        Resolve entities based on user's answer to a clarifying question.

        Args:
            user_input: Original ambiguous input
            clarifying_answer: User's response to clarifying question
            original_context: Original context before clarification

        Returns:
            Dictionary with resolved entities
        """
        resolved_entities = {}

        # If the user specified a particular task in their answer
        if "task" in original_context.get("ambiguities", [{}])[0].get("type", ""):
            # Parse the user's answer to identify which task they meant
            with Session(sync_engine) as session:
                all_tasks = session.exec(
                    select(Task).where(Task.user_id == original_context["user_id"])
                ).all()

            # Look for task titles in the clarifying answer
            for task in all_tasks:
                if task.title.lower() in clarifying_answer.lower():
                    resolved_entities["task"] = {
                        "id": task.id,
                        "title": task.title,
                        "confidence": 0.95
                    }
                    break

            # If no exact match, look for partial matches
            if "task" not in resolved_entities:
                for task in all_tasks:
                    if any(word in clarifying_answer.lower() for word in task.title.lower().split()):
                        resolved_entities["task"] = {
                            "id": task.id,
                            "title": task.title,
                            "confidence": 0.8
                        }
                        break

        # Process other elements based on the clarified input
        resolved_entities.update(
            DisambiguationService._resolve_entities(clarifying_answer, original_context["user_id"], original_context)
        )

        return resolved_entities

    @staticmethod
    def _extract_numerical_references(user_input: str, available_options: List) -> Optional[int]:
        """
        Extract numerical references from user input (e.g., "the first one", "option 2").

        Args:
            user_input: User's input string
            available_options: List of available options to reference

        Returns:
            Index of selected option or None if not found
        """
        # Look for ordinal numbers
        ordinal_patterns = [
            (r'first|1st', 0),
            (r'second|2nd', 1),
            (r'third|3rd', 2),
            (r'(\d+)(th|rd|nd|st)', lambda m: int(m.group(1)) - 1)
        ]

        for pattern, index in ordinal_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                if callable(index):
                    idx = index(match)
                else:
                    idx = index

                if 0 <= idx < len(available_options):
                    return idx

        # Look for direct numbers
        number_match = re.search(r'\b(\d+)\b', user_input)
        if number_match:
            num = int(number_match.group(1)) - 1  # Convert to 0-based index
            if 0 <= num < len(available_options):
                return num

        return None