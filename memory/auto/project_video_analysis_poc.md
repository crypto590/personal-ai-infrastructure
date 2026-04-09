---
name: project_video_analysis_poc
description: Video analysis pipeline PoC — Gemma 4 + YOLO + VballNet + Falcon Perception for volleyball analytics (BallTime competitor)
type: project
---

Video analysis pipeline for automated volleyball analytics, targeting BallTime/Hudl Assist feature parity.

**Why:** Competitive moat — nobody in recruiting space does VLM-orchestrated video analysis yet. Turns livestream recordings into actionable coaching data.

**How to apply:** Worktree `video-analysis-poc`, code in `experiments/video-analysis/`. Videos uploaded to `athleadsandbox7cx3zwozfa/video-analysis-poc/recordings/` (6 files, 6.5GB).

**Current stack (local M1 Max 32GB):**
- YOLO11x + ByteTrack: player detection/tracking (8+ players, 6 FPS)
- YOLO11x-pose: skeleton keypoints (jump height, swing speed)
- VballNet ONNX: volleyball ball tracking (36% detection, 13ms/frame)
- Gemma 4 E4B (mlx-vlm): scene understanding, jersey OCR (#5, #12, #02), score reading
- Falcon Perception: text-prompted player segmentation with masks
- Rally detection from ball presence gaps (80% play / 20% dead time)

**BallTime was acquired by Hudl** (Feb 2025) → now "Hudl Assist powered by Balltime AI"

**Azure GPU (A100) blocked:** Sponsorship subscription has zero GPU quota for all NC families. Need quota request (1-3 business days) or use RunPod ($0.74/hr).

**Key open-source resources identified:**
- `masouduut94/volleyball_analytics` (MIT): VideoMAE game state, YOLOv8 action detection, FastAPI backend
- `masouduut94/volleyball-ml-models`: ML manager with ball/action/court/game-state modules
- `shukkkur/VolleyVision`: 25k ball images, 14k action images, court segmentation datasets on Roboflow Universe
- `asigatchov/vball-net`: Volleyball-specific ball tracking (TrackNetV4 derivative), 271 FPS on CPU
- Pre-trained VolleyVision weights don't work on our club footage (trained on broadcast angles)

**Key learning:** Local YOLO training on M1 Max with imgsz=1280 hangs after ~25 min due to MPS stalls + memory pressure (32GB maxed). Ball training reached 96.9% mAP50 in logs but `best.pt` was never written. For any real training, use GPU (Azure/RunPod) not local MPS.

**Gemini 2.5 Pro works great as the "brain" tier:**
- Reads jersey numbers on BOTH teams (found #1, #4, #5, #7, #10, #12, #13 across frames)
- Reads scoreboards correctly (including team names like "TAV 14 Black")
- Classifies actions natively (serve, rally, timeout, etc.)
- Handles native video input (5s clips)
- ~$1.50-3.60 per game with 2.5 Pro, 4x cheaper with Flash
- Free tier covers all PoC testing
- Stored at `/Users/coreyyoung/Desktop/Projects/athlead/.env` as `GEMINI_API_KEY` (or was `AIzaSyDxchoQsqpGSv3SzE-qKhBhDZbUIZt3jx4` - rotate before commit)

**Next steps:**
1. Polish visualize_gemini.py — better jersey-to-trackID matching (currently position-based, weak)
2. Request Azure A100 quota (blocked: zero GPU quota on sponsorship sub) or use RunPod for training
3. Add court keypoint detection for px→meter calibration (speed, distance stats)
4. Skip custom YOLO training for PoC — Gemini handles ball + action natively
5. iOS Vision framework for real-time on-device analysis (Phase 4)

**Roboflow datasets downloaded (11k+ images):**
- `datasets/volleyball_ball/` — 521 images, 1 class
- `datasets/volleyball_actions/` — 11,019 images, 5 classes (block/defense/serve/set/spike)
