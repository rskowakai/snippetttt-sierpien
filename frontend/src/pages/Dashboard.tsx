import React from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '../api/client';
import { Pismo } from '../types/pismo';

export default function Dashboard() {
  const { data, isLoading, error } = useQuery<Pismo[]>(['pisma'], async () => {
    const res = await api.get('/pisma');
    return res.data;
  });

  if (isLoading) return <div>Ładowanie...</div>;
  if (error) return <div>Błąd ładowania pism.</div>;

  return (
    <div>
      <h1>Moje Pisma</h1>
      {data && data.length > 0 ? (
        <ul>
          {data.map(p => (
            <li key={p.id}>
              {p.title} — <strong>{p.status}</strong>
            </li>
          ))}
        </ul>
      ) : (
        <p>Nie masz jeszcze żadnych pism.</p>
      )}
    </div>
  );
}
