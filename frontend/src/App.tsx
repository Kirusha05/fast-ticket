import { useAuth0 } from "@auth0/auth0-react"

function App() {
  const {
    isLoading,
    isAuthenticated,
    error,
    loginWithRedirect: login,
    logout: auth0Logout,
    user,
    getAccessTokenSilently
  } = useAuth0();

  const logout = () =>
    auth0Logout({ logoutParams: { returnTo: window.location.origin } });
  
  const callBackend = async () => {
    try {
      // 1. Fetch the short-lived access token
      const token = await getAccessTokenSilently();
      console.log(token)

      // 2. Attach it to your HTTP request
      const response = await fetch('http://localhost:8000/users/profile', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      const data = await response.json();
      console.log(data);
    } catch (error) {
      console.error("API Call failed", error);
    }
  };

  if (isLoading) return "Loading...";

  return isAuthenticated ? (
    <>
      <p>Logged in as {user.email}</p>
      <h1>User Profile</h1>
      <pre>{JSON.stringify(user, null, 2)}</pre>
      <button onClick={callBackend}>Fetch data</button>
      <button onClick={logout}>Logout</button>
    </>
  ) : (
    <>
      {error && <p>Error: {error.message}</p>}
      <button onClick={() => login()}>Login</button>
    </>
  );
}

export default App
