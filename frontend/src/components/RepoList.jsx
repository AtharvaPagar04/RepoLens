import { apiClient } from '../api/client';

export function RepoList({ repos, onOpen, onRefresh }) {
  const safeRepos = Array.isArray(repos) ? repos : [];
  
  const handleReindex = async (repoId) => {
    try {
      await apiClient.reindexRepo(repoId);
      onRefresh();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleDelete = async (repoId) => {
    if (!confirm('Are you sure you want to delete this repo?')) return;
    try {
      await apiClient.deleteRepo(repoId);
      onRefresh();
    } catch (err) {
      alert(err.message);
    }
  };

  if (safeRepos.length === 0) {
    return <div className="card">No repositories found. Import one above.</div>;
  }

  return (
    <div className="card">
      <h3>Recent Repositories</h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {safeRepos.map(repo => (
          <div key={repo.id} className="card" style={{ background: 'var(--bg-dark)', marginBottom: 0 }}>
            <div className="flex-between">
              <div>
                <h4 style={{ margin: '0 0 0.5rem 0' }}>{repo.name}</h4>
                <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                  Source: {repo.source_type} {repo.local_path ? `(${repo.local_path})` : ''}
                </div>
                <div className="flex-row" style={{ gap: '0.5rem' }}>
                  <span className="badge">Files: {repo.file_count || 0}</span>
                  <span className="badge">Blocks: {repo.block_count || 0}</span>
                </div>
              </div>
              <div className="flex-row">
                <button className="btn-primary" onClick={() => onOpen(repo)}>Open</button>
                <button className="btn-secondary" onClick={() => handleReindex(repo.id)}>Reindex</button>
                <button className="btn-danger" onClick={() => handleDelete(repo.id)}>Delete</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
