import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Portal from './pages/Portal'
import CreateUser from './pages/CreateUser'
import AgenticHub from './pages/AgenticHub'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/portal" element={<Portal />} />
        <Route path="/create-user" element={<CreateUser />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/hub" element={<AgenticHub />} />
      </Routes>
    </BrowserRouter>
  )
}


