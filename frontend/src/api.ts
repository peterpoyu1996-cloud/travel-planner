import type { ItineraryResponse, TripConditions } from './types'

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

export async function fetchItinerary(conditions: TripConditions): Promise<ItineraryResponse> {
  const resp = await fetch(`${API_BASE}/itinerary`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(conditions),
  })

  if (!resp.ok) {
    const detail = await resp.text()
    throw new Error(`後端回傳錯誤 (${resp.status})：${detail}`)
  }

  return resp.json()
}
