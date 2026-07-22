import { useEffect, useState } from 'react'
import { fetchAttractions } from '../api'
import type { CustomRouteRequest, PublicPOI } from '../types'
import { AnchorFields, anchorStateToGeoAnchor, defaultAnchorState, isAnchorStateComplete } from './AnchorFields'
import type { AnchorState } from './AnchorFields'
import { AttractionPicker } from './AttractionPicker'

interface Props {
  onSubmit: (request: CustomRouteRequest) => void
  loading: boolean
}

const MAX_ATTRACTIONS = 30
const today = new Date().toISOString().slice(0, 10)

export function CustomRouteForm({ onSubmit, loading }: Props) {
  const [pois, setPois] = useState<PublicPOI[]>([])
  const [poisError, setPoisError] = useState<string | null>(null)

  const [selectedIds, setSelectedIds] = useState<string[]>([])
  const [tripDays, setTripDays] = useState(3)
  const [startDate, setStartDate] = useState(today)

  const [start, setStart] = useState<AnchorState>(defaultAnchorState())
  const [hasEnd, setHasEnd] = useState(false)
  const [end, setEnd] = useState<AnchorState>(defaultAnchorState())

  useEffect(() => {
    fetchAttractions()
      .then(setPois)
      .catch((e) => setPoisError(e instanceof Error ? e.message : String(e)))
  }, [])

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const request: CustomRouteRequest = {
      attraction_ids: selectedIds,
      trip_days: tripDays,
      start_date: startDate,
      start: anchorStateToGeoAnchor(start),
      end: hasEnd ? anchorStateToGeoAnchor(end) : null,
    }
    onSubmit(request)
  }

  const canSubmit = selectedIds.length > 0 && isAnchorStateComplete(start)

  return (
    <form className="trip-form custom-route-form" onSubmit={handleSubmit}>
      {poisError && <p className="error">景點清單載入失敗：{poisError}</p>}

      <div className="field-row">
        <label>
          天數
          <input
            type="number"
            min={1}
            max={14}
            value={tripDays}
            onChange={(e) => setTripDays(Number(e.target.value))}
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

      <div>
        <p className="section-intro">
          從知識庫勾選想去的景點，系統會算出實際車程最小的順序，依天數自動分天——
          不考慮開店時間、用餐時段、飯店 check-in/out，純粹以移動距離最小化排序。
        </p>
        <AttractionPicker
          pois={pois}
          selectedIds={selectedIds}
          onChange={setSelectedIds}
          maxSelectable={MAX_ATTRACTIONS}
        />
      </div>

      <button type="submit" disabled={loading || !canSubmit}>
        {loading ? '計算路線中...' : '計算最小移動路徑'}
      </button>
    </form>
  )
}
