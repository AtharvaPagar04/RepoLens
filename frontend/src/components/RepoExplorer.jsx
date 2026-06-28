import { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import { FileTree } from './FileTree';
import { BlockList } from './BlockList';
import { BlockInspector } from './BlockInspector';

export function RepoExplorer({ repo, onBack }) {
  const [tree, setTree] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [blocks, setBlocks] = useState(null);
  const [selectedBlockId, setSelectedBlockId] = useState(null);
  const [selectedBlockDetail, setSelectedBlockDetail] = useState(null);
  
  const [loadingTree, setLoadingTree] = useState(false);
  const [loadingBlocks, setLoadingBlocks] = useState(false);
  const [loadingBlockDetail, setLoadingBlockDetail] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadTree();
  }, [repo.id]);

  const loadTree = async () => {
    setLoadingTree(true);
    try {
      const data = await apiClient.getFileTree(repo.id);
      setTree(data.tree ?? []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingTree(false);
    }
  };

  const handleSelectFile = async (path) => {
    if (!path) return;
    setSelectedFile(path);
    setSelectedBlockId(null);
    setSelectedBlockDetail(null);
    setLoadingBlocks(true);
    setBlocks(null);
    try {
      const data = await apiClient.getFileBlocks(repo.id, path);
      setBlocks(data.blocks ?? []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingBlocks(false);
    }
  };

  const handleSelectBlock = async (blockId) => {
    setSelectedBlockId(blockId);
    setLoadingBlockDetail(true);
    setSelectedBlockDetail(null);
    try {
      const data = await apiClient.getBlock(blockId);
      setSelectedBlockDetail(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingBlockDetail(false);
    }
  };

  return (
    <div>
      <div className="flex-row" style={{ marginBottom: '1rem' }}>
        <button className="btn-secondary" onClick={onBack}>&larr; Back</button>
        <h2 style={{ margin: 0 }}>{repo.name}</h2>
      </div>

      {error && <div style={{ color: 'var(--danger)', marginBottom: '1rem' }}>{error}</div>}

      <div className="explorer-layout">
        
        {!selectedBlockId && (
          <div className={`panel ${selectedFile ? 'resizable-panel' : ''}`} style={{ flex: selectedFile ? 'none' : 1, width: selectedFile ? '350px' : '100%' }}>
            <div className="panel-header">File Tree</div>
            {loadingTree ? (
              <div className="panel-content">Loading tree...</div>
            ) : (
              <FileTree 
                tree={tree} 
                onSelectFile={handleSelectFile} 
                selectedFile={selectedFile} 
              />
            )}
          </div>
        )}
        
        {selectedFile && (
          <div 
            className={`panel ${selectedBlockId ? 'resizable-panel' : ''}`} 
            style={{ 
              flex: selectedBlockId ? 'none' : 1, 
              width: selectedBlockId ? '350px' : 'auto',
              minWidth: 0,
              borderLeft: '1px solid var(--border-color)', 
              borderRight: '1px solid var(--border-color)' 
            }}
          >
            <div className="panel-header" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              {selectedBlockId && (
                <button 
                  className="btn-secondary" 
                  style={{ padding: '2px 8px', fontSize: '0.75rem' }}
                  onClick={() => { setSelectedBlockId(null); setSelectedBlockDetail(null); }}
                >
                  &larr; Tree
                </button>
              )}
              <span>Blocks in File</span>
            </div>
            {loadingBlocks ? (
              <div className="panel-content">Loading blocks...</div>
            ) : (
              <BlockList 
                blocks={blocks} 
                onSelectBlock={handleSelectBlock} 
                selectedBlockId={selectedBlockId} 
              />
            )}
          </div>
        )}

        {selectedBlockId && (
          <div className="panel" style={{ flex: 1, minWidth: 0 }}>
            <div className="panel-header">Block Inspector</div>
            {loadingBlockDetail ? (
              <div className="panel-content">Loading block details...</div>
            ) : (
              <BlockInspector block={selectedBlockDetail} />
            )}
          </div>
        )}
      </div>
    </div>
  );
}
