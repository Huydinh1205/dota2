from __future__ import annotations
import cv2
import os

def frames_to_video(input_folder="game_frames", output_video="output.mp4", fps=30):
    """
    Convert a sequence of image frames into a video file.

    Args:
        input_folder (str): Folder containing the frame images.
        output_video (str): Output video file name (e.g., output.mp4).
        fps (int): Frames per second for the output video.
    """
    # Get all frame files and sort them
    frames = sorted(
        [f for f in os.listdir(input_folder) if f.endswith(".jpg")]
    )
    if not frames:
        print("❌ No frame images found in the folder.")
        return

    # Read the first frame to determine video resolution
    first_frame = cv2.imread(os.path.join(input_folder, frames[0]))
    height, width, _ = first_frame.shape

    # Create the video writer
    out = cv2.VideoWriter(
        output_video,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height)
    )

    # Write each frame to the video
    for i, frame_name in enumerate(frames):
        frame_path = os.path.join(input_folder, frame_name)
        frame = cv2.imread(frame_path)
        out.write(frame)
        if i % 100 == 0:
            print(f"🧩 Processed {i}/{len(frames)} frames...")

    out.release()
    print(f"✅ Video export complete: {output_video}")

if __name__ == "__main__":
    frames_to_video("game_frames", "output.mp4", fps=30)
