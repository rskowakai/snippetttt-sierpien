'use client';

import { useState, useRef, useEffect } from 'react';
// import { Button } from '@/components/ui/button'; // Assuming shadcn/ui
// import { Textarea } from '@/components/ui/textarea'; // Assuming shadcn/ui
// ... other UI imports
import { useDocumentQuery } from '../hooks/useQuery';
import { Query } from '../types/api';

// Stubs for missing components and utils
const Button = ({ children, ...props }: any) => <button {...props}>{children}</button>;
const Textarea = (props: any) => <textarea {...props} />;
const Card = ({ children }: { children: React.ReactNode }) => <div>{children}</div>;
const CardContent = ({ children }: { children: React.ReactNode }) => <div>{children}</div>;
const Badge = ({ children }: { children: React.ReactNode }) => <span>{children}</span>;
const ScrollArea = ({ children }: { children: React.ReactNode }) => <div>{children}</div>;
const Send = () => <span>&gt;</span>;
const Loader2 = () => <span>~</span>;


interface QueryInterfaceProps {
  documentId: string;
  documentName: string;
}

export function QueryInterface({ documentId, documentName }: QueryInterfaceProps) {
  const [question, setQuestion] = useState('');
  const [queries, setQueries] = useState<Query[]>([]);
  const queryMutation = useDocumentQuery();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() || queryMutation.isPending) return;

    const tempQueryId = 'temp-' + Date.now();
    setQueries(prev => [...prev, {
        id: tempQueryId,
        question,
        answer: '',
        confidenceScore: 0,
        processingTime: 0,
        queryType: 'factual',
        createdAt: new Date().toISOString(),
        isLoading: true
    }]);
    setQuestion('');

    try {
      const response: any = await queryMutation.mutateAsync({
        documentId,
        query: { question },
      });
      setQueries(prev => prev.map(q => q.id === tempQueryId ? response.data : q));
    } catch (error) {
      setQueries(prev => prev.map(q => q.id === tempQueryId ? { ...q, answer: 'An error occurred.', isLoading: false, isError: true } : q));
    }
  };

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <header style={{ borderBottom: '1px solid #ccc', padding: '1rem' }}>
        <h2>{documentName}</h2>
      </header>
      <ScrollArea style={{ flex: 1, padding: '1rem' }}>
        {queries.map(q => (
          <div key={q.id}>
            <p><strong>You:</strong> {q.question}</p>
            <div>
              <strong>AI:</strong>
              {q.isLoading ? <span>...</span> : <p>{q.answer}</p>}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </ScrollArea>
      <div style={{ borderTop: '1px solid #ccc', padding: '1rem' }}>
        <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '0.5rem' }}>
          <Textarea
            value={question}
            onChange={(e: any) => setQuestion(e.target.value)}
            placeholder="Zadaj pytanie o dokument..."
          />
          <Button type="submit" disabled={!question.trim() || queryMutation.isPending}>
            {queryMutation.isPending ? <Loader2 /> : <Send />}
          </button>
        </form>
      </div>
    </div>
  );
}
