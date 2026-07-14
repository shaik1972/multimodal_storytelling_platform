import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const { prompt, format } = await request.json();

  const response = await fetch(`http://localhost:8000/${format}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });

  const data = await response.json();
  return NextResponse.json(data);
}
