// types/api.ts - TypeScript type definitions

export enum UserRole {
    USER = 'user',
    ADMIN = 'admin',
}

export enum DocumentType {
    PDF = 'pdf',
    DOCX = 'docx',
    TXT = 'txt',
    AUDIO = 'audio',
    VIDEO = 'video',
}

export enum DocumentStatus {
    UPLOADED = 'uploaded',
    PROCESSING = 'processing',
    PROCESSED = 'processed',
    FAILED = 'failed',
}

export enum QueryType {
    FACTUAL = 'factual',
    INTERPRETIVE = 'interpretive',
    COMPARATIVE = 'comparative',
    PROCEDURAL = 'procedural',
}

export interface Subscription {
    plan: string;
    status: string;
    // add other subscription fields
}

export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName:string;
  role: UserRole;
  isActive: boolean;
  isVerified: boolean;
  createdAt: string;
  subscription?: Subscription;
}

export interface Document {
  id: string;
  filename: string;
  originalFilename: string;
  fileSize: number;
  documentType: DocumentType;
  status: DocumentStatus;
  processingProgress: number;
  summary?: string;
  keyTopics?: string[];
  documentCategory?: string;
  legalArea?: string[];
  createdAt: string;
  processedAt?: string;
}

export interface Citation {
    text: string;
    page: number;
    paragraph: number;
}

export interface Query {
  id: string;
  question: string;
  answer: string;
  confidenceScore: number;
  processingTime: number;
  queryType: QueryType;
  createdAt: string;
  citations?: Citation[];
  suggestions?: string[];
  isLoading?: boolean;
  isError?: boolean;
}

export interface QueryRequest {
  question: string;
  context?: Record<string, any>;
  includeCitations?: boolean;
  language?: string;
}
