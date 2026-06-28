export function BlockInspector({ block }) {
  if (!block) return <div className="panel-content">Select a block to inspect.</div>;

  return (
    <div className="panel-content">
      <div style={{ marginBottom: '1rem' }}>
        <h2 style={{ marginBottom: '0.5rem', wordBreak: 'break-all' }}>{block.name}</h2>
        <div className="flex-row" style={{ flexWrap: 'wrap', gap: '0.5rem' }}>
          <span className="badge">{block.block_type}</span>
          <span className="badge">{block.language}</span>
          <span className="badge">Lines {block.start_line}-{block.end_line}</span>
        </div>
      </div>
      
      <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
        <div><strong>Path:</strong> {block.relative_path}</div>
        {block.qualified_name && <div><strong>QName:</strong> {block.qualified_name}</div>}
      </div>

      <div className="code-inspector">
        <pre style={{ margin: 0 }}>
          <code>{block.content}</code>
        </pre>
      </div>
    </div>
  );
}
