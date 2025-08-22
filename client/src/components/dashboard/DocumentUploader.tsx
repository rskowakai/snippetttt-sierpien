import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/lib/supabase";
import { useToast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { CloudUpload, FileText, FileImage, Check, AlertCircle, RotateCcw } from "lucide-react";

interface ProcessingItem {
  id: string;
  document_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  error_message?: string;
  created_at: string;
  documents: {
    original_filename: string;
    mime_type: string;
  };
}

export function DocumentUploader() {
  const [uploading, setUploading] = useState(false);
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: processingQueue = [], isLoading } = useQuery({
    queryKey: ['processing-queue'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('processing_queue')
        .select(`
          *,
          documents (
            original_filename,
            mime_type
          )
        `)
        .order('created_at', { ascending: false })
        .limit(10);

      if (error) throw error;
      return data as ProcessingItem[];
    },
  });

  const uploadMutation = useMutation({
    mutationFn: async (files: File[]) => {
      const uploadedFiles = [];

      for (const file of files) {
        // Upload to temporary public bucket
        const fileName = `temp/${Date.now()}-${file.name}`;
        const { data: uploadData, error: uploadError } = await supabase.storage
          .from('documents-temp')
          .upload(fileName, file);

        if (uploadError) throw uploadError;

        // Create document record
        const { data: docData, error: docError } = await supabase
          .from('documents')
          .insert({
            original_filename: file.name,
            filename: fileName,
            file_size: file.size,
            mime_type: file.type,
            storage_path: uploadData.path,
            document_type: getDocumentType(file.type),
          })
          .select()
          .single();

        if (docError) throw docError;

        // Add to processing queue
        const { error: queueError } = await supabase
          .from('processing_queue')
          .insert({
            document_id: docData.id,
            status: 'pending',
            progress: 0,
          });

        if (queueError) throw queueError;

        uploadedFiles.push(docData);
      }

      return uploadedFiles;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['processing-queue'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
      toast({
        title: "Files uploaded successfully",
        description: "Your documents are being processed and encrypted.",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Upload failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const retryMutation = useMutation({
    mutationFn: async (documentId: string) => {
      const { error } = await supabase
        .from('processing_queue')
        .update({ status: 'pending', progress: 0, error_message: null })
        .eq('document_id', documentId);

      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['processing-queue'] });
      toast({
        title: "Processing restarted",
        description: "The document will be processed again.",
      });
    },
  });

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      uploadMutation.mutate(acceptedFiles);
    }
  }, [uploadMutation]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxSize: 50 * 1024 * 1024, // 50MB
  });

  const getDocumentType = (mimeType: string) => {
    if (mimeType.includes('pdf')) return 'contract';
    if (mimeType.includes('word')) return 'brief';
    return 'other';
  };

  const getFileIcon = (mimeType: string) => {
    if (mimeType?.includes('pdf')) return <FileText className="text-blue-700" />;
    if (mimeType?.includes('word')) return <FileImage className="text-blue-700" />;
    return <FileText className="text-blue-700" />;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <Check className="text-green-600 h-5 w-5" />;
      case 'failed':
        return <AlertCircle className="text-red-600 h-5 w-5" />;
      case 'processing':
        return <div className="w-3 h-3 bg-green-600 rounded-full animate-pulse" />;
      default:
        return <div className="w-3 h-3 bg-yellow-500 rounded-full" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Completed';
      case 'failed':
        return 'Failed';
      case 'processing':
        return 'Encrypting...';
      default:
        return 'Pending';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600';
      case 'failed':
        return 'text-red-600';
      case 'processing':
        return 'text-green-600';
      default:
        return 'text-yellow-600';
    }
  };

  return (
    <div className="lg:col-span-2">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-6">Document Upload & Processing</h2>
        
        {/* Upload Area */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer ${
            isDragActive ? 'border-blue-700 bg-blue-50' : 'border-gray-300 hover:border-blue-700'
          }`}
          data-testid="upload-dropzone"
        >
          <input {...getInputProps()} data-testid="upload-input" />
          <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
            <CloudUpload className="text-gray-400 text-2xl" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Upload Legal Documents</h3>
          <p className="text-gray-600 mb-4">
            {isDragActive ? 'Drop files here' : 'Drag and drop files here, or click to select'}
          </p>
          <Button
            type="button"
            className="bg-blue-700 text-white px-6 py-2 rounded-lg hover:bg-blue-800"
            disabled={uploadMutation.isPending}
            data-testid="button-select-files"
          >
            <CloudUpload className="mr-2 h-4 w-4" />
            Select Files
          </Button>
          <p className="text-xs text-gray-500 mt-4">Supported formats: PDF, DOC, DOCX (Max 50MB per file)</p>
        </div>

        {/* Processing Queue */}
        <div className="mt-8">
          <h3 className="text-md font-medium text-gray-900 mb-4">Recent Uploads & Processing Status</h3>
          {isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg animate-pulse">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gray-200 rounded-lg"></div>
                    <div>
                      <div className="w-48 h-4 bg-gray-200 rounded mb-2"></div>
                      <div className="w-32 h-3 bg-gray-200 rounded"></div>
                    </div>
                  </div>
                  <div className="w-24 h-2 bg-gray-200 rounded"></div>
                </div>
              ))}
            </div>
          ) : processingQueue.length === 0 ? (
            <div className="text-center py-8 text-gray-500" data-testid="empty-queue">
              No documents uploaded yet. Upload your first document to get started.
            </div>
          ) : (
            <div className="space-y-3">
              {processingQueue.map((item) => (
                <div key={item.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg" data-testid={`queue-item-${item.id}`}>
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-blue-700 bg-opacity-10 rounded-lg flex items-center justify-center">
                      {getFileIcon(item.documents?.mime_type)}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900" data-testid={`filename-${item.id}`}>
                        {item.documents?.original_filename || 'Unknown file'}
                      </p>
                      <p className="text-sm text-gray-600">
                        Uploaded {new Date(item.created_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(item.status)}
                      <span className={`text-sm font-medium ${getStatusColor(item.status)}`} data-testid={`status-${item.id}`}>
                        {getStatusText(item.status)}
                      </span>
                    </div>
                    {item.status === 'processing' && (
                      <div className="w-24">
                        <Progress value={item.progress} className="h-2" />
                      </div>
                    )}
                    {item.status === 'failed' && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => retryMutation.mutate(item.document_id)}
                        disabled={retryMutation.isPending}
                        data-testid={`button-retry-${item.id}`}
                      >
                        <RotateCcw className="h-4 w-4 mr-1" />
                        Retry
                      </Button>
                    )}
                    {item.status === 'completed' && getStatusIcon(item.status)}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
