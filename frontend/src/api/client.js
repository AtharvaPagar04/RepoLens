const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`API Error: ${response.status} - ${errorBody}`);
  }
  return response.json();
}

export const apiClient = {
  healthCheck: () => request('/health'),
  
  listRepos: async () => {
    const data = await request('/api/repos');
    return data.repos ?? [];
  },
  
  indexLocalRepo: (path, name) => 
    request('/api/repos/index-local', {
      method: 'POST',
      body: JSON.stringify({ path, name: name || undefined })
    }),
    
  importGitHubRepo: (repoUrl, name) =>
    request('/api/repos/import-github', {
      method: 'POST',
      body: JSON.stringify({ repo_url: repoUrl, name: name || undefined })
    }),
    
  getRepo: (repoId) => request(`/api/repos/${repoId}`),
  
  reindexRepo: (repoId) => 
    request(`/api/repos/${repoId}/reindex`, { method: 'POST' }),
    
  deleteRepo: (repoId) => 
    request(`/api/repos/${repoId}`, { method: 'DELETE' }),
    
  getFileTree: (repoId) => 
    request(`/api/repos/${repoId}/files/tree`),
    
  getFileBlocks: (repoId, path) => {
    if (!path) {
      throw new Error('File path is required to load blocks');
    }
    return request(`/api/repos/${repoId}/files/blocks?path=${encodeURIComponent(path)}`);
  },
    
  getBlock: (blockId) => 
    request(`/api/blocks/${blockId}`),
};
