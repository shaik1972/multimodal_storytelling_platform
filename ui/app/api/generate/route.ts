import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const { prompt, format, voice, speed } = await request.json();

  let response: Response;
  try {
    response = await fetch(`http://localhost:8000/${format}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt, voice, speed }),
    });
  } catch {
    return NextResponse.json(
      { error: "Could not reach the backend. Is uvicorn running on port 8000?" },
      { status: 502 },
    );
  }

  if (!response.ok) {
    const text = await response.text();
    return NextResponse.json(
      { error: `Backend error ${response.status}: ${text}` },
      { status: response.status },
    );
  }

  const data = await response.json();
  return NextResponse.json(data);
}
