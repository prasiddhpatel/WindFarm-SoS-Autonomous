import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Box, Text } from '@react-three/drei'

const API = 'http://localhost:8080'

function TwinScene() {
  return (
    <Canvas camera={{ position: [3, 3, 3], fov: 50 }}>
      <ambientLight intensity={0.8} />
      <directionalLight position={[5, 5, 5]} intensity={1.0} />
      <Box args={[0.2, 2.0, 0.2]} position={[0, 1, 0]}>
        <meshStandardMaterial color="#d0d7de" />
      </Box>
      <Box args={[2.0, 0.05, 0.2]} position={[0.7, 2.1, 0]} rotation={[0, 0, 0.2]}>
        <meshStandardMaterial color="#7dd3fc" />
      </Box>
      <Text position={[0, 2.8, 0]} fontSize={0.15} color="white">WTG Digital Twin</Text>
      <OrbitControls />
    </Canvas>
  )
}

export default function App() {
  const [turbines, setTurbines] = useState([])
  const [patches, setPatches] = useState([])
  const [tasks, setTasks] = useState([])

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [t, p, k] = await Promise.all([
          axios.get(`${API}/turbines`),
          axios.get(`${API}/patches`),
          axios.get(`${API}/tasks`),
        ])
        setTurbines(t.data)
        setPatches(p.data)
        setTasks(k.data)
      } catch (e) {
        console.error(e)
      }
    }
    fetchAll()
    const id = setInterval(fetchAll, 5000)
    return () => clearInterval(id)
  }, [])

  const severityData = patches.slice(0, 20).map((p, i) => ({
    name: `${p.blade_index}:${p.span_pos.toFixed(2)}`,
    severity: p.severity || 0,
    rul: p.rul_days || 0,
  }))

  const taskData = tasks.map((t) => ({
    name: t.task_type,
    utility: t.utility || 0,
  }))

  return (
    <div className="app-shell">
      <header className="topbar">
        <h1>WindFarm SoS Operations Dashboard</h1>
        <div className="stats">
          <div className="stat-card"><span>Turbines</span><strong>{turbines.length}</strong></div>
          <div className="stat-card"><span>Tracked Patches</span><strong>{patches.length}</strong></div>
          <div className="stat-card"><span>Fleet Tasks</span><strong>{tasks.length}</strong></div>
        </div>
      </header>

      <section className="grid">
        <div className="panel twin-panel">
          <h2>Digital Twin</h2>
          <TwinScene />
        </div>

        <div className="panel">
          <h2>Patch Severity</h2>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={severityData}>
              <XAxis dataKey="name" hide />
              <YAxis domain={[0, 1]} />
              <Tooltip />
              <Line type="monotone" dataKey="severity" stroke="#38bdf8" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="panel">
          <h2>MRTA Utility</h2>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={taskData}>
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="utility" fill="#4ade80" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="panel wide">
          <h2>Patch Table</h2>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Blade</th>
                  <th>Chord</th>
                  <th>Span</th>
                  <th>Severity</th>
                  <th>RUL (days)</th>
                  <th>Recommendation</th>
                </tr>
              </thead>
              <tbody>
                {patches.slice(0, 20).map((p) => (
                  <tr key={p.id}>
                    <td>{p.blade_index}</td>
                    <td>{p.chord_pos.toFixed(2)}</td>
                    <td>{p.span_pos.toFixed(2)}</td>
                    <td>{(p.severity || 0).toFixed(3)}</td>
                    <td>{p.rul_days ? p.rul_days.toFixed(1) : '—'}</td>
                    <td>{p.recommendation || 'monitor'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </div>
  )
}
