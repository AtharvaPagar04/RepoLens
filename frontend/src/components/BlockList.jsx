export function BlockList({ blocks, onSelectBlock, selectedBlockId }) {
  if (!blocks) return <div className="panel-content">Select a file to view blocks.</div>;
  const safeBlocks = Array.isArray(blocks) ? blocks : [];
  if (safeBlocks.length === 0) return <div className="panel-content">No code blocks found in this file.</div>;

  return (
    <div className="panel-content">
      {safeBlocks.map(block => (
        <div 
          key={block.id} 
          className={`block-card ${selectedBlockId === block.id ? 'selected' : ''}`}
          onClick={() => onSelectBlock(block.id)}
        >
          <span className="block-type">{block.block_type}</span>
          <div className="block-name">{block.name}</div>
          <div className="block-lines">
            Lines: {block.start_line} - {block.end_line}
          </div>
          {block.signature && (
            <div style={{ fontSize: '0.75rem', marginTop: '0.5rem', fontFamily: 'var(--font-mono)', opacity: 0.8, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {block.signature}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
