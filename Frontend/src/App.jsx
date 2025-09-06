import { useEffect, useState } from "react";
import Dashboard from "./Pages/Dashboard";
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  // const [count, setCount] = useState(0)

  return (
    <>
       <div className="min-h-screen bg-gray-100 p-6">
      <h1 className="text-3xl font-bold mb-6 text-center">📧 AI Email Assistant</h1>
      <Dashboard />
    </div>
    </>
  )
}

export default App
