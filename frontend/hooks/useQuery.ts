// hooks/useQuery.ts - React Query hooks
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
// import { apiClient } from '@/lib/api-client'; // Assuming an axios or fetch wrapper
import { QueryRequest } from '../types/api';

// This is a placeholder for the actual API client
const apiClient = {
    get: (url: string) => Promise.resolve({ data: [] }),
    post: (url: string, data: any) => Promise.resolve({ data: {} }),
};


export function useDocuments() {
  return useQuery({
    queryKey: ['documents'],
    queryFn: () => apiClient.get('/documents').then(res => res.data),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useDocument(documentId: string) {
  return useQuery({
    queryKey: ['documents', documentId],
    queryFn: () => apiClient.get(`/documents/${documentId}`).then(res => res.data),
    enabled: !!documentId,
  });
}

export function useDocumentQuery() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ documentId, query }: { documentId: string; query: QueryRequest }) =>
      apiClient.post(`/documents/${documentId}/query`, query),
    onSuccess: (data, variables) => {
      // Update document queries cache
      queryClient.invalidateQueries({ queryKey: ['documents', variables.documentId, 'queries'] });
    },
  });
}

export function useDocumentUpload() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      return apiClient.post('/documents/upload', formData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
  });
}
