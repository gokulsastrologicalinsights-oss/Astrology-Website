import { NextResponse, type NextRequest } from "next/server";
import { getDailyPanchang } from "@/lib/api";

export async function POST(request: NextRequest) {
  try {
    const payload = await request.json();
    const data = await getDailyPanchang(payload);
    return NextResponse.json(data);
  } catch (err: any) {
    return NextResponse.json(
      { error: err?.message || "Failed to calculate daily Panchangam." },
      { status: 500 }
    );
  }
}
