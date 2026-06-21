import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { Auth0Provider } from "@auth0/auth0-react";
import { BrowserRouter } from 'react-router'
// import './index.css'
import App from './App.tsx'


createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Auth0Provider
        domain="krrr.eu.auth0.com"
        clientId="l48RZLGylbcQTAJXELwKhDcgCZUBFba0"
        authorizationParams={{ 
          redirect_uri: window.location.origin, 
          audience: 'https://fast-ticket.com'
        }}
        cacheLocation="localstorage"
      >
        <App />
      </Auth0Provider>
    </BrowserRouter>
  </StrictMode>,
)
