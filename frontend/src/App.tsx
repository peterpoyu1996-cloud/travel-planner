import { useState } from 'react'
import './App.css'
import { fetchCustomRoute, fetchDayPlan, fetchItinerary } from './api'
import { TripForm } from './components/TripForm'
import { CustomRouteForm } from './components/CustomRouteForm'
import { DayPlanForm } from './components/DayPlanForm'
import { DayPlanResultView } from './components/DayPlanResultView'
import { ItineraryView } from './components/ItineraryView'
import { ScenarioPicker } from './components/ScenarioPicker'
import { DEMO_SCENARIOS } from './data/demoScenarios'
import type {
  CustomRouteRequest,
  CustomRouteResponse,
  DayPlanRequest,
  DayPlanResponse,
  ItineraryResponse,
  TripConditions,
} from './types'

type Mode = 'scenarios' | 'custom' | 'route-optimizer' | 'day-plan'

function App() {
  const [mode, setMode] = useState<Mode>('scenarios')

  const [activeScenarioId, setActiveScenarioId] = useState<string | null>(DEMO_SCENARIOS[0]?.id ?? null)

  const [itinerary, setItinerary] = useState<ItineraryResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [customRoute, setCustomRoute] = useState<CustomRouteResponse | null>(null)
  const [routeLoading, setRouteLoading] = useState(false)
  const [routeError, setRouteError] = useState<string | null>(null)

  const [dayPlan, setDayPlan] = useState<DayPlanResponse | null>(null)
  const [dayPlanLoading, setDayPlanLoading] = useState(false)
  const [dayPlanError, setDayPlanError] = useState<string | null>(null)

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

  async function handleCustomRouteSubmit(request: CustomRouteRequest) {
    setRouteLoading(true)
    setRouteError(null)
    setCustomRoute(null)
    try {
      const result = await fetchCustomRoute(request)
      setCustomRoute(result)
    } catch (e) {
      setRouteError(e instanceof Error ? e.message : String(e))
    } finally {
      setRouteLoading(false)
    }
  }

  async function handleDayPlanSubmit(request: DayPlanRequest) {
    setDayPlanLoading(true)
    setDayPlanError(null)
    setDayPlan(null)
    try {
      const result = await fetchDayPlan(request)
      setDayPlan(result)
    } catch (e) {
      setDayPlanError(e instanceof Error ? e.message : String(e))
    } finally {
      setDayPlanLoading(false)
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
        <button
          type="button"
          role="tab"
          aria-selected={mode === 'route-optimizer'}
          className={mode === 'route-optimizer' ? 'active' : ''}
          onClick={() => setMode('route-optimizer')}
        >
          自訂景點清單
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={mode === 'day-plan'}
          className={mode === 'day-plan' ? 'active' : ''}
          onClick={() => setMode('day-plan')}
        >
          分天規劃
        </button>
      </nav>

      <main>
        {mode === 'scenarios' && (
          <>
            <p className="section-intro">
              預先產生的範例，點擊即看、不呼叫 API，可以並排比較「知識庫實際計算」跟「直接問 Claude Chat」兩種產出方式的差異。
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

        {mode === 'route-optimizer' && (
          <>
            <CustomRouteForm onSubmit={handleCustomRouteSubmit} loading={routeLoading} />
            {routeError && <p className="error">發生錯誤：{routeError}</p>}
            {customRoute && (
              <>
                <p className="section-intro">
                  總移動時間約 {Math.round(customRoute.total_travel_minutes)} 分鐘。
                </p>
                <ItineraryView itinerary={customRoute} />
              </>
            )}
          </>
        )}

        {mode === 'day-plan' && (
          <>
            <DayPlanForm onSubmit={handleDayPlanSubmit} loading={dayPlanLoading} />
            {dayPlanError && <p className="error">發生錯誤：{dayPlanError}</p>}
            {dayPlan && <DayPlanResultView result={dayPlan} />}
          </>
        )}
      </main>
    </div>
  )
}

export default App
