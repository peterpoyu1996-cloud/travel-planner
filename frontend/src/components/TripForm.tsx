import { useState } from 'react'
import type { BudgetLevel, TripConditions } from '../types'

interface Props {
  onSubmit: (conditions: TripConditions) => void
  loading: boolean
}

const today = new Date().toISOString().slice(0, 10)

export function TripForm({ onSubmit, loading }: Props) {
  const [startDate, setStartDate] = useState(today)
  const [endDate, setEndDate] = useState(today)
  const [lodging, setLodging] = useState('')
  const [hasCar, setHasCar] = useState(true)
  const [hasKids, setHasKids] = useState(false)
  const [kidAgeRange, setKidAgeRange] = useState('')
  const [budgetLevel, setBudgetLevel] = useState<BudgetLevel>('$$')
  const [startLocation, setStartLocation] = useState('那霸機場')

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    onSubmit({
      start_date: startDate,
      end_date: endDate,
      lodging,
      has_car: hasCar,
      has_kids: hasKids,
      kid_age_range: hasKids ? kidAgeRange || null : null,
      budget_level: budgetLevel,
      start_location: startLocation,
    })
  }

  return (
    <form className="trip-form" onSubmit={handleSubmit}>
      <div className="field-row">
        <label>
          出發日期
          <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} required />
        </label>
        <label>
          回程日期
          <input type="date" value={endDate} min={startDate} onChange={(e) => setEndDate(e.target.value)} required />
        </label>
      </div>

      <label>
        住宿地
        <input
          type="text"
          placeholder="例：美麗海村公寓 / 那霸市區飯店"
          value={lodging}
          onChange={(e) => setLodging(e.target.value)}
          required
        />
      </label>

      <label>
        目前所在地／出發地
        <input
          type="text"
          value={startLocation}
          onChange={(e) => setStartLocation(e.target.value)}
          required
        />
      </label>

      <div className="field-row">
        <label className="checkbox">
          <input type="checkbox" checked={hasCar} onChange={(e) => setHasCar(e.target.checked)} />
          有租車
        </label>
        <label className="checkbox">
          <input type="checkbox" checked={hasKids} onChange={(e) => setHasKids(e.target.checked)} />
          有帶小孩
        </label>
      </div>

      {hasKids && (
        <label>
          小孩年齡區間
          <select value={kidAgeRange} onChange={(e) => setKidAgeRange(e.target.value)}>
            <option value="">請選擇</option>
            <option value="學齡前">學齡前</option>
            <option value="國小">國小</option>
            <option value="青少年">青少年</option>
          </select>
        </label>
      )}

      <label>
        預算
        <select value={budgetLevel} onChange={(e) => setBudgetLevel(e.target.value as BudgetLevel)}>
          <option value="$">$（省錢）</option>
          <option value="$$">$$（一般）</option>
          <option value="$$$">$$$（寬裕）</option>
        </select>
      </label>

      <button type="submit" disabled={loading}>
        {loading ? '生成中...' : '生成行程建議'}
      </button>
    </form>
  )
}
