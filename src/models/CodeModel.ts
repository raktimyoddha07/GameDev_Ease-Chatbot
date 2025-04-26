export interface ICodeSuggestion {
  original: string;
  suggested: string;
  explanation: string;
}

export interface ICodeAnalysisRequest {
  code: string;
  prompt: string;
}

export class CodeModel {
  private apiUrl = 'http://localhost:8000';

  async analyzeCode(request: ICodeAnalysisRequest): Promise<ICodeSuggestion> {
    const response = await fetch(`${this.apiUrl}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to analyze code');
    }

    return await response.json();
  }

  detectLanguage(code: string): string {
    if (code.includes('def ') || code.includes('import ') && code.includes(':')) return 'python';
    if (code.includes('cout') || code.includes('#include')) return 'cpp';
    if (code.includes('Console.') || code.includes('namespace')) return 'csharp';
    if (code.includes('public class') || code.includes('private void') || code.includes('extends') || code.includes('implements')) return 'java';
    if (code.includes('function') || code.includes('=>')) {
      if (code.includes(':') && (code.includes('interface') || code.includes('type '))) {
        return 'typescript';
      }
      return 'javascript';
    }
    return 'typescript';
  }
} 