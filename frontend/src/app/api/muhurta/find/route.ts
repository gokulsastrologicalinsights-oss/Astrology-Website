import { NextResponse, type NextRequest } from "next/server";
import { findMuhurtas } from "@/lib/api";

export async function POST(request: NextRequest) {
  try {
    const payload = await request.json();
    const data = await findMuhurtas(payload);
    return NextResponse.json(data);
  } catch (err: any) {
    return NextResponse.json(
      { error: err?.message || "Failed to search candidate Muhurtas." },
      { status: 500 }
    );
  }
}
