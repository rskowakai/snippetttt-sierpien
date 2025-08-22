import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/lib/supabase";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { FileText, Download, Eye, Lock } from "lucide-react";

interface DocumentWithDetails {
  id: string;
  original_filename: string;
  document_type: string;
  file_size: number;
  is_encrypted: boolean;
  created_at: string;
  cases?: {
    title: string;
  };
}

export function DocumentsTable() {
  const { data: documents = [], isLoading } = useQuery({
    queryKey: ['recent-documents'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('documents')
        .select(`
          *,
          cases (title)
        `)
        .order('created_at', { ascending: false })
        .limit(10);

      if (error) throw error;
      return data as DocumentWithDetails[];
    },
  });

  const formatFileSize = (bytes: number) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const formatDocumentType = (type: string) => {
    return type.charAt(0).toUpperCase() + type.slice(1);
  };

  if (isLoading) {
    return (
      <div className="mt-8">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="w-48 h-6 bg-gray-200 rounded animate-pulse"></div>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="flex items-center space-x-4 animate-pulse">
                  <div className="w-10 h-10 bg-gray-200 rounded-lg"></div>
                  <div className="flex-1">
                    <div className="w-48 h-4 bg-gray-200 rounded mb-2"></div>
                    <div className="w-24 h-3 bg-gray-200 rounded"></div>
                  </div>
                  <div className="w-20 h-6 bg-gray-200 rounded"></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="mt-8">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Recent Documents</h2>
            <Button variant="ghost" className="text-blue-700 hover:underline text-sm font-medium" data-testid="button-view-all">
              View All Documents
            </Button>
          </div>
        </div>
        
        {documents.length === 0 ? (
          <div className="px-6 py-12 text-center text-gray-500" data-testid="empty-documents">
            <FileText className="mx-auto h-12 w-12 text-gray-300 mb-4" />
            <p>No documents uploaded yet</p>
            <p className="text-sm mt-2">Upload your first document to get started</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Document</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Case</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Uploaded</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-gray-50" data-testid={`document-row-${doc.id}`}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-10 h-10 bg-blue-700 bg-opacity-10 rounded-lg flex items-center justify-center mr-3">
                          <FileText className="text-blue-700" size={16} />
                        </div>
                        <div>
                          <div className="text-sm font-medium text-gray-900" data-testid={`filename-${doc.id}`}>
                            {doc.original_filename}
                          </div>
                          <div className="text-sm text-gray-500">{formatFileSize(doc.file_size)}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900" data-testid={`type-${doc.id}`}>
                      {formatDocumentType(doc.document_type)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900" data-testid={`case-${doc.id}`}>
                      {doc.cases?.title || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap" data-testid={`status-${doc.id}`}>
                      <Badge 
                        variant={doc.is_encrypted ? "default" : "secondary"}
                        className={doc.is_encrypted ? "bg-green-600 bg-opacity-10 text-green-600" : "bg-yellow-100 text-yellow-800"}
                      >
                        <Lock className="mr-1 h-3 w-3" />
                        {doc.is_encrypted ? "Encrypted" : "Processing"}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500" data-testid={`date-${doc.id}`}>
                      {new Date(doc.created_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div className="flex items-center space-x-2">
                        <Button 
                          variant="ghost" 
                          size="sm"
                          className="text-blue-700 hover:underline" 
                          data-testid={`button-view-${doc.id}`}
                        >
                          <Eye className="h-4 w-4 mr-1" />
                          View
                        </Button>
                        <Button 
                          variant="ghost" 
                          size="sm"
                          className="text-gray-400 hover:text-gray-600" 
                          data-testid={`button-download-${doc.id}`}
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
