import { useState, useEffect } from 'react';
import { apiClient } from './api/client';
import { ImportRepoForm } from './components/ImportRepoForm';
import { RepoList } from './components/RepoList';
import { RepoExplorer } from './components/RepoExplorer';

function App() {
  const [repos, setRepos] = useState([]);
  const [selectedRepo, setSelectedRepo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchRepos = async () => {
    setLoading(true);
    setError(null);
    try {
      const repos = await apiClient.listRepos();
      setRepos(repos);
    } catch (err) {
      setError('Failed to fetch repositories. Is the backend running?');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRepos();
  }, []);

  return (
    <div className="container">
      <header className="header">
        <h1 className="title">RepoLens</h1>
        <p style={{ color: 'var(--text-muted)' }}>Interactive Codebase Explorer</p>
      </header>

      <main>
        {selectedRepo ? (
          <RepoExplorer 
            repo={selectedRepo} 
            onBack={() => {
              setSelectedRepo(null);
              fetchRepos();
            }} 
          />
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            <ImportRepoForm 
              onImportSuccess={async (repoId) => {
                await fetchRepos();
                if (repoId) {
                  const repo = await apiClient.getRepo(repoId);
                  setSelectedRepo(repo);
                }
              }} 
            />
            {loading ? (
              <div className="card">Loading repositories...</div>
            ) : error ? (
              <div className="card" style={{ color: 'var(--danger)' }}>{error}</div>
            ) : (
              <RepoList 
                repos={repos} 
                onOpen={setSelectedRepo} 
                onRefresh={fetchRepos}
              />
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
