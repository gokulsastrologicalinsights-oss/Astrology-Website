import { NextResponse, type NextRequest } from "next/server";
import { calculatePanchaPakshi } from "@/lib/api";

export async function POST(request: NextRequest) {
  try {
    const payload = await request.json();
    const data = await calculatePanchaPakshi(payload);
    return NextResponse.json(data);
  } catch (err: any) {
    return NextResponse.json(
      { error: err?.message || "Failed to calculate Pancha Pakshi bio-rhythms." },
      { status: 500 }
    );
  }
}
