export default function BreakModal({ challenge, onStart, onClose }) {
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Break My App — {challenge.title}</h2>
        <div className="meta">
          <span className="chip">{challenge.id}</span>
          <span className="chip">{challenge.difficulty}</span>
          <span className="chip">Skill: {challenge.skill}</span>
        </div>
        <p className="description">{challenge.description}</p>
        <div className="error-box">{challenge.error_output}</div>
        <p className="description">
          A disposable challenge copy will be created. Your original project stays untouched.
        </p>
        <div className="actions">
          <button className="btn ghost" onClick={onClose}>Cancel</button>
          <button className="btn danger" onClick={onStart}>Start Investigation</button>
        </div>
      </div>
    </div>
  )
}
