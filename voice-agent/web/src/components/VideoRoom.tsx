'use client';

import { useState } from 'react';
import {
  LiveKitRoom,
  RoomAudioRenderer,
  ControlBar,
  GridLayout,
  ParticipantTile,
  useTracks,
  PreJoin,
} from '@livekit/components-react';
import '@livekit/components-styles';
import { Track } from 'livekit-client';
import { RecordButton } from './RecordButton';

function VideoGrid() {
  const tracks = useTracks(
    [
      { source: Track.Source.Camera, withPlaceholder: true },
      { source: Track.Source.ScreenShare, withPlaceholder: false },
    ],
    { onlySubscribed: false }
  );

  return (
    <GridLayout
      tracks={tracks}
      style={{ height: 'calc(100vh - 100px)' }}
    >
      <ParticipantTile />
    </GridLayout>
  );
}

interface VideoRoomProps {
  token: string;
  serverUrl: string;
  onDisconnect?: () => void;
}

export function VideoRoom({ token, serverUrl, onDisconnect }: VideoRoomProps) {
  const [preJoinComplete, setPreJoinComplete] = useState(false);

  if (!preJoinComplete) {
    return (
      <div className="h-screen bg-zinc-950" data-lk-theme="default">
        <PreJoin
          onSubmit={() => setPreJoinComplete(true)}
          onError={(err) => console.error('PreJoin error:', err)}
          defaults={{
            videoEnabled: true,
            audioEnabled: true,
          }}
        />
      </div>
    );
  }

  return (
    <LiveKitRoom
      token={token}
      serverUrl={serverUrl}
      connect={true}
      video={true}
      audio={true}
      onDisconnected={onDisconnect}
      data-lk-theme="default"
      style={{ height: '100vh' }}
    >
      <VideoGrid />
      <RoomAudioRenderer />
      <div className="flex items-center justify-center gap-4 p-4">
        <ControlBar variation="minimal" />
        <RecordButton />
      </div>
    </LiveKitRoom>
  );
}
