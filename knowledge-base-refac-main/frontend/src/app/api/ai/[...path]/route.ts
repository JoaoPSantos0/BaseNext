import { NextRequest, NextResponse } from 'next/server';

const FASTAPI_URL = process.env.FASTAPI_URL || 'http://127.0.0.1:8000';
const FASTAPI_API_KEY = process.env.FASTAPI_API_KEY || '';

async function proxyToFastAPI(request: NextRequest): Promise<NextResponse> {
  const url = `${FASTAPI_URL}/auth/query`;

  // Monta headers iguais ao curl
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    'X-API-Key': FASTAPI_API_KEY,
    Accept: 'application/json',
  };

  // Transforma o body vindo do frontend para { pergunta: ... }
  let body: string | undefined;
  if (request.method !== 'GET') {
    try {
      const originalBody = await request.json();
      // Se vier { question: "..."} converte para { pergunta: "..." }
      const pergunta =
        originalBody.pergunta ??
        originalBody.question ??
        originalBody.q ??
        '';
      body = JSON.stringify({ pergunta });
    } catch (err) {
      return NextResponse.json(
        { error: 'Invalid JSON body' },
        { status: 400 }
      );
    }
  }

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers,
      body,
    });

    const text = await response.text();

    if (!response.ok) {
      return NextResponse.json(
        { error: 'FastAPI error', details: text },
        { status: response.status }
      );
    }

    // Repassa a resposta do FastAPI direto para o cliente
    return new NextResponse(text, {
      status: response.status,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (err) {
    return NextResponse.json(
      { error: 'Failed to connect to FastAPI', details: String(err) },
      { status: 502 }
    );
  }
}

// Next.js handlers
export async function POST(req: NextRequest) {
  return proxyToFastAPI(req);
}
export async function GET() {
  return NextResponse.json({ error: 'GET not supported' }, { status: 405 });
}
