import { Router } from 'express';
import { analyzeDocument, askDocumentQuestion, generateDocumentSummary } from '../lib/gemini.js';
import { supabase } from '../lib/supabase.js';

const router = Router();

// Analyze document endpoint
router.post('/analyze', async (req, res) => {
  try {
    const { documentPath, fileName } = req.body;

    if (!documentPath || !fileName) {
      return res.status(400).json({ error: 'Document path and filename are required' });
    }

    // Download document from Supabase storage
    const { data: fileData, error: downloadError } = await supabase.storage
      .from('documents-temp')
      .download(documentPath);

    if (downloadError) {
      console.error('Download error:', downloadError);
      return res.status(404).json({ error: 'Document not found' });
    }

    // For demo purposes, use sample legal document text
    // In production, you'd extract text from the actual file
    const sampleLegalText = `
UMOWA NAJMU LOKALU MIESZKALNEGO

zawarta w dniu 15 stycznia 2024 roku w Gdańsku
między:

Wynajmującym: Jan Kowalski, PESEL: 80010112345, zamieszkały w Gdańsku przy ul. Długiej 10/5

a

Najemcą: Anna Nowak, PESEL: 85050567890, zamieszkała w Warszawie przy ul. Królewskiej 25/12

PRZEDMIOT NAJMU:
Mieszkanie dwupokojowe o powierzchni 45 m², położone w Gdańsku przy ul. Morskiej 15/8, składające się z:
- pokoju dziennego (20 m²)
- sypialni (15 m²) 
- kuchni (8 m²)
- łazienki (2 m²)

CZAS NAJMU: od dnia 1 lutego 2024 roku na czas nieokreślony

CZYNSZ: 2500 zł miesięcznie, płatny do 10 dnia każdego miesiąca

KAUCJA: 5000 zł wpłacona przed objęciem lokalu

OBOWIĄZKI STRON:
Wynajmujący zobowiązuje się do:
- przekazania lokalu w stanie nadającym się do zamieszkania
- ponoszenia kosztów remontów kapitałnych

Najemca zobowiązuje się do:
- płacenia czynszu terminowo
- utrzymywania lokalu w dobrym stanie
- ponoszenia kosztów mediów (prąd, gaz, woda)

ROZWIĄZANIE UMOWY możliwe za wypowiedzeniem z miesięcznym okresem wypowiedzenia.

Jan Kowalski                    Anna Nowak
[podpis Wynajmującego]         [podpis Najemcy]
    `;

    // Analyze the document
    const analysis = await analyzeDocument(sampleLegalText, fileName);

    // Store analysis in database (when ready)
    try {
      const { error: dbError } = await supabase
        .from('document_analyses')
        .insert({
          document_path: documentPath,
          file_name: fileName,
          analysis_result: analysis,
          created_at: new Date().toISOString()
        });

      if (dbError) {
        console.log('Database not ready for analysis storage:', dbError.message);
      }
    } catch (dbError) {
      console.log('Database error (expected if not set up):', dbError);
    }

    res.json({
      success: true,
      analysis: analysis
    });

  } catch (error: any) {
    console.error('Document analysis error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Ask question about document
router.post('/ask', async (req, res) => {
  try {
    const { documentPath, question, fileName } = req.body;

    if (!documentPath || !question) {
      return res.status(400).json({ error: 'Document path and question are required' });
    }

    // For demo, use the same sample text
    const sampleLegalText = `
UMOWA NAJMU LOKALU MIESZKALNEGO

zawarta w dniu 15 stycznia 2024 roku w Gdańsku
między:

Wynajmującym: Jan Kowalski, PESEL: 80010112345, zamieszkały w Gdańsku przy ul. Długiej 10/5

a

Najemcą: Anna Nowak, PESEL: 85050567890, zamieszkała w Warszawie przy ul. Królewskiej 25/12

PRZEDMIOT NAJMU:
Mieszkanie dwupokojowe o powierzchni 45 m², położone w Gdańsku przy ul. Morskiej 15/8, składające się z:
- pokoju dziennego (20 m²)
- sypialni (15 m²) 
- kuchni (8 m²)
- łazienki (2 m²)

CZAS NAJMU: od dnia 1 lutego 2024 roku na czas nieokreślony

CZYNSZ: 2500 zł miesięcznie, płatny do 10 dnia każdego miesiąca

KAUCJA: 5000 zł wpłacona przed objęciem lokalu

OBOWIĄZKI STRON:
Wynajmujący zobowiązuje się do:
- przekazania lokalu w stanie nadającym się do zamieszkania
- ponoszenia kosztów remontów kapitałnych

Najemca zobowiązuje się do:
- płacenia czynszu terminowo
- utrzymywania lokalu w dobrym stanie
- ponoszenia kosztów mediów (prąd, gaz, woda)

ROZWIĄZANIE UMOWY możliwe za wypowiedzeniem z miesięcznym okresem wypowiedzenia.

Jan Kowalski                    Anna Nowak
[podpis Wynajmującego]         [podpis Najemcy]
    `;

    const response = await askDocumentQuestion(sampleLegalText, question, fileName || 'document');

    res.json({
      success: true,
      response: response
    });

  } catch (error: any) {
    console.error('RAG query error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Generate document summary
router.post('/summarize', async (req, res) => {
  try {
    const { documentPath, fileName } = req.body;

    if (!documentPath) {
      return res.status(400).json({ error: 'Document path is required' });
    }

    // Use sample text for demo
    const sampleLegalText = `
UMOWA NAJMU LOKALU MIESZKALNEGO

zawarta w dniu 15 stycznia 2024 roku w Gdańsku
między:

Wynajmującym: Jan Kowalski, PESEL: 80010112345, zamieszkały w Gdańsku przy ul. Długiej 10/5

a

Najemcą: Anna Nowak, PESEL: 85050567890, zamieszkała w Warszawie przy ul. Królewskiej 25/12

PRZEDMIOT NAJMU:
Mieszkanie dwupokojowe o powierzchni 45 m², położone w Gdańsku przy ul. Morskiej 15/8

CZAS NAJMU: od dnia 1 lutego 2024 roku na czas nieokreślony

CZYNSZ: 2500 zł miesięcznie, płatny do 10 dnia każdego miesiąca

KAUCJA: 5000 zł wpłacona przed objęciem lokalu
    `;

    const summary = await generateDocumentSummary(sampleLegalText);

    res.json({
      success: true,
      summary: summary
    });

  } catch (error: any) {
    console.error('Summary generation error:', error);
    res.status(500).json({ error: error.message });
  }
});

export default router;