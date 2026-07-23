import type { ItineraryResponse } from '../types'

interface Props {
  itinerary: ItineraryResponse
}

// 後端時間欄位是 ISO "HH:MM:SS"，畫面上不需要秒數
function formatClockTime(t: string): string {
  return t.slice(0, 5)
}

export function ItineraryView({ itinerary }: Props) {
  return (
    <div className="itinerary-view">
      {itinerary.warnings.length > 0 && (
        <div className="warnings">
          {itinerary.warnings.map((w, i) => (
            <p key={i}>⚠️ {w}</p>
          ))}
        </div>
      )}

      {itinerary.days.map((day) => (
        <div key={day.day_index} className="day-block">
          <h3>Day {day.day_index}｜{day.date}</h3>
          {day.stops.length === 0 && (
            <p className="day-empty">這天刻意留白，沒有硬湊行程——原因見上方提醒。</p>
          )}
          <div className="stop-list">
            {day.stops.map((stop) => (
              <div key={stop.id} className={`stop-card${stop.late_by_minutes ? ' stop-card-late' : ''}`}>
                <div className="stop-header">
                  {stop.eta && <span className="stop-eta">{formatClockTime(stop.eta)}</span>}
                  <span className="stop-name">{stop.name}</span>
                  <span className="stop-category">{stop.category}</span>
                </div>
                <p className="stop-reason">{stop.reason}</p>
                <div className="stop-meta">
                  {stop.suggested_stay_duration && <span>停留：{stop.suggested_stay_duration}</span>}
                  {stop.travel_time_from_prev && <span>交通：{stop.travel_time_from_prev}</span>}
                  {stop.parking_notes && <span>停車：{stop.parking_notes}</span>}
                  {stop.requires_reservation && <span className="badge">需預約</span>}
                  {stop.must_arrive_by && (
                    <span className="badge badge-deadline">訂位 {formatClockTime(stop.must_arrive_by)}</span>
                  )}
                </div>
                {stop.late_by_minutes != null && (
                  <p className="stop-late-warning">⚠️ 預估會晚到約 {Math.round(stop.late_by_minutes)} 分鐘，排不進這個時間窗</p>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
