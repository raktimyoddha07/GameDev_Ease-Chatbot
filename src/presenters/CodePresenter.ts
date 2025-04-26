import { CodeModel, ICodeSuggestion, ICodeAnalysisRequest } from '../models/CodeModel';
import { ChatModel, IChatMessage } from '../models/ChatModel';

export interface ICodeView {
  setLoading(loading: boolean): void;
  setError(error: string | null): void;
  setSuggestion(suggestion: ICodeSuggestion | null): void;
  setEditorLanguage(language: string): void;
  setMessages(messages: IChatMessage[]): void;
}

export class CodePresenter {
  private model: CodeModel;
  private chatModel: ChatModel;
  private view: ICodeView;
  private messages: IChatMessage[] = [];

  constructor(view: ICodeView) {
    this.model = new CodeModel();
    this.chatModel = new ChatModel();
    this.view = view;
  }

  async analyzeCode(code: string, prompt: string): Promise<void> {
    try {
      this.view.setError(null);
      this.view.setLoading(true);

      // Add user message
      const userMessage: IChatMessage = {
        id: this.chatModel.generateMessageId(),
        type: 'user',
        content: prompt,
        code: code,
        timestamp: Date.now()
      };
      this.messages = this.chatModel.addMessage(this.messages, userMessage);
      this.view.setMessages(this.messages);

      // Set editor language to JavaScript for Phaser.js
      this.view.setEditorLanguage('javascript');

      const request: ICodeAnalysisRequest = {
        code,
        prompt,
      };

      const suggestion = await this.model.analyzeCode(request);
      
      // Add assistant message
      const assistantMessage: IChatMessage = {
        id: this.chatModel.generateMessageId(),
        type: 'assistant',
        content: suggestion.explanation,
        timestamp: Date.now(),
        suggestion: suggestion
      };
      this.messages = this.chatModel.addMessage(this.messages, assistantMessage);
      this.view.setMessages(this.messages);
      this.view.setSuggestion(suggestion);
    } catch (error) {
      console.error('Error:', error);
      this.view.setError(error instanceof Error ? error.message : 'An unexpected error occurred');
      this.view.setSuggestion(null);
    } finally {
      this.view.setLoading(false);
    }
  }

  clearHistory(): void {
    this.messages = [];
    this.view.setMessages(this.messages);
    this.view.setSuggestion(null);
  }
} 