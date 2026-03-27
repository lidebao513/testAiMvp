import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

console.log('main.tsx loaded')

const root = document.getElementById('root')
console.log('root element:', root)

if (root) {
  console.log('Rendering App component...')
  ReactDOM.createRoot(root).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>,
  )
  console.log('App component rendered successfully')
}