import { type NextRequest, NextResponse } from "next/server";

export const maxDuration = 60;

const BACKEND_BASE =
  process.env.BACKEND_INTERNAL_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "http://127.0.0.1:8000";

// Hop-by-hop headers that should not be forwarded by a reverse proxy
const HOP_BY_HOP_HEADERS = new Set([
  "connection",
  "keep-alive",
  "proxy-authenticate",
  "proxy-authorization",
  "te",
  "trailer",
  "transfer-encoding",
  "upgrade",
]);

async function proxyRequest(request: NextRequest, pathSegments: string[]) {
  const subpath = pathSegments.join("/");
  const search = request.nextUrl.search;
  const targetUrl = `${BACKEND_BASE.replace(/\/$/, "")}/api/v1/${subpath}${search}`;

  const forwardHeaders: Record<string, string> = {};
  const authHeader = request.headers.get("authorization");
  if (authHeader) {
    forwardHeaders["authorization"] = authHeader;
  }
  const contentType = request.headers.get("content-type");
  if (contentType) {
    forwardHeaders["content-type"] = contentType;
  }
  forwardHeaders["accept"] = request.headers.get("accept") || "*/*";

  try {
    let body: BodyInit | undefined = undefined;
    if (request.method !== "GET" && request.method !== "HEAD" && request.method !== "OPTIONS") {
      // Use arrayBuffer to prevent UTF-8 text decoding corruption of binary or multipart payloads
      const buffer = await request.arrayBuffer();
      if (buffer.byteLength > 0) {
        body = buffer;
      }
    }

    const backendRes = await fetch(targetUrl, {
      method: request.method,
      headers: forwardHeaders,
      body,
    });

    const responseHeaders = new Headers();
    backendRes.headers.forEach((val, key) => {
      if (!HOP_BY_HOP_HEADERS.has(key.toLowerCase())) {
        responseHeaders.set(key, val);
      }
    });

    if (!responseHeaders.has("content-type")) {
      responseHeaders.set("content-type", "application/json");
    }

    // Direct binary stream piping preserves chunked downloads (e.g. 9-page PDF reports) without buffer corruption
    return new NextResponse(backendRes.body, {
      status: backendRes.status,
      statusText: backendRes.statusText,
      headers: responseHeaders,
    });
  } catch (err: any) {
    console.error(`[API Proxy Error] Failed to reach backend at ${targetUrl}:`, err?.message || err);
    return NextResponse.json(
      {
        error: "Backend Unavailable",
        detail: `Failed to connect to astrology calculation backend at ${BACKEND_BASE}. Please ensure the FastAPI server is running.`,
      },
      { status: 503 }
    );
  }
}

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path);
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path);
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path);
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path);
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path);
}
