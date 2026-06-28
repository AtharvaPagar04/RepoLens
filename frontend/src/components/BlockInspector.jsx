export function BlockInspector({ block }) {
  if (!block) return <div className="panel-content" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>Select a block to inspect.</div>;

  return (
    <div className="panel-content" style={{ display: 'flex', flexDirection: 'column' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ marginBottom: '0.75rem', wordBreak: 'break-all', fontSize: '1.25rem', fontWeight: 600 }}>{block.name}</h2>
        <div className="flex-row" style={{ flexWrap: 'wrap', gap: '0.5rem' }}>
          <span className="badge" style={{ background: 'var(--accent)', color: 'white', borderColor: 'var(--accent)' }}>{block.block_type}</span>
          <span className="badge">{block.language}</span>
          <span className="badge">Lines {block.start_line}-{block.end_line}</span>
        </div>
      </div>
      
      <div className="card" style={{ padding: '1rem', marginBottom: '1.5rem', fontSize: '0.875rem' }}>
        <div style={{ marginBottom: '0.5rem' }}><strong style={{ color: 'var(--text-muted)' }}>Path:</strong> <span style={{ fontFamily: 'var(--font-mono)' }}>{block.relative_path}</span></div>
        {block.qualified_name && <div style={{ marginBottom: '0.5rem' }}><strong style={{ color: 'var(--text-muted)' }}>QName:</strong> <span style={{ fontFamily: 'var(--font-mono)' }}>{block.qualified_name}</span></div>}
        <div><strong style={{ color: 'var(--text-muted)' }}>Hash:</strong> <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>{block.code_hash}</span></div>
      </div>

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
        <div className="flex-between" style={{ padding: '0.5rem 1rem', background: 'var(--bg-dark)', border: '1px solid var(--border-color)', borderBottom: 'none', borderTopLeftRadius: '8px', borderTopRightRadius: '8px' }}>
          <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 600 }}>Source Code</span>
          <button className="btn-secondary" style={{ padding: '2px 8px', fontSize: '0.75rem' }} onClick={() => navigator.clipboard.writeText(block.content)}>Copy</button>
        </div>
        <div className="code-inspector">
          <pre style={{ margin: 0 }}>
            <code>{block.content}</code>
          </pre>
        </div>
      </div>
    </div>
  );
}
