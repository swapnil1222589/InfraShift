export function buildGitHubPullRequestUrl(
  repositoryUrl: string,
  pullRequestNumber: number
): string {
  const urlTrimmed = repositoryUrl.trim();
  
  try {
    const parsed = new URL(urlTrimmed);
    
    // Verify protocol
    if (parsed.protocol !== 'https:' && parsed.protocol !== 'http:') {
      throw new Error('Invalid protocol');
    }
    
    // Verify hostname
    if (parsed.hostname !== 'github.com' && parsed.hostname !== 'www.github.com') {
      throw new Error('Invalid hostname');
    }
    
    // Extract pathname and clean it
    const pathParts = parsed.pathname
      .replace(/\/$/, '')
      .replace(/\.git$/i, '')
      .split('/')
      .filter(Boolean);
      
    // Verify exact owner/repo format
    if (pathParts.length !== 2) {
      throw new Error('Invalid repository format');
    }
    
    const owner = pathParts[0];
    const repository = pathParts[1];
    
    return `https://github.com/${owner}/${repository}/pull/${pullRequestNumber.toString().trim()}`;
  } catch (error) {
    throw new Error('Failed to parse GitHub repository URL');
  }
}
