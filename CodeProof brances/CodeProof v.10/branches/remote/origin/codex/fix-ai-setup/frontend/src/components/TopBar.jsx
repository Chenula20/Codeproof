export default function TopBar({ projectName, started, onReset }) {
  return (
    <div className="topbar">
      <div className="brand">Code<span>Proof</span></div>
      <div className="project-name">{projectName}</div>
      <div className="spacer" />
      <span className="chip demo">DEMO · MOCK SERVICES</span>
      <span className="chip sim">SIMULATED RESULTS</span>
      <span className="chip guardian dot">Guardian Active</span>
      {started && <button className="btn ghost sm" onClick={onReset}>Reset Demo</button>}
    </div>
  )
}
