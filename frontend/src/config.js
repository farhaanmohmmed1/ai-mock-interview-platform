// API Configuration
// In production (Vercel), use relative URLs
// In development, use localhost:8000

const API_BASE_URL = import.meta.env.PROD 
  ? ''  // Use relative URLs in production
  : 'http://localhost:8000';

export const API_URL = API_BASE_URL;

export default API_URL;
