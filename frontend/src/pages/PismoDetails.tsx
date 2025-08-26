import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../api/client';
import { Pismo, Analiza } from '../types/pismo';

interface PismoDetailsData extends Pismo {
    analizy: Analiza[];
}

export default function PismoDetails() {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery<PismoDetailsData>(['pismo', id], async () => {
    const res = await api.get(`/pisma/${id}`);
    return res.data;
  }, { enabled: !!id });

  const buyMutation = useMutation(
      (opcjaId: number) => api.post(`/opcje/${opcjaId}/kup`),
      {
        onSuccess: () => {
            queryClient.invalidateQueries(['pismo', id]);
            alert("Opcja została zakupiona!");
        },
        onError: () => {
            alert("Wystąpił błąd podczas zakupu opcji.");
        }
      }
  );

  if (isLoading || !data) return <div>Ładuję dane pisma...</div>;

  return (
    <div>
      <h2>{data.title}</h2>
      <p><strong>Status:</strong> {data.status}</p>
      <hr />
      <h3>Treść pisma:</h3>
      <p>{data.content}</p>
      <hr />
      <h3>Analizy i Opcje:</h3>
      {data.analizy && data.analizy.length > 0 ? (
        data.analizy.map(analiza => (
          <div key={analiza.id}>
            <h4>Analiza #{analiza.id}</h4>
            <p>{analiza.summary}</p>
            <ul>
              {analiza.opcje.map(opcja => (
                <li key={opcja.id}>
                  {opcja.description} - {opcja.price} PLN
                  {!opcja.is_purchased && (
                    <button onClick={() => buyMutation.mutate(opcja.id)}>
                        Kup opcję
                    </button>
                  )}
                  {opcja.is_purchased && <strong> (Zakupiono)</strong>}
                </li>
              ))}
            </ul>
          </div>
        ))
      ) : (
        <p>Brak dostępnych analiz dla tego pisma.</p>
      )}
    </div>
  );
}
