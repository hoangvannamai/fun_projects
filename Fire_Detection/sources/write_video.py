import cv2

def write_video(frames, fps, output_file):
    height, width, _ = frames[0].shape
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output = cv2.VideoWriter(output_file, fourcc, fps, (width, height))
    for frame in frames:
        frame = frame[:, :, ::-1]
        output.write(frame)

    output.release()