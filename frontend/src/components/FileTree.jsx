import { useState } from 'react';

const FileTreeNode = ({ node, level = 0, onSelectFile, selectedFile }) => {
  const [expanded, setExpanded] = useState(false);
  const isDir = node.type === 'directory';
  const isSelected = selectedFile === node.path;

  const handleClick = () => {
    if (isDir) {
      setExpanded(!expanded);
    } else if (node.path) {
      onSelectFile(node.path);
    }
  };

  return (
    <div>
      <div 
        className={`tree-node ${isSelected ? 'selected' : ''}`}
        style={{ paddingLeft: `${level * 12 + 8}px` }}
        onClick={handleClick}
      >
        <span style={{ width: '16px', display: 'inline-block' }}>
          {isDir ? (expanded ? '📂' : '📁') : '📄'}
        </span>
        <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {node.name}
        </span>
        {!isDir && node.block_count > 0 && (
          <span style={{ fontSize: '0.75rem', opacity: 0.7 }}>{node.block_count}</span>
        )}
      </div>
      {isDir && expanded && node.children && (
        <div>
          {node.children.map(child => (
            <FileTreeNode 
              key={child.path} 
              node={child} 
              level={level + 1} 
              onSelectFile={onSelectFile}
              selectedFile={selectedFile}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export function FileTree({ tree, onSelectFile, selectedFile }) {
  if (!tree) return <div className="panel-content">Loading tree...</div>;
  // tree itself might be the root node
  const nodes = tree.children ? tree.children : (Array.isArray(tree) ? tree : [tree]);
  if (!nodes || nodes.length === 0) return <div className="panel-content">Empty repository.</div>;

  return (
    <div className="panel-content" style={{ padding: '0.5rem' }}>
      {nodes.map(node => (
        <FileTreeNode 
          key={node.path} 
          node={node} 
          onSelectFile={onSelectFile} 
          selectedFile={selectedFile}
        />
      ))}
    </div>
  );
}
