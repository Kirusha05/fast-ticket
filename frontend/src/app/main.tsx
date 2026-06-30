import { createRoot } from 'react-dom/client';
import { Providers } from './providers';
import '@/index.css';

createRoot(document.getElementById('root')!).render(
  <Providers />
);
