import React from 'react'
import ReactDOM from 'react-dom/client'
import { CssBaseline, ThemeProvider, createTheme } from '@mui/material'
import './index.css'
import App from './App'

const theme = createTheme({
  palette: {
    mode: 'dark',
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>,
)
