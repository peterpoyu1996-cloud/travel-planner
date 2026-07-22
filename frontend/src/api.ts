import type {
  CustomRouteRequest,
  CustomRouteResponse,
  DayPlanRequest,
  DayPlanResponse,
  ItineraryResponse,
  PublicPOI,
  TripConditions,
} from './types'

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

async function postJson<TResponse>(path: string, body: unknown): Promise<TResponse> {
  const resp = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

  if (!resp.ok) {
    const detail = await resp.text()
    throw new Error(`後端回傳錯誤 (${resp.status})：${detail}`)
  }

  return resp.json()
}

export async function fetchItinerary(conditions: TripConditions): Promise<ItineraryResponse> {
  return postJson<ItineraryResponse>('/itinerary', conditions)
}

export async function fetchAttractions(): Promise<PublicPOI[]> {
  const resp = await fetch(`${API_BASE}/attractions`)
  if (!resp.ok) {
    const detail = await resp.text()
    throw new Error(`後端回傳錯誤 (${resp.status})：${detail}`)
  }
  return resp.json()
}

export async function fetchCustomRoute(request: CustomRouteRequest): Promise<CustomRouteResponse> {
  return postJson<CustomRouteResponse>('/custom-route', request)
}

export async function fetchDayPlan(request: DayPlanRequest): Promise<DayPlanResponse> {
  return postJson<DayPlanResponse>('/day-plan', request)
}
