export interface IChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: number;
  code?: string;
  suggestion?: {
    original: string;
    suggested: string;
    explanation: string;
  };
}

export class ChatModel {
  private readonly STORAGE_KEY = 'chat_history';

  loadChatHistory(): IChatMessage[] {
    const stored = localStorage.getItem(this.STORAGE_KEY);
    return stored ? JSON.parse(stored) : [];
  }

  saveChatHistory(messages: IChatMessage[]): void {
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(messages));
  }

  addMessage(messages: IChatMessage[], message: IChatMessage): IChatMessage[] {
    const updatedMessages = [...messages, message];
    this.saveChatHistory(updatedMessages);
    return updatedMessages;
  }

  clearHistory(): void {
    localStorage.removeItem(this.STORAGE_KEY);
  }

  generateMessageId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
} 