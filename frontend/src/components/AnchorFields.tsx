import type { GeoAnchor, PublicPOI } from '../types'

// 那霸機場公開已知座標，當「手動座標」模式的預設值方便使用者不用自己查——
// 這是眾所皆知的公開地理事實，不是猜測填入的資料欄位
export const NAHA_AIRPORT = { lat: 26.1958, lng: 127.6455, label: '那霸機場' }

export type AnchorMode = 'poi' | 'coords'

export interface AnchorState {
  mode: AnchorMode
  poiId: string
  lat: string
  lng: string
  label: string
}

export function defaultAnchorState(): AnchorState {
  return {
    mode: 'coords',
    poiId: '',
    lat: String(NAHA_AIRPORT.lat),
    lng: String(NAHA_AIRPORT.lng),
    label: NAHA_AIRPORT.label,
  }
}

export function anchorStateToGeoAnchor(state: AnchorState): GeoAnchor {
  if (state.mode === 'poi') {
    return { poi_id: state.poiId }
  }
  return { lat: Number(state.lat), lng: Number(state.lng), label: state.label || null }
}

export function isAnchorStateComplete(state: AnchorState): boolean {
  return state.mode === 'coords' || state.poiId !== ''
}

interface Props {
  title: string
  pois: PublicPOI[]
  value: AnchorState
  onChange: (value: AnchorState) => void
}

export function AnchorFields({ title, pois, value, onChange }: Props) {
  return (
    <fieldset className="anchor-fields">
      <legend>{title}</legend>
      <div className="field-row">
        <label className="checkbox">
          <input
            type="radio"
            checked={value.mode === 'poi'}
            onChange={() => onChange({ ...value, mode: 'poi' })}
          />
          選知識庫景點/飯店
        </label>
        <label className="checkbox">
          <input
            type="radio"
            checked={value.mode === 'coords'}
            onChange={() => onChange({ ...value, mode: 'coords' })}
          />
          手動座標（例如機場）
        </label>
      </div>

      {value.mode === 'poi' ? (
        <select value={value.poiId} onChange={(e) => onChange({ ...value, poiId: e.target.value })} required>
          <option value="">請選擇</option>
          {pois.map((p) => (
            <option key={p.id} value={p.id} disabled={p.lat === null || p.lng === null}>
              {p.name}{p.lat === null ? '（缺座標，無法選）' : ''}
            </option>
          ))}
        </select>
      ) : (
        <div className="field-row">
          <label>
            名稱
            <input type="text" value={value.label} onChange={(e) => onChange({ ...value, label: e.target.value })} />
          </label>
          <label>
            緯度
            <input
              type="number"
              step="any"
              value={value.lat}
              onChange={(e) => onChange({ ...value, lat: e.target.value })}
              required
            />
          </label>
          <label>
            經度
            <input
              type="number"
              step="any"
              value={value.lng}
              onChange={(e) => onChange({ ...value, lng: e.target.value })}
              required
            />
          </label>
        </div>
      )}
    </fieldset>
  )
}
