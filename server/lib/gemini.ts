import { GoogleGenAI } from "@google/genai";

// Initialize Gemini AI client
const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY || "" });

export interface DocumentAnalysis {
  summary: string;
  keyPoints: string[];
  documentType: string;
  entities: {
    people: string[];
    organizations: string[];
    dates: string[];
    locations: string[];
  };
  legalConcepts: string[];
  confidence: number;
}

export interface RAGResponse {
  answer: string;
  relevantSections: string[];
  confidence: number;
  sources: string[];
}

export async function analyzeDocument(content: string, fileName: string): Promise<DocumentAnalysis> {
  try {
    const prompt = `Jesteś ekspertem prawnym analizującym dokument: "${fileName}".

Przeanalizuj następujący tekst dokumentu i podaj szczegółową analizę w języku polskim:

${content}

Odpowiedz w formacie JSON z następującymi polami:
{
  "summary": "Streszczenie dokumentu w 2-3 zdaniach",
  "keyPoints": ["Najważniejsze punkty dokumentu jako tablica stringów"],
  "documentType": "Typ dokumentu prawnego (np. umowa, pozew, uchwała)",
  "entities": {
    "people": ["Imiona i nazwiska osób"],
    "organizations": ["Nazwy organizacji, firm, instytucji"],
    "dates": ["Ważne daty w formacie YYYY-MM-DD lub opisowo"],
    "locations": ["Miejsca, adresy, lokalizacje"]
  },
  "legalConcepts": ["Kluczowe pojęcia prawne występujące w dokumencie"],
  "confidence": 0.95
}`;

    const response = await ai.models.generateContent({
      model: "gemini-2.5-pro",
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: "object",
          properties: {
            summary: { type: "string" },
            keyPoints: { type: "array", items: { type: "string" } },
            documentType: { type: "string" },
            entities: {
              type: "object",
              properties: {
                people: { type: "array", items: { type: "string" } },
                organizations: { type: "array", items: { type: "string" } },
                dates: { type: "array", items: { type: "string" } },
                locations: { type: "array", items: { type: "string" } }
              }
            },
            legalConcepts: { type: "array", items: { type: "string" } },
            confidence: { type: "number" }
          },
          required: ["summary", "keyPoints", "documentType", "entities", "legalConcepts", "confidence"]
        }
      },
      contents: prompt,
    });

    const rawJson = response.text;
    if (!rawJson) {
      throw new Error("Empty response from AI model");
    }

    return JSON.parse(rawJson) as DocumentAnalysis;
  } catch (error) {
    console.error("Document analysis failed:", error);
    throw new Error(`Nie udało się przeanalizować dokumentu: ${error}`);
  }
}

export async function askDocumentQuestion(
  documentContent: string, 
  question: string, 
  fileName: string
): Promise<RAGResponse> {
  try {
    const prompt = `Jesteś ekspertem prawnym odpowiadającym na pytania dotyczące dokumentu: "${fileName}".

TREŚĆ DOKUMENTU:
${documentContent}

PYTANIE UŻYTKOWNIKA: ${question}

Odpowiedz na pytanie w oparciu o treść dokumentu. Jeśli odpowiedź nie znajduje się w dokumencie, wyraźnie to zaznacz.

Odpowiedz w formacie JSON:
{
  "answer": "Szczegółowa odpowiedź na pytanie w języku polskim",
  "relevantSections": ["Fragmenty dokumentu odnoszące się do pytania"],
  "confidence": 0.95,
  "sources": ["Konkretne sekcje lub punkty dokumentu, które wspierają odpowiedź"]
}`;

    const response = await ai.models.generateContent({
      model: "gemini-2.5-pro",
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: "object",
          properties: {
            answer: { type: "string" },
            relevantSections: { type: "array", items: { type: "string" } },
            confidence: { type: "number" },
            sources: { type: "array", items: { type: "string" } }
          },
          required: ["answer", "relevantSections", "confidence", "sources"]
        }
      },
      contents: prompt,
    });

    const rawJson = response.text;
    if (!rawJson) {
      throw new Error("Empty response from AI model");
    }

    return JSON.parse(rawJson) as RAGResponse;
  } catch (error) {
    console.error("RAG query failed:", error);
    throw new Error(`Nie udało się odpowiedzieć na pytanie: ${error}`);
  }
}

export async function extractTextFromPDF(buffer: Buffer): Promise<string> {
  // For now, return a placeholder - in production you'd use a PDF parsing library
  // like pdf-parse or pdf2pic + OCR
  return `[PLACEHOLDER] Ekstrakcja tekstu z PDF zostanie zaimplementowana z biblioteką pdf-parse.
  
Na razie możesz testować funkcjonalność RAG z przykładowym tekstem dokumentu.`;
}

export async function generateDocumentSummary(content: string): Promise<string> {
  try {
    const prompt = `Przygotuj zwięzłe streszczenie następującego dokumentu prawnego w języku polskim.
    
Streszczenie powinno zawierać:
- Typ dokumentu
- Główne strony/podmioty
- Kluczowe ustalenia lub postanowienia
- Ważne daty lub terminy

Dokument:
${content}`;

    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: prompt,
    });

    return response.text || "Nie udało się wygenerować streszczenia.";
  } catch (error) {
    console.error("Summary generation failed:", error);
    throw new Error(`Nie udało się wygenerować streszczenia: ${error}`);
  }
}