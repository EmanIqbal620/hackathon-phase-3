"""
Advanced NLP Processing Module
This module handles complex natural language understanding for the AI chatbot.
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import logging
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from ..models.task import Task
from sqlmodel import Session, select
from ..database import sync_engine
import spacy
from transformers import pipeline


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntentType(Enum):
    """Enumeration of possible user intents."""
    ADD_TASK = "add_task"
    COMPLETE_TASK = "complete_task"
    UPDATE_TASK = "update_task"
    LIST_TASKS = "list_tasks"
    DELETE_TASK = "delete_task"
    GET_ANALYTICS = "get_analytics"
    SET_REMINDER = "set_reminder"
    GET_SUGGESTIONS = "get_suggestions"
    UNCLEAR = "unclear"


@dataclass
class ParsedIntent:
    """Data class for storing parsed intent information."""
    intent_type: IntentType
    entities: Dict[str, str]
    confidence: float
    original_input: str


class AdvancedNLPProcessor:
    """Advanced NLP processor for understanding complex user requests."""

    def __init__(self):
        """Initialize the NLP processor with required models."""
        try:
            # Load spaCy model for linguistic analysis
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy English model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None

        # Initialize transformer pipeline for text classification if available
        try:
            self.classifier = pipeline("text-classification",
                                      model="facebook/bart-large-mnli",
                                      return_all_scores=True)
        except Exception as e:
            logger.warning(f"Transformer model not available: {e}")
            self.classifier = None

        # Define intent patterns
        self.intent_patterns = {
            IntentType.ADD_TASK: [
                r"add.*task",
                r"create.*task",
                r"make.*task",
                r"new.*task",
                r"remind.*to",
                r"need.*to",
                r"have.*to",
                r"should.*",
                r"plan.*to"
            ],
            IntentType.COMPLETE_TASK: [
                r"complete.*task",
                r"finish.*task",
                r"done.*task",
                r"mark.*done",
                r"check.*off",
                r"finished.*task"
            ],
            IntentType.LIST_TASKS: [
                r"show.*tasks?",
                r"list.*tasks?",
                r"what.*tasks?",
                r"view.*tasks?",
                r"my.*tasks?",
                r"pending.*tasks?",
                r"completed.*tasks?"
            ],
            IntentType.GET_ANALYTICS: [
                r"how.*am.*doing",
                r"analytics",
                r"statistics",
                r"metrics",
                r"performance",
                r"productivity",
                r"progress",
                r"trends"
            ],
            IntentType.SET_REMINDER: [
                r"remind.*me",
                r"set.*reminder",
                r"notify.*me",
                r"alert.*me"
            ],
            IntentType.GET_SUGGESTIONS: [
                r"suggest.*task",
                r"recommend.*task",
                r"what.*should.*do",
                r"ideas.*for",
                r"recommendations"
            ]
        }

    def process_input(self, user_input: str, user_id: str) -> ParsedIntent:
        """
        Process user input and extract intent and entities.

        Args:
            user_input: Raw user input string
            user_id: ID of the user making the request

        Returns:
            ParsedIntent object with intent and extracted entities
        """
        logger.info(f"Processing NLP input: '{user_input}' for user {user_id}")

        # Preprocess input
        processed_input = self._preprocess_input(user_input)

        # Identify intent
        intent_type, confidence = self._identify_intent(processed_input)

        # Extract entities
        entities = self._extract_entities(processed_input, user_id)

        # Enhance entities with context
        enhanced_entities = self._enhance_entities_with_context(entities, user_input, user_id)

        parsed_intent = ParsedIntent(
            intent_type=intent_type,
            entities=enhanced_entities,
            confidence=confidence,
            original_input=user_input
        )

        logger.info(f"Parsed intent: {parsed_intent.intent_type}, confidence: {parsed_intent.confidence}")
        return parsed_intent

    def _preprocess_input(self, user_input: str) -> str:
        """
        Preprocess user input for NLP analysis.

        Args:
            user_input: Raw user input string

        Returns:
            Preprocessed input string
        """
        # Convert to lowercase and normalize whitespace
        processed = re.sub(r'\s+', ' ', user_input.strip().lower())

        # Expand common contractions
        contractions = {
            "i'm": "i am",
            "you're": "you are",
            "it's": "it is",
            "we're": "we are",
            "they're": "they are",
            "i've": "i have",
            "you've": "you have",
            "we've": "we have",
            "they've": "they have",
            "i'll": "i will",
            "you'll": "you will",
            "he'll": "he will",
            "she'll": "she will",
            "we'll": "we will",
            "they'll": "they will",
            "isn't": "is not",
            "aren't": "are not",
            "wasn't": "was not",
            "weren't": "were not",
            "haven't": "have not",
            "hasn't": "has not",
            "hadn't": "had not",
            "won't": "will not",
            "wouldn't": "would not",
            "don't": "do not",
            "doesn't": "does not",
            "didn't": "did not",
            "can't": "cannot",
            "couldn't": "could not",
            "shouldn't": "should not"
        }

        for contraction, expansion in contractions.items():
            processed = processed.replace(contraction, expansion)

        return processed

    def _identify_intent(self, processed_input: str) -> Tuple[IntentType, float]:
        """
        Identify the intent of the user input.

        Args:
            processed_input: Preprocessed user input string

        Returns:
            Tuple of (intent_type, confidence)
        """
        # Check for direct pattern matches first
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, processed_input):
                    # Calculate confidence based on pattern match strength
                    confidence = 0.7 + (0.2 * (len(pattern) / 100))  # Simple confidence calculation
                    return intent_type, min(confidence, 0.95)

        # If no direct pattern matches, try ML-based classification if available
        if self.classifier:
            try:
                # Define candidate labels for classification
                candidate_labels = [
                    "add task", "complete task", "list tasks", "get analytics",
                    "set reminder", "get suggestions", "update task", "delete task"
                ]

                # Classify the input
                results = self.classifier(processed_input, candidate_labels=candidate_labels)

                # Find the best match
                best_result = max(results[0], key=lambda x: x['score'])

                # Map to our intent types
                intent_mapping = {
                    "add task": IntentType.ADD_TASK,
                    "complete task": IntentType.COMPLETE_TASK,
                    "list tasks": IntentType.LIST_TASKS,
                    "get analytics": IntentType.GET_ANALYTICS,
                    "set reminder": IntentType.SET_REMINDER,
                    "get suggestions": IntentType.GET_SUGGESTIONS,
                    "update task": IntentType.UPDATE_TASK,
                    "delete task": IntentType.DELETE_TASK
                }

                intent_type = intent_mapping.get(best_result['label'], IntentType.UNCLEAR)
                confidence = best_result['score']

                return intent_type, confidence
            except Exception as e:
                logger.warning(f"ML classification failed: {e}")

        # If all else fails, return unclear intent
        return IntentType.UNCLEAR, 0.1

    def _extract_entities(self, processed_input: str, user_id: str) -> Dict[str, str]:
        """
        Extract entities from the processed input.

        Args:
            processed_input: Preprocessed user input string
            user_id: ID of the user making the request

        Returns:
            Dictionary of extracted entities
        """
        entities = {}

        # Extract potential task title (look for content after intent-indicating words)
        title_patterns = [
            r"add.*?to.*?([^.!?]+)",
            r"create.*?([^.!?]+)",
            r"need.*?to.*?([^.!?]+)",
            r"have.*?to.*?([^.!?]+)",
            r"should.*?([^.!?]+)",
            r"plan.*?to.*?([^.!?]+)",
            r"remind.*?to.*?([^.!?]+)"
        ]

        for pattern in title_patterns:
            match = re.search(pattern, processed_input)
            if match:
                title = match.group(1).strip()
                # Clean up the title
                title = re.sub(r'(please|kindly|would\s+you)', '', title).strip()
                if title:
                    entities['task_title'] = title
                break

        # Extract priority indicators
        priority_indicators = {
            'high': [r'urgent', r'important', r'critical', r'high', r'asap', r'as\s+soon\s+as\s+possible'],
            'medium': [r'medium', r'normal', r'regular'],
            'low': [r'low', r'when.*?possible', r'whenever', r'eventually']
        }

        for priority, indicators in priority_indicators.items():
            for indicator in indicators:
                if re.search(indicator, processed_input):
                    entities['priority'] = priority
                    break

        # Extract date/time indicators
        date_patterns = [
            r'today',
            r'tomorrow',
            r'next\s+(week|month|year)',
            r'in\s+(\d+)\s+(day|hour|week|month)',
            r'on\s+([a-zA-Z]+,\s+\w+\s+\d+)',
            r'by\s+([a-zA-Z]+,\s+\w+\s+\d+)',
            r'before\s+([a-zA-Z]+,\s+\w+\s+\d+)'
        ]

        for pattern in date_patterns:
            match = re.search(pattern, processed_input)
            if match:
                date_str = match.group(0)
                entities['due_date'] = self._parse_date(date_str)
                break

        # Extract task ID if mentioned
        id_patterns = [
            r'task\s+(\w+)',
            r'id\s*(\w+)',
            r'number\s*(\w+)'
        ]

        for pattern in id_patterns:
            match = re.search(pattern, processed_input)
            if match:
                entities['task_id'] = match.group(1)
                break

        # Extract category if mentioned
        category_indicators = [
            (r'work|job|office|meeting|project|presentation|report', 'work'),
            (r'home|house|chores|clean|laundry|cooking|family|personal', 'personal'),
            (r'health|doctor|exercise|medication|appointment|medical', 'health'),
            (r'shopping|buy|purchase|store|grocery|market', 'shopping'),
            (r'learning|study|read|book|course|education|school', 'education')
        ]

        for pattern, category in category_indicators:
            if re.search(pattern, processed_input):
                entities['category'] = category
                break

        return entities

    def _parse_date(self, date_str: str) -> Optional[str]:
        """
        Parse date string into ISO format.

        Args:
            date_str: Date string to parse

        Returns:
            ISO formatted date string or None if parsing fails
        """
        try:
            # Handle relative dates
            if 'today' in date_str:
                return datetime.now().date().isoformat()
            elif 'tomorrow' in date_str:
                return (datetime.now() + timedelta(days=1)).date().isoformat()
            elif 'next week' in date_str:
                return (datetime.now() + timedelta(weeks=1)).date().isoformat()
            elif 'next month' in date_str:
                return (datetime.now() + timedelta(days=30)).date().isoformat()
            elif 'next year' in date_str:
                return (datetime.now() + timedelta(days=365)).date().isoformat()

            # Handle "in X days/hours" patterns
            time_pattern = r'in\s+(\d+)\s+(day|hour|week|month)s?'
            match = re.search(time_pattern, date_str)
            if match:
                amount = int(match.group(1))
                unit = match.group(2)

                if unit == 'day':
                    return (datetime.now() + timedelta(days=amount)).date().isoformat()
                elif unit == 'hour':
                    return (datetime.now() + timedelta(hours=amount)).date().isoformat()
                elif unit == 'week':
                    return (datetime.now() + timedelta(weeks=amount)).date().isoformat()
                elif unit == 'month':
                    return (datetime.now() + timedelta(days=amount*30)).date().isoformat()

            # Try to parse as specific date
            parsed_date = date_parser.parse(date_str, fuzzy=True)
            return parsed_date.date().isoformat()
        except Exception as e:
            logger.warning(f"Could not parse date string '{date_str}': {e}")
            return None

    def _enhance_entities_with_context(self, entities: Dict, original_input: str, user_id: str) -> Dict:
        """
        Enhance extracted entities with contextual information.

        Args:
            entities: Dictionary of initially extracted entities
            original_input: Original user input string
            user_id: ID of the user making the request

        Returns:
            Enhanced entities dictionary
        """
        enhanced_entities = entities.copy()

        # Enhance with user-specific context
        if 'task_title' in enhanced_entities:
            # Look for similar tasks in user's history
            similar_tasks = self._find_similar_tasks(user_id, enhanced_entities['task_title'])
            if similar_tasks:
                # Add context about similar tasks
                enhanced_entities['similar_task_count'] = len(similar_tasks)
                enhanced_entities['most_similar_task'] = similar_tasks[0]['title']

        # Enhance due date with time context
        if 'due_date' in enhanced_entities:
            due_date = datetime.fromisoformat(enhanced_entities['due_date'])
            days_diff = (due_date.date() - datetime.now().date()).days

            if days_diff < 0:
                enhanced_entities['time_frame'] = 'past'
            elif days_diff == 0:
                enhanced_entities['time_frame'] = 'today'
            elif days_diff == 1:
                enhanced_entities['time_frame'] = 'tomorrow'
            elif days_diff <= 7:
                enhanced_entities['time_frame'] = 'week'
            elif days_diff <= 30:
                enhanced_entities['time_frame'] = 'month'
            else:
                enhanced_entities['time_frame'] = 'future'

        # Add context based on input structure
        if self.nlp:
            try:
                doc = self.nlp(original_input)

                # Extract named entities
                named_entities = []
                for ent in doc.ents:
                    named_entities.append({
                        'text': ent.text,
                        'label': ent.label_,
                        'start': ent.start_char,
                        'end': ent.end_char
                    })

                if named_entities:
                    enhanced_entities['named_entities'] = named_entities

                # Extract dependencies for better understanding
                dependencies = []
                for token in doc:
                    if token.dep_ in ['nsubj', 'dobj', 'pobj']:  # Subject, direct object, prepositional object
                        dependencies.append({
                            'text': token.text,
                            'dependency': token.dep_,
                            'head': token.head.text
                        })

                if dependencies:
                    enhanced_entities['syntactic_dependencies'] = dependencies
            except Exception as e:
                logger.warning(f"spaCy processing failed: {e}")

        return enhanced_entities

    def _find_similar_tasks(self, user_id: str, task_title: str) -> List[Dict]:
        """
        Find similar tasks in user's history.

        Args:
            user_id: ID of the user to search for
            task_title: Title to match against

        Returns:
            List of similar tasks with similarity scores
        """
        with Session(sync_engine) as session:
            # Get user's tasks
            user_tasks = session.exec(
                select(Task).where(Task.user_id == user_id)
            ).all()

            similar_tasks = []
            task_title_lower = task_title.lower()

            for task in user_tasks:
                task_title_comparison = task.title.lower()

                # Calculate similarity based on common words
                task_words = set(task_title_comparison.split())
                input_words = set(task_title_lower.split())
                common_words = task_words.intersection(input_words)

                if common_words:
                    similarity_score = len(common_words) / max(len(task_words), len(input_words))

                    if similarity_score > 0.3:  # Threshold for considering similarity
                        similar_tasks.append({
                            'id': task.id,
                            'title': task.title,
                            'similarity_score': similarity_score,
                            'created_at': task.created_at.isoformat() if task.created_at else None,
                            'completed': task.is_completed
                        })

            # Sort by similarity score descending
            similar_tasks.sort(key=lambda x: x['similarity_score'], reverse=True)

            return similar_tasks[:5]  # Return top 5 similar tasks

    def disambiguate_request(self, parsed_intent: ParsedIntent, user_id: str) -> Tuple[ParsedIntent, List[str]]:
        """
        Disambiguate potentially ambiguous user requests.

        Args:
            parsed_intent: Parsed intent that may need disambiguation
            user_id: ID of the user making the request

        Returns:
            Tuple of (disambiguated_intent, list_of_clarifying_questions)
        """
        clarifying_questions = []

        # Check for ambiguous task references
        if 'task_title' in parsed_intent.entities:
            with Session(sync_engine) as session:
                # Find all tasks that might match the title
                similar_tasks = session.exec(
                    select(Task).where(
                        Task.user_id == user_id,
                        Task.title.ilike(f"%{parsed_intent.entities['task_title']}%")
                    )
                ).all()

                if len(similar_tasks) > 1:
                    # Multiple tasks match, need disambiguation
                    task_list = [f"'{task.title}' (ID: {task.id})" for task in similar_tasks[:5]]
                    clarifying_questions.append(
                        f"I found multiple tasks matching '{parsed_intent.entities['task_title']}': {', '.join(task_list)}. "
                        f"Could you specify which one you mean?"
                    )

        # Check for ambiguous pronouns in context
        if any(pronoun in parsed_intent.original_input.lower() for pronoun in ['it', 'that', 'this']):
            # Check if there's clear antecedent in recent context
            if not any(entity in parsed_intent.entities for entity in ['task_id', 'task_title']):
                clarifying_questions.append(
                    f"You mentioned 'it', 'that', or 'this' but I'm not sure what you're referring to. "
                    f"Could you please specify which task or item you mean?"
                )

        # Check for ambiguous time references
        if 'due_date' not in parsed_intent.entities:
            time_indicators = ['today', 'tomorrow', 'this week', 'next week', 'soon', 'later']
            if any(indicator in parsed_intent.original_input.lower() for indicator in time_indicators):
                if parsed_intent.intent_type in [IntentType.ADD_TASK, IntentType.SET_REMINDER]:
                    clarifying_questions.append(
                        f"When exactly would you like this scheduled? "
                        f"I heard a time reference but need a specific date."
                    )

        # If we have clarifying questions, mark intent as uncertain
        if clarifying_questions and parsed_intent.confidence > 0.5:
            # Lower confidence since there are ambiguities
            parsed_intent.confidence = 0.5

        return parsed_intent, clarifying_questions

    def generate_task_suggestions(self, user_id: str, context: Optional[Dict] = None) -> List[Dict]:
        """
        Generate intelligent task suggestions based on user patterns and context.

        Args:
            user_id: ID of the user to generate suggestions for
            context: Optional context to influence suggestions

        Returns:
            List of suggested tasks with confidence scores
        """
        suggestions = []

        with Session(sync_engine) as session:
            # Get user's tasks
            all_tasks = session.exec(
                select(Task).where(Task.user_id == user_id)
            ).all()

        # Analyze patterns in user's tasks
        if all_tasks:
            # Find recurring patterns
            title_counts = {}
            for task in all_tasks:
                title_lower = task.title.lower()
                title_counts[title_lower] = title_counts.get(title_lower, 0) + 1

            # Suggest recurring tasks that haven't been done recently
            for title, count in title_counts.items():
                if count >= 2:  # At least done twice before
                    # Check if this task has been done recently
                    recent_occurrences = [
                        task for task in all_tasks
                        if task.title.lower() == title and
                        task.created_at and
                        (datetime.now() - task.created_at).days < 7
                    ]

                    if not recent_occurrences:
                        # This is a recurring pattern that hasn't happened recently
                        suggestions.append({
                            "title": title,
                            "description": f"Based on your pattern of doing this task regularly",
                            "confidence": min(0.95, 0.3 + (count * 0.1)),
                            "suggestion_type": "pattern_based",
                            "reasoning": f"You typically do '{title}' tasks regularly (appeared {count} times in your history)"
                        })

            # Suggest tasks based on priority patterns
            incomplete_high_priority = [
                task for task in all_tasks
                if not task.is_completed and task.priority == "high"
            ]

            for task in incomplete_high_priority[:3]:  # Suggest up to 3 high priority tasks
                suggestions.append({
                    "title": f"Complete: {task.title}",
                    "description": f"This is a high-priority task that needs attention",
                    "confidence": 0.85,
                    "suggestion_type": "priority_based",
                    "reasoning": f"'{task.title}' is marked as high priority and is still pending"
                })

            # Suggest tasks based on deadlines
            now = datetime.now()
            upcoming_deadlines = [
                task for task in all_tasks
                if not task.is_completed and
                task.due_date and
                (task.due_date - now).days <= 3 and  # Due in next 3 days
                (task.due_date - now).days >= 0  # Not already past due
            ]

            for task in upcoming_deadlines:
                days_until = (task.due_date - now).days
                suggestions.append({
                    "title": f"Due Soon: {task.title}",
                    "description": f"This task is due in {days_until} day{'s' if days_until != 1 else ''}",
                    "confidence": 0.8 if days_until == 0 else 0.7,  # Higher confidence if due today
                    "suggestion_type": "deadline_based",
                    "reasoning": f"'{task.title}' is due on {task.due_date.strftime('%A, %B %d')}"
                })

        # Add context-based suggestions if provided
        if context:
            # Add suggestions based on time of day, day of week, etc.
            current_hour = datetime.now().hour
            day_of_week = datetime.now().strftime('%A')

            if current_hour < 10 and day_of_week == 'Monday':
                suggestions.append({
                    "title": "Review weekly goals",
                    "description": "Start the week by reviewing your goals and priorities",
                    "confidence": 0.6,
                    "suggestion_type": "contextual",
                    "reasoning": "It's Monday morning, a good time to review weekly goals"
                })

        return suggestions

    def infer_task_attributes(self, user_input: str) -> Dict:
        """
        Infer task attributes (priority, category, etc.) from user input.

        Args:
            user_input: Raw user input string

        Returns:
            Dictionary of inferred task attributes
        """
        attributes = {}

        # Infer priority based on urgency indicators
        high_priority_indicators = [
            r'urgent', r'asap', r'immediately', r'now', r'critical',
            r'important', r'crucial', r'essential', r'vital', r'high priority'
        ]

        medium_priority_indicators = [
            r'medium priority', r'normal', r'regular', r'soon', r'eventually'
        ]

        low_priority_indicators = [
            r'low priority', r'whenever', r'when possible', r'eventually', r'later'
        ]

        user_input_lower = user_input.lower()

        # Check for high priority indicators
        if any(re.search(indicator, user_input_lower) for indicator in high_priority_indicators):
            attributes['priority'] = 'high'
        elif any(re.search(indicator, user_input_lower) for indicator in medium_priority_indicators):
            attributes['priority'] = 'medium'
        elif any(re.search(indicator, user_input_lower) for indicator in low_priority_indicators):
            attributes['priority'] = 'low'
        else:
            # Default priority based on intensity of language
            exclamation_count = user_input.count('!')
            if exclamation_count >= 2:
                attributes['priority'] = 'high'
            else:
                attributes['priority'] = 'medium'

        # Infer category based on keywords
        category_indicators = [
            (r'(work|job|office|meet|project|report|present|email|task|colleague|boss|team|company)', 'work'),
            (r'(home|house|clean|laundry|cook|meal|family|chores|personal)', 'personal'),
            (r'(health|doctor|medical|appointment|medicine|exercise|gym|fitness|wellness)', 'health'),
            (r'(shop|buy|purchase|grocer|store|market|amazon)', 'shopping'),
            (r'(learn|study|read|book|course|education|school|training|skill)', 'education'),
            (r'(social|friend|party|hangout|dinner|lunch|coffee|date)', 'social'),
            (r'(travel|vacation|trip|hotel|flight|destination|booking)', 'travel')
        ]

        for pattern, category in category_indicators:
            if re.search(pattern, user_input_lower):
                attributes['category'] = category
                break

        # Infer estimated duration based on task complexity indicators
        complexity_indicators = {
            'short': [r'quick', r'fast', r'easy', r'simple', r'5 min', r'10 min', r'few minutes'],
            'medium': [r'medium', r'reasonable', r'normal', r'30 min', r'1 hour', r'couple hours'],
            'long': [r'complex', r'involved', r'large', r'few hours', r'full day', r'extensive']
        }

        for duration_level, indicators in complexity_indicators.items():
            if any(re.search(indicator, user_input_lower, re.IGNORECASE) for indicator in indicators):
                attributes['estimated_duration'] = duration_level
                break

        return attributes


# Singleton instance for use throughout the application
nlp_processor = AdvancedNLPProcessor()