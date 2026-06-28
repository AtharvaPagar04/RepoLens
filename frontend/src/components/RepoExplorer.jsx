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
        <div className="panel">
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
        
        <div className="panel" style={{ borderLeft: '1px solid var(--border-color)', borderRight: '1px solid var(--border-color)' }}>
          <div className="panel-header">Blocks in File</div>
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

        <div className="panel">
          <div className="panel-header">Block Inspector</div>
          {loadingBlockDetail ? (
            <div className="panel-content">Loading block details...</div>
          ) : (
            <BlockInspector block={selectedBlockDetail} />
          )}
        </div>
      </div>
    </div>
  );
}
