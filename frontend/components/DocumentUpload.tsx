'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
// import { Progress } from '@/components/ui/progress'; // Assuming shadcn/ui
// import { Alert, AlertDescription } from '@/components/ui/alert'; // Assuming shadcn/ui
// import { Button } from '@/components/ui/button'; // Assuming shadcn/ui
// import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'; // Assuming shadcn/ui
// import { FileText, Upload, X, CheckCircle, AlertCircle } from 'lucide-react';
import { useDocumentUpload } from '../hooks/useQuery';
// import { formatBytes } from '@/lib/utils';

// Stubs for missing components and utils
const Progress = ({ value }: { value: number }) => <progress value={value} max="100" />;
const Alert = ({ children }: { children: React.ReactNode }) => <div>{children}</div>;
const AlertDescription = ({ children }: { children: React.ReactNode }) => <p>{children}</p>;
const Button = ({ children, ...props }: any) => <button {...props}>{children}</button>;
const Card = ({ children }: { children: React.ReactNode }) => <div>{children}</div>;
const CardContent = ({ children }: { children: React.ReactNode }) => <div>{children}</div>;
const CardHeader = ({ children }: { children: React.ReactNode }) => <div>{children}</div>;
const CardTitle = ({ children }: { children: React.ReactNode }) => <h3>{children}</h3>;
const FileText = () => <span>F</span>;
const Upload = () => <span>U</span>;
const X = () => <span>X</span>;
const CheckCircle = () => <span>✓</span>;
const AlertCircle = () => <span>!</span>;
const formatBytes = (bytes: number) => `${(bytes / 1024).toFixed(2)} KB`;


interface UploadFile extends File {
  id: string;
  progress: number;
  status: 'pending' | 'uploading' | 'success' | 'error';
  error?: string;
}

export function DocumentUpload() {
  const [files, setFiles] = useState<UploadFile[]>([]);
  const uploadMutation = useDocumentUpload();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles: UploadFile[] = acceptedFiles.map(file => ({
      ...file,
      id: crypto.randomUUID(),
      progress: 0,
      status: 'pending' as const,
    }));

    setFiles(prev => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    maxSize: 100 * 1024 * 1024, // 100MB
  });

  const uploadFile = async (file: UploadFile) => {
    // ... implementation from prompt
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Upload Documents</CardTitle>
      </CardHeader>
      <CardContent>
        <div {...getRootProps()} style={{ border: '2px dashed #ccc', padding: '20px', textAlign: 'center' }}>
          <input {...getInputProps()} />
          {isDragActive ? <p>Drop the files here ...</p> : <p>Drag 'n' drop files here, or click to select</p>}
        </div>
        <div>
          {files.map(file => (
            <div key={file.id}>
              {file.name} - {formatBytes(file.size)}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
