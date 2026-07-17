import type { ItineraryResponse } from '../types'

interface Props {
  itinerary: ItineraryResponse
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
          <div className="stop-list">
            {day.stops.map((stop) => (
              <div key={stop.id} className="stop-card">
                <div className="stop-header">
                  <span className="stop-name">{stop.name}</span>
                  <span className="stop-category">{stop.category}</span>
                </div>
                <p className="stop-reason">{stop.reason}</p>
                <div className="stop-meta">
                  {stop.suggested_stay_duration && <span>停留：{stop.suggested_stay_duration}</span>}
                  {stop.travel_time_from_prev && <span>交通：{stop.travel_time_from_prev}</span>}
                  {stop.parking_notes && <span>停車：{stop.parking_notes}</span>}
                  {stop.requires_reservation && <span className="badge">需預約</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
