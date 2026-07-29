import { NextResponse } from "next/server";

// Routes video edit requests to the correct FastAPI endpoint:
// POST /api/video-edit  { endpoint: "trim"|"overlay"|"transition", videoUrl, ...params }

export async function POST(request: Request) {
  const { endpoint, ...body } = await request.json();

  const allowed = ["trim", "overlay", "transition"];
  if (!allowed.includes(endpoint)) {
    return NextResponse.json({ error: "Unknown edit endpoint" }, { status: 400 });
  }

  const response = await fetch(`http://localhost:8000/video/${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  const data = await response.json();
  return NextResponse.json(data, { status: response.status });
}
