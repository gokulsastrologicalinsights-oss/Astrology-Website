import { type NextRequest, NextResponse } from "next/server";

const BACKEND_BASE =
  process.env.BACKEND_INTERNAL_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "http://127.0.0.1:8000";

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
  forwardHeaders["accept"] = request.headers.get("accept") || "application/json";

  try {
    let body: BodyInit | undefined = undefined;
    if (request.method !== "GET" && request.method !== "HEAD" && request.method !== "OPTIONS") {
      body = await request.text();
    }

    const backendRes = await fetch(targetUrl, {
      method: request.method,
      headers: forwardHeaders,
      body,
    });

    const resContentType = backendRes.headers.get("content-type") || "application/json";
    const resBuffer = await backendRes.arrayBuffer();

    return new NextResponse(resBuffer, {
      status: backendRes.status,
      headers: {
        "content-type": resContentType,
      },
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
