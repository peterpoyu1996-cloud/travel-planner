import { DEMO_SCENARIOS } from '../data/demoScenarios'

interface Props {
  activeId: string | null
  onSelect: (id: string) => void
}

export function ScenarioPicker({ activeId, onSelect }: Props) {
  return (
    <div className="scenario-grid">
      {DEMO_SCENARIOS.map((s) => (
        <button
          key={s.id}
          type="button"
          className={`scenario-card${activeId === s.id ? ' active' : ''}`}
          onClick={() => onSelect(s.id)}
        >
          <span className="scenario-emoji" aria-hidden="true">{s.emoji}</span>
          <span className="scenario-title">{s.title}</span>
          <span className="scenario-persona">{s.persona}</span>
        </button>
      ))}
    </div>
  )
}
