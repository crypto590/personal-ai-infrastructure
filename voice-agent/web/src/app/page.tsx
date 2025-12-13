'use client';

import { useState, useCallback } from 'react';
import { VideoRoom } from '@/components/VideoRoom';

interface ConnectionState {
  token: string;
  serverUrl: string;
}

export default function Home() {
  const [connection, setConnection] = useState<ConnectionState | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const connect = useCallback(async () => {
    setIsConnecting(true);
    setError(null);

    try {
      const response = await fetch('/api/token');
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to get token');
      }

      setConnection({
        token: data.token,
        serverUrl: data.serverUrl,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Connection failed');
    } finally {
      setIsConnecting(false);
    }
  }, []);

  const disconnect = useCallback(() => {
    setConnection(null);
  }, []);

  if (connection) {
    return (
      <VideoRoom
        token={connection.token}
        serverUrl={connection.serverUrl}
        onDisconnect={disconnect}
      />
    );
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-zinc-950 p-8">
      <div className="flex flex-col items-center gap-8 text-center">
        <div className="flex flex-col gap-2">
          <h1 className="text-4xl font-bold text-white">Alex</h1>
          <p className="text-zinc-400">Vision-enabled voice assistant</p>
        </div>

        {error && (
          <div className="rounded-lg bg-red-500/10 px-4 py-2 text-red-400">
            {error}
          </div>
        )}

        <button
          onClick={connect}
          disabled={isConnecting}
          className="flex h-14 items-center justify-center gap-2 rounded-full bg-white px-8 text-lg font-medium text-black transition-all hover:bg-zinc-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isConnecting ? (
            <>
              <span className="h-5 w-5 animate-spin rounded-full border-2 border-zinc-400 border-t-black" />
              Connecting...
            </>
          ) : (
            'Start Conversation'
          )}
        </button>

        <p className="max-w-md text-sm text-zinc-500">
          Grant camera and microphone access to have a real-time conversation with Alex.
        </p>
      </div>
    </div>
  );
}
