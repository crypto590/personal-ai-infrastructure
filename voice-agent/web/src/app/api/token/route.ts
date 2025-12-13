import { AccessToken } from 'livekit-server-sdk';
import { NextResponse } from 'next/server';
import { config } from 'dotenv';
import { resolve } from 'path';

// Load env from parent directory
config({ path: resolve(process.cwd(), '..', '.env') });

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const room = searchParams.get('room') || 'voice-agent';
  const username = searchParams.get('username') || `user-${Math.random().toString(36).slice(2, 7)}`;

  const apiKey = process.env.LIVEKIT_API_KEY;
  const apiSecret = process.env.LIVEKIT_API_SECRET;

  if (!apiKey || !apiSecret) {
    return NextResponse.json(
      { error: 'LiveKit credentials not configured' },
      { status: 500 }
    );
  }

  const token = new AccessToken(apiKey, apiSecret, {
    identity: username,
    ttl: '1h',
  });

  token.addGrant({
    roomJoin: true,
    room,
    canPublish: true,
    canSubscribe: true,
    canPublishData: true,
  });

  const jwt = await token.toJwt();

  return NextResponse.json({
    token: jwt,
    room,
    username,
    serverUrl: process.env.LIVEKIT_URL,
  });
}
