import { NextRequest, NextResponse } from 'next/server';

const FASTAPI_URL = process.env.FASTAPI_URL || 'http://127.0.0.1:8000';
const FASTAPI_API_KEY = process.env.FASTAPI_API_KEY || '';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json().catch(() => ({}));
    const pergunta = body.pergunta?.toString() || '';
    console.log('💡 DEBUG: pergunta recebida no route.ts:', pergunta);

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    if (FASTAPI_API_KEY) headers['x-api-key'] = FASTAPI_API_KEY;

    const response = await fetch(`${FASTAPI_URL}/auth/query`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ pergunta }),
    });

    const text = await response.text();
    console.log('💡 DEBUG: body raw recebido da FastAPI:', text);

    let data: any = {};
    try {
      data = JSON.parse(text);
    } catch {
      data = { message: text.trim() };
    }

    // ⚠️ AQUI está a correção definitiva
    const mappedResponse = {
      answer: data.detail ?? data.message ?? '>>> DEBUG: Sem resposta <<<',
      sources: [],
      tokens_used: 0,
      processing_time: 0,
      search_time: 0,
      generation_time: 0,
    };

    console.log('💡 DEBUG FINAL: mappedResponse:', mappedResponse);

    return NextResponse.json(mappedResponse);
  } catch (error) {
    console.error('💥 Erro no route.ts:', error);
    return NextResponse.json(
      {
        error: 'Falha ao processar a requisição',
        details: error instanceof Error ? error.message : String(error),
      },
      { status: 500 }
    );
  }
}
