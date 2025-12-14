import { EgressClient, EncodedFileOutput, EncodedFileType, S3Upload } from 'livekit-server-sdk';
import { NextResponse } from 'next/server';
import { config } from 'dotenv';
import { resolve } from 'path';

// Load env from parent directory
config({ path: resolve(process.cwd(), '..', '.env') });

const getEgressClient = () => {
  const host = process.env.LIVEKIT_URL;
  const apiKey = process.env.LIVEKIT_API_KEY;
  const apiSecret = process.env.LIVEKIT_API_SECRET;

  if (!host || !apiKey || !apiSecret) {
    throw new Error('LiveKit credentials not configured');
  }

  // Convert wss:// to https:// for REST API
  const httpHost = host.replace('wss://', 'https://').replace('ws://', 'http://');

  return new EgressClient(httpHost, apiKey, apiSecret);
};

// Start recording
export async function POST(request: Request) {
  try {
    const { room } = await request.json();

    if (!room) {
      return NextResponse.json({ error: 'Room name required' }, { status: 400 });
    }

    // Check R2 credentials
    const r2AccessKey = process.env.R2_ACCESS_KEY_ID;
    const r2SecretKey = process.env.R2_SECRET_ACCESS_KEY;
    const r2Bucket = process.env.R2_BUCKET;
    const r2AccountId = process.env.R2_ACCOUNT_ID;

    if (!r2AccessKey || !r2SecretKey || !r2Bucket || !r2AccountId) {
      return NextResponse.json({ error: 'R2 storage not configured' }, { status: 500 });
    }

    const client = getEgressClient();

    // Configure R2 upload (S3-compatible)
    const s3Upload = new S3Upload({
      accessKey: r2AccessKey,
      secret: r2SecretKey,
      bucket: r2Bucket,
      endpoint: `https://${r2AccountId}.r2.cloudflarestorage.com`,
      forcePathStyle: true,
    });

    // Start room composite egress - records all participants
    const output = new EncodedFileOutput({
      fileType: EncodedFileType.MP4,
      filepath: `recordings/${room}-${Date.now()}.mp4`,
      output: { case: 's3', value: s3Upload },
    });

    const egress = await client.startRoomCompositeEgress(room, { file: output }, {
      layout: 'grid-dark',
      audioOnly: false,
    });

    return NextResponse.json({
      success: true,
      egressId: egress.egressId,
      status: egress.status,
    });
  } catch (error) {
    console.error('Failed to start recording:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to start recording' },
      { status: 500 }
    );
  }
}

// Stop recording
export async function DELETE(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const egressId = searchParams.get('egressId');

    if (!egressId) {
      return NextResponse.json({ error: 'Egress ID required' }, { status: 400 });
    }

    const client = getEgressClient();

    // First check egress status
    const egresses = await client.listEgress({ egressId });
    const currentEgress = egresses[0];

    // Status 4 = EGRESS_FAILED, Status 5 = EGRESS_ENDED
    if (currentEgress && (currentEgress.status === 4 || currentEgress.status === 5)) {
      return NextResponse.json({
        success: true,
        egressId: currentEgress.egressId,
        status: currentEgress.status,
        message: currentEgress.status === 4 ? 'Recording failed' : 'Recording already ended',
        error: currentEgress.error || undefined,
      });
    }

    const egress = await client.stopEgress(egressId);

    return NextResponse.json({
      success: true,
      egressId: egress.egressId,
      status: egress.status,
    });
  } catch (error) {
    console.error('Failed to stop recording:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to stop recording' },
      { status: 500 }
    );
  }
}

// Get recording status
export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const room = searchParams.get('room');

    if (!room) {
      return NextResponse.json({ error: 'Room name required' }, { status: 400 });
    }

    const client = getEgressClient();
    const egresses = await client.listEgress({ roomName: room });

    // Find active recordings
    const activeRecordings = egresses.filter(
      (e) => e.status === 0 || e.status === 1 // EGRESS_STARTING or EGRESS_ACTIVE
    );

    return NextResponse.json({
      isRecording: activeRecordings.length > 0,
      activeEgress: activeRecordings[0] || null,
    });
  } catch (error) {
    console.error('Failed to get recording status:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to get status' },
      { status: 500 }
    );
  }
}
