'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRoomContext } from '@livekit/components-react';

export function RecordButton() {
  const room = useRoomContext();
  const [isRecording, setIsRecording] = useState(false);
  const [egressId, setEgressId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Check recording status on mount
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const res = await fetch(`/api/recording?room=${room.name}`);
        const data = await res.json();
        if (data.isRecording && data.activeEgress) {
          setIsRecording(true);
          setEgressId(data.activeEgress.egressId);
        }
      } catch (err) {
        console.error('Failed to check recording status:', err);
      }
    };
    checkStatus();
  }, [room.name]);

  const toggleRecording = useCallback(async () => {
    setIsLoading(true);
    try {
      if (isRecording && egressId) {
        // Stop recording
        const res = await fetch(`/api/recording?egressId=${egressId}`, {
          method: 'DELETE',
        });
        const data = await res.json();
        setIsRecording(false);
        setEgressId(null);
        if (data.message) {
          alert(data.message);
        }
      } else {
        // Start recording
        const res = await fetch('/api/recording', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ room: room.name }),
        });
        const data = await res.json();
        if (res.ok && data.egressId) {
          setIsRecording(true);
          setEgressId(data.egressId);
        } else if (data.error) {
          console.error('Recording error:', data.error);
          alert(data.error);
        }
      }
    } catch (err) {
      console.error('Recording toggle failed:', err);
    } finally {
      setIsLoading(false);
    }
  }, [isRecording, egressId, room.name]);

  return (
    <button
      onClick={toggleRecording}
      disabled={isLoading}
      className={`
        flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all
        ${isRecording
          ? 'bg-red-600 hover:bg-red-700 text-white'
          : 'bg-zinc-800 hover:bg-zinc-700 text-zinc-200'
        }
        ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}
      `}
      title={isRecording ? 'Stop Recording' : 'Start Recording'}
    >
      {/* Recording indicator dot */}
      <span
        className={`
          w-3 h-3 rounded-full
          ${isRecording ? 'bg-white animate-pulse' : 'bg-red-500'}
        `}
      />
      <span>{isLoading ? 'Loading...' : isRecording ? 'Stop' : 'Record'}</span>
    </button>
  );
}
