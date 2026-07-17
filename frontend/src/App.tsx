import { useState } from 'react'
import './App.css'
import { fetchItinerary } from './api'
import { TripForm } from './components/TripForm'
import { ItineraryView } from './components/ItineraryView'
import type { ItineraryResponse, TripConditions } from './types'

function App() {
  const [itinerary, setItinerary] = useState<ItineraryResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(conditions: TripConditions) {
    setLoading(true)
    setError(null)
    setItinerary(null)
    try {
      const result = await fetchItinerary(conditions)
      setItinerary(result)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-shell">
      <header>
        <h1>旅遊決策助手（沖繩試點）</h1>
        <p className="subtitle">輸入條件，根據知識庫生成多日行程建議</p>
      </header>

      <main>
        <TripForm onSubmit={handleSubmit} loading={loading} />

        {error && <p className="error">發生錯誤：{error}</p>}
        {itinerary && <ItineraryView itinerary={itinerary} />}
      </main>
    </div>
  )
}

export default App
