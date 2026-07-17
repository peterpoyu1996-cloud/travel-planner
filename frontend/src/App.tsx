import { useState } from 'react'
import './App.css'
import { fetchItinerary } from './api'
import { TripForm } from './components/TripForm'
import { ItineraryView } from './components/ItineraryView'
import { ScenarioPicker } from './components/ScenarioPicker'
import { DEMO_SCENARIOS } from './data/demoScenarios'
import type { ItineraryResponse, TripConditions } from './types'

type Mode = 'scenarios' | 'custom'

function App() {
  const [mode, setMode] = useState<Mode>('scenarios')

  const [activeScenarioId, setActiveScenarioId] = useState<string | null>(DEMO_SCENARIOS[0]?.id ?? null)

  const [itinerary, setItinerary] = useState<ItineraryResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const activeScenario = DEMO_SCENARIOS.find((s) => s.id === activeScenarioId) ?? null

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
        <h1>旅遊決策助手</h1>
        <p className="subtitle">沖繩試點・輸入條件，根據知識庫生成多日行程建議</p>
      </header>

      <nav className="mode-tabs" role="tablist">
        <button
          type="button"
          role="tab"
          aria-selected={mode === 'scenarios'}
          className={mode === 'scenarios' ? 'active' : ''}
          onClick={() => setMode('scenarios')}
        >
          範例情境
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={mode === 'custom'}
          className={mode === 'custom' ? 'active' : ''}
          onClick={() => setMode('custom')}
        >
          自訂條件生成
        </button>
      </nav>

      <main>
        {mode === 'scenarios' && (
          <>
            <p className="section-intro">
              四個預先產生的範例，直接展示這套系統怎麼根據不同家庭組成給出不同（甚至誠實留白的）建議，點擊即看，不呼叫 API。
            </p>
            <ScenarioPicker activeId={activeScenarioId} onSelect={setActiveScenarioId} />
            {activeScenario && (
              <div className="scenario-result">
                <div className="scenario-result-header">
                  <span className="scenario-emoji" aria-hidden="true">{activeScenario.emoji}</span>
                  <div>
                    <h2>{activeScenario.title}</h2>
                    <p className="scenario-persona">{activeScenario.persona}</p>
                  </div>
                </div>
                <ItineraryView itinerary={activeScenario.itinerary} />
              </div>
            )}
          </>
        )}

        {mode === 'custom' && (
          <>
            <TripForm onSubmit={handleSubmit} loading={loading} />
            {error && <p className="error">發生錯誤：{error}</p>}
            {itinerary && <ItineraryView itinerary={itinerary} />}
          </>
        )}
      </main>
    </div>
  )
}

export default App
