import io
from pathlib import Path
import shutil

import numpy as np
from PIL import Image
import rerun as rr

from tinycmax.visualizer_utils import event_frame_to_image, flow_map_to_image


class RerunVisualizer:
    """
    Live visualizer using Rerun.
    """

    def __init__(self, app_id, log_dir, server, mode, compression, time_window, blueprint):
        rr.init(app_id)
        if mode == "connect":
            rr.connect_tcp(server)
        elif mode == "serve":
            rr.serve_web()
        elif mode == "save":
            log_dir = Path(log_dir)
            log_dir.mkdir(exist_ok=True, parents=True)
            rr.save(log_dir / f"{app_id}.rrd")
        else:
            raise ValueError(f"Unknown mode: {mode}")

        self.compression = compression
        self.counter = 0
        self.time_window = time_window / 1e6
        if blueprint is not None:
            self.blueprint = blueprint
            rr.send_blueprint(self.blueprint, make_active=True)

    def set_counter(self):
        rr.set_time_seconds("time", self.counter * self.time_window)
        self.counter += 1

    def event_frame(self, frame, name="events"):
        image = event_frame_to_image(frame)
        self.log_image(name, image, self.compression)

    def flow_map(self, frame, name="flow"):
        image = flow_map_to_image(frame)
        self.log_image(name, image, self.compression)

    def scalar(self, name, scalar):
        self.log_scalar(name, scalar)

    @staticmethod
    def log_image(name, image_ndarray, compression=False):
        # compression: none/false, jpeg, png
        if compression:
            with io.BytesIO() as output:
                Image.fromarray(image_ndarray).save(output, format=compression)
                media_type = f"image/{compression.lower()}"
                rr.log(name, rr.EncodedImage(contents=output.getvalue(), media_type=media_type))
        else:
            rr.log(name, rr.Image(image_ndarray))

    @staticmethod
    def log_scalar(name, scalar):
        rr.log(name, rr.Scalar(scalar))


class FileVisualizer:
    def __init__(self, root_dir, names, image_format, time_window):
        self.root_dir = Path(root_dir)
        self.image_format = image_format
        self.time_window = time_window / 1e6
        shutil.rmtree(self.root_dir) if self.root_dir.exists() else None
        for name in names:
            (self.root_dir / name).mkdir(exist_ok=True, parents=True)

        self.counter = 0
        self.time = 0

    def set_counter(self):
        self.counter += 1
        self.time = self.counter * self.time_window

    def event_frame(self, frame, name="events"):
        image = event_frame_to_image(frame)
        self.save_image(name, image)

    def flow_map(self, frame, name="flow"):
        image = flow_map_to_image(frame)
        self.save_image(name, image)

    def ndarray(self, ndarray, name="raw"):
        self.save_ndarray(ndarray, name)

    def scalar(self, name, scalar):
        if (self.root_dir / name).exists():
            with open(self.root_dir / name / "data.csv", "a") as f:
                f.write(f"{self.counter:05d},{self.time},{','.join([str(s) for s in scalar])}\n")

    def save_image(self, name, image):
        if (self.root_dir / name).exists():
            image = Image.fromarray(image)
            image.save(self.root_dir / name / f"{self.counter:05d}.{self.format}")

    def save_ndarray(self, ndarray, name):
        if (self.root_dir / name).exists():
            np.save(self.root_dir / name / f"{self.counter:05d}.npy", ndarray)
