import type { PublicPOI } from '../types'

interface Props {
  stopIds: string[]
  pois: PublicPOI[]
  value: Record<string, string> // attraction_id -> "HH:MM"
  onChange: (value: Record<string, string>) => void
}

// 大部分景點都不用填訂位時間，只有使用者自己標的少數幾個（通常是午餐/晚餐）才需要。
export function StopDeadlines({ stopIds, pois, value, onChange }: Props) {
  const poiById = new Map(pois.map((p) => [p.id, p]))

  function handleToggle(id: string, enabled: boolean) {
    const next = { ...value }
    if (enabled) {
      next[id] = next[id] ?? '12:00'
    } else {
      delete next[id]
    }
    onChange(next)
  }

  function handleTimeChange(id: string, time: string) {
    onChange({ ...value, [id]: time })
  }

  if (stopIds.length === 0) return null

  return (
    <div className="stop-deadlines">
      <p className="stop-deadlines-hint">有訂位時間的景點（例如午餐/晚餐），可以標「幾點前必須到」：</p>
      {stopIds.map((id) => {
        const poi = poiById.get(id)
        const enabled = id in value
        return (
          <label key={id} className="stop-deadline-row">
            <input type="checkbox" checked={enabled} onChange={(e) => handleToggle(id, e.target.checked)} />
            <span className="stop-deadline-name">{poi?.name ?? id}</span>
            {enabled && (
              <input
                type="time"
                value={value[id]}
                onChange={(e) => handleTimeChange(id, e.target.value)}
              />
            )}
          </label>
        )
      })}
    </div>
  )
}
