import { useState } from 'react';
import { apiClient } from '../api/client';

export function ImportRepoForm({ onImportSuccess }) {
  const [localPath, setLocalPath] = useState('');
  const [githubUrl, setGithubUrl] = useState('');
  const [repoNameLocal, setRepoNameLocal] = useState('');
  const [repoNameGithub, setRepoNameGithub] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleLocalImport = async (e) => {
    e.preventDefault();
    if (!localPath) return;
    setLoading(true);
    setError(null);
    try {
      const result = await apiClient.indexLocalRepo(localPath, repoNameLocal);
      await onImportSuccess(result.repo_id);
      setLocalPath('');
      setRepoNameLocal('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGithubImport = async (e) => {
    e.preventDefault();
    if (!githubUrl) return;
    setLoading(true);
    setError(null);
    try {
      const result = await apiClient.importGitHubRepo(githubUrl, repoNameGithub);
      await onImportSuccess(result.repo_id);
      setGithubUrl('');
      setRepoNameGithub('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h3>Import Repository</h3>
      {error && <div style={{ color: 'var(--danger)', marginBottom: '1rem' }}>{error}</div>}
      
      <div style={{ display: 'flex', gap: '2rem' }}>
        <div style={{ flex: 1 }}>
          <h4>Local Repository</h4>
          <form onSubmit={handleLocalImport}>
            <div className="form-group">
              <label>Local Path</label>
              <input 
                className="form-control"
                value={localPath}
                onChange={e => setLocalPath(e.target.value)}
                placeholder="/path/to/repo"
                required
              />
            </div>
            <div className="form-group">
              <label>Optional Name</label>
              <input 
                className="form-control"
                value={repoNameLocal}
                onChange={e => setRepoNameLocal(e.target.value)}
                placeholder="my-repo"
              />
            </div>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Analyzing...' : 'Analyze Local'}
            </button>
          </form>
        </div>

        <div style={{ flex: 1 }}>
          <h4>GitHub Repository</h4>
          <form onSubmit={handleGithubImport}>
            <div className="form-group">
              <label>GitHub URL</label>
              <input 
                className="form-control"
                value={githubUrl}
                onChange={e => setGithubUrl(e.target.value)}
                placeholder="https://github.com/user/repo"
                required
              />
            </div>
            <div className="form-group">
              <label>Optional Name</label>
              <input 
                className="form-control"
                value={repoNameGithub}
                onChange={e => setRepoNameGithub(e.target.value)}
                placeholder="my-repo"
              />
            </div>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Analyzing...' : 'Analyze GitHub'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
