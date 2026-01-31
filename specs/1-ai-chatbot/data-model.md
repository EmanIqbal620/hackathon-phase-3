# Data Model: AI-Powered Todo Chatbot

**Created**: 2026-01-23
**Feature**: 1-ai-chatbot
**Status**: Complete

---

## Overview

This document defines the database schema extensions required for the AI-Powered Todo Chatbot feature. The design extends the existing Phase II database schema while maintaining user data isolation and security requirements.

## Entity Relationships

```
[Users] 1 ---- * [Conversations] 1 ---- * [Messages]
                    |
                    *---- * [Tasks] (via user_id)
```

## Entity Definitions

### Conversation Entity

**Description**: Represents a logical conversation thread between a user and the AI assistant

**Fields**:
- `id` (UUID, Primary Key)
  - Unique identifier for the conversation
  - Auto-generated
- `user_id` (UUID, Foreign Key)
  - Links to the user who owns this conversation
  - References `users.id` from Phase II schema
  - Required
- `created_at` (TIMESTAMP WITH TIME ZONE)
  - Timestamp when conversation was initiated
  - Auto-populated
- `updated_at` (TIMESTAMP WITH TIME ZONE)
  - Timestamp of last activity in conversation
  - Auto-updated on changes

**Constraints**:
- Foreign key constraint on `user_id` referencing `users.id`
- Index on `user_id` for efficient querying
- Index on `created_at` for chronological ordering

**Validation Rules**:
- `user_id` must reference an existing user
- Cannot create conversation for non-existent user

### Message Entity

**Description**: Represents individual messages within a conversation

**Fields**:
- `id` (UUID, Primary Key)
  - Unique identifier for the message
  - Auto-generated
- `conversation_id` (UUID, Foreign Key)
  - Links to the conversation this message belongs to
  - References `conversations.id`
  - Required
- `user_id` (UUID, Foreign Key)
  - Links to the user who sent this message
  - References `users.id`
  - Required
- `role` (ENUM: 'user' | 'assistant')
  - Indicates whether message was sent by user or AI assistant
  - Required
- `content` (TEXT)
  - The actual message content
  - Required
  - Max length: 10,000 characters
- `created_at` (TIMESTAMP WITH TIME ZONE)
  - Timestamp when message was created
  - Auto-populated

**Constraints**:
- Foreign key constraint on `conversation_id` referencing `conversations.id`
- Foreign key constraint on `user_id` referencing `users.id`
- Check constraint to ensure `role` is either 'user' or 'assistant'
- Index on `conversation_id` for efficient retrieval
- Index on `created_at` for chronological ordering

**Validation Rules**:
- `conversation_id` must reference an existing conversation
- `user_id` must match the conversation owner
- `role` must be one of allowed values
- `content` cannot be empty

### Relationship Constraints

**User-Conversation Relationship**:
- Each conversation belongs to exactly one user
- A user can have multiple conversations
- When a user is deleted, their conversations should be archived or deleted

**Conversation-Message Relationship**:
- Each message belongs to exactly one conversation
- A conversation can have multiple messages
- Messages are tied to the same user as their conversation

## State Transitions

### Message Lifecycle
```
CREATED (when message is first saved)
  ↓
STORED (when message is persisted in database)
  ↓
RETRIEVED (when message is fetched for conversation context)
  ↓
DISPLAYED (when message is shown to user)
```

## Indexing Strategy

**Primary Indexes**:
- `conversations.id` (primary key)
- `messages.id` (primary key)

**Secondary Indexes**:
- `conversations.user_id` - for efficient user-specific queries
- `messages.conversation_id` - for retrieving conversation history
- `conversations.created_at` - for chronological ordering
- `messages.created_at` - for chronological ordering

## Data Integrity Rules

1. **User Isolation**: All queries must be filtered by `user_id` to prevent cross-user data access
2. **Referential Integrity**: Foreign key constraints enforce relationship validity
3. **Immutable Messages**: Once created, message content should not be modified
4. **Audit Trail**: Creation timestamps provide complete history

## Access Patterns

**Frequently Used Queries**:
1. Retrieve all conversations for a user
2. Retrieve all messages for a conversation
3. Retrieve latest messages for a conversation
4. Create new message in a conversation

**Query Optimization**:
- Use indexed columns in WHERE clauses
- Limit result sets for message history
- Consider pagination for long conversations

## Security Considerations

1. **Row-Level Security**: Always filter by `user_id` in queries
2. **Input Sanitization**: Validate message content before storage
3. **Access Control**: Verify user identity before allowing operations
4. **Data Encryption**: Ensure sensitive data is encrypted at rest

## Integration with Existing Schema

The new entities integrate with the existing Phase II schema by:
- Leveraging the existing `users` table for authentication
- Maintaining the existing `tasks` table for task operations
- Using the same user_id foreign key pattern for data isolation
- Following the same security and validation patterns