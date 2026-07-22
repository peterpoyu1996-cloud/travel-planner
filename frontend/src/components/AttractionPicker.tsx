import { useMemo, useState } from 'react'
import type { PublicPOI } from '../types'

interface Props {
  pois: PublicPOI[]
  selectedIds: string[]
  onChange: (ids: string[]) => void
  maxSelectable: number
}

type SortKey = 'name' | 'recommendation_score' | 'kid_friendly'

const SORT_LABELS: Record<SortKey, string> = {
  name: '名稱',
  recommendation_score: '推薦指數',
  kid_friendly: '親子友善',
}

export function AttractionPicker({ pois, selectedIds, onChange, maxSelectable }: Props) {
  const [search, setSearch] = useState('')
  const [regionFilter, setRegionFilter] = useState('')
  const [sortKey, setSortKey] = useState<SortKey>('name')

  const regions = useMemo(
    () => [...new Set(pois.map((p) => p.region_group).filter((r): r is string => Boolean(r)))],
    [pois],
  )

  const filtered = useMemo(() => {
    const keyword = search.trim()
    const result = pois.filter((p) => {
      if (regionFilter && p.region_group !== regionFilter) return false
      if (keyword && !p.name.includes(keyword)) return false
      return true
    })

    const sorted = [...result]
    if (sortKey === 'name') {
      sorted.sort((a, b) => a.name.localeCompare(b.name, 'zh-Hant'))
    } else {
      // 高分排前面，沒有值的（尚未查證過）排最後，不當成 0 分處理
      sorted.sort((a, b) => {
        const av = a[sortKey]
        const bv = b[sortKey]
        if (av === null && bv === null) return 0
        if (av === null) return 1
        if (bv === null) return -1
        return bv - av
      })
    }
    return sorted
  }, [pois, search, regionFilter, sortKey])

  function toggle(id: string) {
    if (selectedIds.includes(id)) {
      onChange(selectedIds.filter((i) => i !== id))
      return
    }
    if (selectedIds.length >= maxSelectable) return
    onChange([...selectedIds, id])
  }

  return (
    <div className="attraction-picker">
      <div className="attraction-picker-filters">
        <input
          type="text"
          placeholder="搜尋景點名稱"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select value={regionFilter} onChange={(e) => setRegionFilter(e.target.value)}>
          <option value="">全部地區</option>
          {regions.map((r) => (
            <option key={r} value={r}>{r}</option>
          ))}
        </select>
        <select value={sortKey} onChange={(e) => setSortKey(e.target.value as SortKey)}>
          {(Object.keys(SORT_LABELS) as SortKey[]).map((key) => (
            <option key={key} value={key}>依{SORT_LABELS[key]}排序</option>
          ))}
        </select>
        <span className="attraction-picker-count">
          已選 {selectedIds.length} / {maxSelectable}
        </span>
      </div>

      <div className="attraction-list">
        {filtered.map((poi) => {
          const checked = selectedIds.includes(poi.id)
          const disabled = !checked && selectedIds.length >= maxSelectable
          const missingCoords = poi.lat === null || poi.lng === null
          return (
            <label key={poi.id} className={`attraction-item${disabled ? ' disabled' : ''}`}>
              <input
                type="checkbox"
                checked={checked}
                disabled={disabled}
                onChange={() => toggle(poi.id)}
              />
              <span className="attraction-item-name">{poi.name}</span>
              <span className="attraction-item-meta">
                {poi.region_group}
                {poi.recommendation_score !== null && (
                  <span className="score-tag">推薦 {poi.recommendation_score.toFixed(1)}</span>
                )}
                {poi.kid_friendly !== null && (
                  <span className="score-tag">親子 {poi.kid_friendly.toFixed(1)}</span>
                )}
                {missingCoords && <span className="badge badge-warning">缺座標</span>}
              </span>
            </label>
          )
        })}
        {filtered.length === 0 && <p className="section-intro">沒有符合篩選條件的景點。</p>}
      </div>
    </div>
  )
}
