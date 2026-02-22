import React, { useEffect, useState } from 'react';
import axios from 'axios';

export default function Dashboard() {
  const [patrols, setPatrols] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [messages, setMessages] = useState([]);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [incidentForm, setIncidentForm] = useState({
    camp: '',
    dtg: '',
    subject: '',
    lat: '',
    lon: '',
    details: '',
    follow_up: '',
  });

  const apiBase = process.env.NEXT_PUBLIC_API_BASE;
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;

  useEffect(() => {
    if (!token) return;
    fetchPatrols();
    fetchIncidents();
    // Open WebSocket connection for real-time updates
    const wsUrl = apiBase.replace(/^http/, 'ws') + '/ws';
    const ws = new WebSocket(wsUrl);
    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        setMessages((prev) => [...prev, msg]);
        // Update patrols list if message refers to patrol
        if (msg.type === 'location_update') {
          setPatrols((prev) =>
            prev.map((p) =>
              p.id === msg.patrol_id
                ? { ...p, current_location: msg.location, last_update: msg.timestamp, on_track: msg.on_track }
                : p
            )
          );
        }
      } catch (err) {
        console.error(err);
      }
    };
    return () => {
      ws.close();
    };
  }, [token]);

  const fetchPatrols = async () => {
    try {
      const res = await axios.get(`${apiBase}/patrols/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setPatrols(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchIncidents = async () => {
    try {
      const res = await axios.get(`${apiBase}/incidents/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setIncidents(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleIncidentSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        camp: incidentForm.camp,
        dtg: incidentForm.dtg ? new Date(incidentForm.dtg).toISOString() : new Date().toISOString(),
        subject: incidentForm.subject,
        location: [parseFloat(incidentForm.lat), parseFloat(incidentForm.lon)],
        incident_in_brief: incidentForm.details.split('\n').filter(Boolean),
        follow_up: incidentForm.follow_up || null,
        reporter: 'self', // Reporter will be replaced by backend
      };
      const res = await axios.post(`${apiBase}/incidents/report`, payload, {
        headers: { Authorization: `Bearer ${token}` },
      });
      alert('Incident reported');
      setIncidentForm({ camp: '', dtg: '', subject: '', lat: '', lon: '', details: '', follow_up: '' });
      fetchIncidents();
    } catch (err) {
      console.error(err);
      alert('Failed to submit incident');
    }
  };

  const handleReportDownload = async () => {
    if (!startDate || !endDate) {
      alert('Please enter start and end dates');
      return;
    }
    try {
      const res = await axios.get(
        `${apiBase}/reports/commander-brief?start=${startDate}&end=${endDate}`,
        {
          headers: { Authorization: `Bearer ${token}` },
          responseType: 'blob',
        }
      );
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `commander_brief_${startDate}_${endDate}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
    } catch (err) {
      console.error(err);
      alert('Failed to generate report');
    }
  };

  if (!token) {
    return <p>Please login first.</p>;
  }

  return (
    <div style={{ padding: '1rem' }}>
      <h1>Patrol Dashboard</h1>
      <h2>Patrols</h2>
      <table border="1" cellPadding="4" cellSpacing="0">
        <thead>
          <tr>
            <th>ID</th>
            <th>Unit</th>
            <th>Route</th>
            <th>Last Update</th>
            <th>On Track</th>
          </tr>
        </thead>
        <tbody>
          {patrols.map((p) => (
            <tr key={p.id}>
              <td>{p.id}</td>
              <td>{p.unit}</td>
              <td>{p.route_name}</td>
              <td>{p.last_update ? new Date(p.last_update).toLocaleString() : 'N/A'}</td>
              <td>{p.on_track ? 'Yes' : 'No'}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2>Real-Time Updates</h2>
      <ul>
        {messages.map((msg, idx) => (
          <li key={idx}>{JSON.stringify(msg)}</li>
        ))}
      </ul>

      <h2>Incidents</h2>
      <ul>
        {incidents.map((inc) => (
          <li key={inc.id}>
            <strong>{inc.subject}</strong> at {inc.camp} on {new Date(inc.dtg).toLocaleString()}
          </li>
        ))}
      </ul>

      <h2>Report Download</h2>
      <div>
        <input type="datetime-local" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
        <input type="datetime-local" value={endDate} onChange={(e) => setEndDate(e.target.value)} style={{ marginLeft: '0.5rem' }} />
        <button onClick={handleReportDownload} style={{ marginLeft: '0.5rem' }}>
          Download Commander Brief
        </button>
      </div>

      <h2>Submit Incident</h2>
      <form onSubmit={handleIncidentSubmit} style={{ marginTop: '1rem' }}>
        <div>
          <input
            type="text"
            placeholder="Camp"
            value={incidentForm.camp}
            onChange={(e) => setIncidentForm({ ...incidentForm, camp: e.target.value })}
            required
          />
        </div>
        <div>
          <input
            type="datetime-local"
            placeholder="DTG"
            value={incidentForm.dtg}
            onChange={(e) => setIncidentForm({ ...incidentForm, dtg: e.target.value })}
            required
          />
        </div>
        <div>
          <input
            type="text"
            placeholder="Subject"
            value={incidentForm.subject}
            onChange={(e) => setIncidentForm({ ...incidentForm, subject: e.target.value })}
            required
          />
        </div>
        <div>
          <input
            type="number"
            step="0.0001"
            placeholder="Latitude"
            value={incidentForm.lat}
            onChange={(e) => setIncidentForm({ ...incidentForm, lat: e.target.value })}
            required
          />
          <input
            type="number"
            step="0.0001"
            placeholder="Longitude"
            value={incidentForm.lon}
            onChange={(e) => setIncidentForm({ ...incidentForm, lon: e.target.value })}
            required
            style={{ marginLeft: '0.5rem' }}
          />
        </div>
        <div>
          <textarea
            placeholder="Incident details (each line)"
            value={incidentForm.details}
            onChange={(e) => setIncidentForm({ ...incidentForm, details: e.target.value })}
            rows={4}
            cols={40}
            required
          />
        </div>
        <div>
          <input
            type="text"
            placeholder="Follow-up (optional)"
            value={incidentForm.follow_up}
            onChange={(e) => setIncidentForm({ ...incidentForm, follow_up: e.target.value })}
          />
        </div>
        <button type="submit">Submit Incident</button>
      </form>
    </div>
  );
}