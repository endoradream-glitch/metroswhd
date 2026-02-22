import React, { useState } from 'react';
import axios from 'axios';
import { useRouter } from 'next/router';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const router = useRouter();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const url = `${process.env.NEXT_PUBLIC_API_BASE}/token`;
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);
      // OAuth2PasswordRequestForm requires these fields even if blank
      formData.append('grant_type', '');
      formData.append('scope', '');
      formData.append('client_id', '');
      formData.append('client_secret', '');
      const res = await axios.post(url, formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      const { access_token } = res.data;
      if (access_token) {
        localStorage.setItem('token', access_token);
        router.push('/dashboard');
      } else {
        alert('Invalid response');
      }
    } catch (err) {
      console.error(err);
      alert('Login failed');
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: '2rem auto', padding: '1rem', border: '1px solid #ccc' }}>
      <h1>Patrol Tracker Login</h1>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '1rem' }}>
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Username"
            required
            style={{ width: '100%', padding: '0.5rem' }}
          />
        </div>
        <div style={{ marginBottom: '1rem' }}>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            required
            style={{ width: '100%', padding: '0.5rem' }}
          />
        </div>
        <button type="submit" style={{ width: '100%', padding: '0.5rem' }}>Login</button>
      </form>
    </div>
  );
}