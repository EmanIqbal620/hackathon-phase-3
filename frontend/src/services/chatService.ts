import { ChatMessage } from '@/types/chat';
import { authService } from './authService'; // Import authService to use the same token method

interface ChatRequest {
  conversation_id?: number;
  message: string;
}

interface ChatResponse {
  conversation_id: number;
  response: string;
  tool_calls: Array<{
    tool: string;
    status: string;
    result: any;
  }>;
}

class ChatService {
  private baseUrl: string;

  constructor() {
    // Use the backend API URL, defaulting to localhost:8000 for development
    this.baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
  }

  async sendMessage(userId: string, request: ChatRequest): Promise<ChatResponse> {
    try {
      // Use the same token retrieval method as other services
      const token = authService.getToken();

      if (!token) {
        throw new Error('No authentication token found');
      }

      // Full endpoint is http://localhost:8000/api/chat/{user_id}
      const response = await fetch(`${this.baseUrl}/api/chat/${userId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Chat API Error Response:', errorText);
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }

  async getConversation(userId: string, conversationId: number): Promise<ChatMessage[]> {
    try {
      const token = authService.getToken();

      if (!token) {
        throw new Error('No authentication token found');
      }

      // Full endpoint is http://localhost:8000/api/chat/{user_id}/{conversation_id}
      const response = await fetch(`${this.baseUrl}/api/chat/${userId}/${conversationId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Chat API Error Response:', errorText);
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      }

      const data = await response.json();
      return data.map((msg: any) => ({
        id: msg.id,
        userId: msg.user_id,
        conversationId: msg.conversation_id,
        role: msg.role,
        content: msg.content,
        timestamp: new Date(msg.timestamp),
        toolCallResults: msg.tool_call_results,
      }));
    } catch (error) {
      console.error('Error fetching conversation:', error);
      throw error;
    }
  }

  async createNewConversation(userId: string): Promise<number> {
    // For now, we'll just send a message without a conversation_id to create a new one
    // In practice, you might have a dedicated endpoint for this
    return this.sendMessage(userId, { message: "" }).then(response => response.conversation_id);
  }
}

export default new ChatService();