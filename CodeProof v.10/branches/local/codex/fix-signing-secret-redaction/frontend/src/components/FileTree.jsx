export default function FileTree({ nodes, selected, onSelect }) {
  const depth = (path) => path.split('/').length - 1
  return (
    <div className="file-tree">
      {nodes.map((node) => (
        <div
          key={node.path}
          className={`tree-row ${node.kind}${selected === node.path ? ' selected' : ''}`}
          style={{ paddingLeft: 8 + depth(node.path) * 14 }}
          onClick={() => node.kind === 'file' && onSelect(node.path)}
        >
          <span className="icon">{node.kind === 'dir' ? '▸' : '📄'}</span>
          {node.name}
        </div>
      ))}
    </div>
  )
}
