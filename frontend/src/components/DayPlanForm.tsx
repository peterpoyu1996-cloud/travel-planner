import { useEffect, useState } from 'react'
import { fetchAttractions } from '../api'
import type { DayPlanRequest, PublicPOI } from '../types'
import { AnchorFields, anchorStateToGeoAnchor, defaultAnchorState, isAnchorStateComplete } from './AnchorFields'
import type { AnchorState } from './AnchorFields'
import { AttractionPicker } from './AttractionPicker'
import { StopDeadlines } from './StopDeadlines'

interface Props {
  onSubmit: (request: DayPlanRequest) => void
  loading: boolean
}

const MAX_DAYS = 7 // 跟 common/geo/route_optimizer.py 的 MAX_DAY_PLAN_DAYS 對齊：
                    // 天序建議是窮舉全排列，7天=5040種排列，再多會太慢
const MAX_PER_DAY = 15
const DEFAULT_START_TIME = '09:00'
const today = new Date().toISOString().slice(0, 10)

function resizeBuckets(buckets: string[][], size: number): string[][] {
  if (buckets.length === size) return buckets
  if (buckets.length > size) return buckets.slice(0, size)
  return [...buckets, ...Array.from({ length: size - buckets.length }, () => [])]
}

function resizeStartTimes(times: string[], size: number): string[] {
  if (times.length === size) return times
  if (times.length > size) return times.slice(0, size)
  return [...times, ...Array.from({ length: size - times.length }, () => DEFAULT_START_TIME)]
}

export function DayPlanForm({ onSubmit, loading }: Props) {
  const [pois, setPois] = useState<PublicPOI[]>([])
  const [poisError, setPoisError] = useState<string | null>(null)

  const [tripDays, setTripDays] = useState(3)
  const [dayBuckets, setDayBuckets] = useState<string[][]>([[], [], []])
  const [dayStartTimes, setDayStartTimes] = useState<string[]>([DEFAULT_START_TIME, DEFAULT_START_TIME, DEFAULT_START_TIME])
  const [deadlines, setDeadlines] = useState<Record<string, string>>({}) // attraction_id -> "HH:MM"
  const [startDate, setStartDate] = useState(today)

  const [start, setStart] = useState<AnchorState>(defaultAnchorState())
  const [hasEnd, setHasEnd] = useState(false)
  const [end, setEnd] = useState<AnchorState>(defaultAnchorState())

  useEffect(() => {
    fetchAttractions()
      .then(setPois)
      .catch((e) => setPoisError(e instanceof Error ? e.message : String(e)))
  }, [])

  function handleTripDaysChange(value: number) {
    const clamped = Math.min(Math.max(value, 1), MAX_DAYS)
    setTripDays(clamped)
    setDayBuckets((prev) => resizeBuckets(prev, clamped))
    setDayStartTimes((prev) => resizeStartTimes(prev, clamped))
  }

  function handleDayChange(dayIndex: number, ids: string[]) {
    setDayBuckets((prev) => prev.map((day, i) => (i === dayIndex ? ids : day)))
  }

  function handleStartTimeChange(dayIndex: number, time: string) {
    setDayStartTimes((prev) => prev.map((t, i) => (i === dayIndex ? time : t)))
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const request: DayPlanRequest = {
      days: dayBuckets.map((ids, i) => ({
        stops: ids.map((id) => ({ attraction_id: id, must_arrive_by: deadlines[id] ?? null })),
        start_time: dayStartTimes[i],
      })),
      start_date: startDate,
      start: anchorStateToGeoAnchor(start),
      end: hasEnd ? anchorStateToGeoAnchor(end) : null,
    }
    onSubmit(request)
  }

  const canSubmit = isAnchorStateComplete(start) && dayBuckets.every((day) => day.length > 0)

  return (
    <form className="day-plan-form" onSubmit={handleSubmit}>
      {poisError && <p className="error">景點清單載入失敗：{poisError}</p>}

      <div className="field-row">
        <label>
          天數
          <input
            type="number"
            min={1}
            max={MAX_DAYS}
            value={tripDays}
            onChange={(e) => handleTripDaysChange(Number(e.target.value))}
            required
          />
        </label>
        <label>
          出發日期
          <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} required />
        </label>
      </div>

      <AnchorFields title="起點" pois={pois} value={start} onChange={setStart} />

      <label className="checkbox">
        <input type="checkbox" checked={hasEnd} onChange={(e) => setHasEnd(e.target.checked)} />
        終點跟起點不同
      </label>

      {hasEnd && <AnchorFields title="終點" pois={pois} value={end} onChange={setEnd} />}

      <p className="section-intro">
        每天自己選要去的景點（不限地區，篩選器只是方便瀏覽）。送出後系統會幫每天內部排最佳順序，
        並檢查「哪天先去」順不順——如果來回跑，會建議更好的天序，但不會動你每天選的景點組合。
      </p>

      <div className="day-bucket-list">
        {dayBuckets.map((ids, dayIndex) => (
          <div key={dayIndex} className="day-bucket-card">
            <div className="day-bucket-header">
              <h3>第 {dayIndex + 1} 天</h3>
              <label className="day-start-time">
                出發時間
                <input
                  type="time"
                  value={dayStartTimes[dayIndex] ?? DEFAULT_START_TIME}
                  onChange={(e) => handleStartTimeChange(dayIndex, e.target.value)}
                />
              </label>
            </div>
            <AttractionPicker
              pois={pois}
              selectedIds={ids}
              onChange={(newIds) => handleDayChange(dayIndex, newIds)}
              maxSelectable={MAX_PER_DAY}
            />
            <StopDeadlines stopIds={ids} pois={pois} value={deadlines} onChange={setDeadlines} />
          </div>
        ))}
      </div>

      <button type="submit" disabled={loading || !canSubmit}>
        {loading ? '計算中...' : '排每天順序並檢查天序'}
      </button>
    </form>
  )
}
