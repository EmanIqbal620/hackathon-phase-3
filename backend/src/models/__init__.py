"""
Database models for the Todo App
"""
from .user import User, UserCreate, UserRead, UserBase
from .task import Task, TaskCreate, TaskRead, TaskBase, TaskUpdate
from .conversation import Conversation, Message, ConversationCreate, ConversationRead, MessageCreate, MessageRead
from .accessibility import AccessibilitySettings, AccessibilitySettingsCreate, AccessibilitySettingsRead, AccessibilitySettingsUpdate
from .analytics import AnalyticsData, AnalyticsDataCreate, AnalyticsDataRead, AnalyticsDataUpdate
from .reminder import Reminder, ReminderCreate, ReminderRead, ReminderUpdate, ReminderResponse
from .performance import PerformanceMetrics, PerformanceMetricsCreate, PerformanceMetricsRead, PerformanceMetricsUpdate
from .suggestion import Suggestion, SuggestionCreate, SuggestionRead, SuggestionUpdate, SuggestionResponse
from .micro_feature import MicroFeature, UserMicroFeaturePreference, MicroFeatureCreate, MicroFeatureRead, MicroFeatureUpdate, UserMicroFeaturePreferenceCreate, UserMicroFeaturePreferenceRead, UserMicroFeaturePreferenceUpdate
from .tool_call_log import ToolCallLog
from .user_interaction import UserInteraction, UserInteractionCreate, UserInteractionRead, UserInteractionUpdate, UserInteractionStats
from .ux_enhancement import UXEnhancement, UXEnhancementCreate, UXEnhancementRead, UXEnhancementUpdate
# Import old chat models if needed, but avoid naming conflicts

__all__ = [
    "User",
    "UserCreate",
    "UserRead",
    "UserBase",
    "Task",
    "TaskCreate",
    "TaskRead",
    "TaskBase",
    "TaskUpdate",
    "Conversation",
    "Message",
    "ConversationCreate",
    "ConversationRead",
    "MessageCreate",
    "MessageRead",
    "AccessibilitySettings",
    "AccessibilitySettingsCreate",
    "AccessibilitySettingsRead",
    "AccessibilitySettingsUpdate",
    "AnalyticsData",
    "AnalyticsDataCreate",
    "AnalyticsDataRead",
    "AnalyticsDataUpdate",
    "Reminder",
    "ReminderCreate",
    "ReminderRead",
    "ReminderUpdate",
    "ReminderResponse",
    "PerformanceMetrics",
    "PerformanceMetricsCreate",
    "PerformanceMetricsRead",
    "PerformanceMetricsUpdate",
    "Suggestion",
    "SuggestionCreate",
    "SuggestionRead",
    "SuggestionUpdate",
    "SuggestionResponse",
    "MicroFeature",
    "UserMicroFeaturePreference",
    "MicroFeatureCreate",
    "MicroFeatureRead",
    "MicroFeatureUpdate",
    "UserMicroFeaturePreferenceCreate",
    "UserMicroFeaturePreferenceRead",
    "UserMicroFeaturePreferenceUpdate",
    "ToolCallLog",
    "UserInteraction",
    "UserInteractionCreate",
    "UserInteractionRead",
    "UserInteractionUpdate",
    "UserInteractionStats",
    "UXEnhancement",
    "UXEnhancementCreate",
    "UXEnhancementRead",
    "UXEnhancementUpdate",

]