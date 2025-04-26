import { useState, useRef, useEffect } from 'react'
import { Box, Container, TextField, Button, Typography, Paper, Alert, IconButton, Divider } from '@mui/material'
import DeleteIcon from '@mui/icons-material/Delete'
import Editor, { DiffEditor, BeforeMount } from '@monaco-editor/react'
import { ICodeView } from './presenters/CodePresenter'
import { CodePresenter } from './presenters/CodePresenter'
import { ICodeSuggestion } from './models/CodeModel'
import { IChatMessage } from './models/ChatModel'

function App() {
  const [code, setCode] = useState<string>('')
  const [prompt, setPrompt] = useState<string>('')
  const [suggestion, setSuggestion] = useState<ICodeSuggestion | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [editorLanguage, setEditorLanguage] = useState('javascript')
  const [messages, setMessages] = useState<IChatMessage[]>([])
  const chatEndRef = useRef<HTMLDivElement>(null)
  
  const [presenter] = useState<CodePresenter>(() => new CodePresenter({
    setLoading,
    setError,
    setSuggestion,
    setEditorLanguage,
    setMessages
  }))

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = () => {
    if (!code.trim() || !prompt.trim() || loading) return
    presenter.analyzeCode(code, prompt)
    setPrompt('')
  }

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      handleSubmit()
    }
  }

  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString()
  }

  // Configure Monaco editor theme
  const beforeMount: BeforeMount = (monacoEditor) => {
    monacoEditor.editor.defineTheme('diffTheme', {
      base: 'vs-dark',
      inherit: true,
      rules: [
        { token: 'diff.added', foreground: '4EC9B0', fontStyle: 'bold' },
        { token: 'diff.removed', foreground: 'F14C4C', fontStyle: 'bold' },
        { token: 'diff.modified', foreground: 'DCDCAA', fontStyle: 'bold' },
      ],
      colors: {
        'editor.background': '#1E1E1E',
        'editor.lineHighlightBackground': '#2D2D2D',
      }
    })
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4, height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          AI Code Iterator
        </Typography>
        <IconButton 
          color="error" 
          onClick={() => presenter.clearHistory()}
          title="Clear chat history"
        >
          <DeleteIcon />
        </IconButton>
      </Box>

      <Box sx={{ display: 'flex', gap: 2, height: 'calc(100vh - 150px)' }}>
        {/* Left panel: Code Editor */}
        <Paper elevation={3} sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          <Box sx={{ position: 'relative', flex: 1 }}>
            {!code && (
              <Typography
                sx={{
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  transform: 'translate(-50%, -50%)',
                  color: '#6e7681',
                  fontSize: '14px',
                  fontFamily: 'Consolas, Monaco, monospace',
                  opacity: 0.8,
                  pointerEvents: 'none',
                  zIndex: 1,
                }}
              >
                Write your code here
              </Typography>
            )}
            <Editor
              height="100%"
              defaultLanguage="javascript"
              language="javascript"
              value={code}
              onChange={(value) => setCode(value || '')}
              theme="vs-dark"
              options={{
                minimap: { enabled: false },
                fontSize: 14,
              }}
            />
          </Box>
        </Paper>

        {/* Right panel: Chat and Suggestions */}
        <Paper elevation={3} sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          {/* Chat messages */}
          <Box sx={{ flex: 1, overflowY: 'auto', p: 2 }}>
            {messages.map((message) => (
              <Box
                key={message.id}
                sx={{
                  mb: 2,
                  p: 2,
                  backgroundColor: message.type === 'user' ? '#2C2C2C' : '#1E1E1E',
                  borderRadius: 1,
                }}
              >
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="caption" sx={{ color: '#888' }}>
                    {message.type === 'user' ? 'You' : 'Assistant'}
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#888' }}>
                    {formatTimestamp(message.timestamp)}
                  </Typography>
                </Box>
                
                <Typography sx={{ whiteSpace: 'pre-wrap', mb: 1 }}>
                  {message.content}
                </Typography>

                {message.suggestion && (
                  <Box sx={{ mt: 2 }}>
                    <DiffEditor
                      height="200px"
                      language="javascript"
                      original={message.suggestion.original}
                      modified={message.suggestion.suggested}
                      theme="vs-dark"
                      options={{
                        renderSideBySide: false,
                        minimap: { enabled: false },
                        fontSize: 12,
                        readOnly: true,
                        lineNumbers: 'off',
                      }}
                    />
                    <Button
                      variant="contained"
                      color="success"
                      size="small"
                      sx={{ mt: 1 }}
                      onClick={() => setCode(message.suggestion!.suggested)}
                    >
                      Integrate Code
                    </Button>
                  </Box>
                )}
              </Box>
            ))}
            <div ref={chatEndRef} />
          </Box>

          {error && (
            <Alert severity="error" sx={{ mx: 2, mb: 2 }}>
              {error}
            </Alert>
          )}

          {/* Input area */}
          <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
            <TextField
              fullWidth
              multiline
              maxRows={4}
              variant="outlined"
              placeholder="What changes would you like to make to your code?"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={loading}
              sx={{
                '& .MuiOutlinedInput-root': {
                  backgroundColor: '#2C2C2C',
                }
              }}
            />
            <Button
              fullWidth
              variant="contained"
              color="primary"
              onClick={handleSubmit}
              disabled={!code || !prompt || loading}
              sx={{ mt: 1 }}
            >
              {loading ? 'Analyzing...' : 'Send'}
            </Button>
          </Box>
        </Paper>
      </Box>
    </Container>
  )
}

export default App
