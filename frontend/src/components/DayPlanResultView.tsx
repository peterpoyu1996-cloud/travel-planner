import { useState } from 'react'
import type { DayPlanResponse } from '../types'
import { ItineraryView } from './ItineraryView'

interface Props {
  result: DayPlanResponse
}

type ViewMode = 'chosen' | 'suggested'

export function DayPlanResultView({ result }: Props) {
  const [mode, setMode] = useState<ViewMode>('chosen')
  const hasSuggestion = result.suggested_order !== null && result.suggested_days !== null

  const activeDays = mode === 'suggested' && result.suggested_days ? result.suggested_days : result.chosen_days
  const activeMinutes = mode === 'suggested' && result.suggested_total_minutes !== null
    ? result.suggested_total_minutes
    : result.chosen_total_minutes

  return (
    <div className="day-plan-result">
      {hasSuggestion && (
        <div className="suggestion-banner">
          <h3>⚡ 系統發現更順的天序</h3>
          <p>
            你選的天序總移動約 {Math.round(result.chosen_total_minutes)} 分鐘；
            換個天序（每天的景點組合不變，只調整哪天先去）可以省下約 {Math.round(result.minutes_saved)} 分鐘，
            變成約 {Math.round(result.suggested_total_minutes ?? 0)} 分鐘。
          </p>
        </div>
      )}

      {hasSuggestion && (
        <div className="result-tabs" role="tablist">
          <button
            type="button"
            role="tab"
            aria-selected={mode === 'chosen'}
            className={mode === 'chosen' ? 'active' : ''}
            onClick={() => setMode('chosen')}
          >
            你的安排
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={mode === 'suggested'}
            className={mode === 'suggested' ? 'active' : ''}
            onClick={() => setMode('suggested')}
          >
            建議安排
          </button>
        </div>
      )}

      <p className="section-intro">總移動時間約 {Math.round(activeMinutes)} 分鐘。</p>
      <ItineraryView itinerary={{ days: activeDays, warnings: result.warnings }} />
    </div>
  )
}
