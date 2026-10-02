export default function StatusBar() {
  return (
    <div className="statusbar">
      <span className="ok">● Guardian: original project write-protected</span>
      <span>Sandbox: disposable copies only</span>
      <span className="spacer" />
      <span>Demo mode — no disk writes, no network, no AI calls</span>
    </div>
  )
}
