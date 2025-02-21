from lightning.pytorch.callbacks import Callback

from tinycmax.visualizer import RerunVisualizer


class LiveVisualizer(Callback):

    is_visualizer = True

    def __init__(self, app_id, server, web, compression, time_window, blueprint=None):
        self.visualizer = RerunVisualizer(app_id, server, web, compression, time_window, blueprint)

    def on_batch_end(self, outputs):
        for output in outputs.values():
            self.visualizer.set_counter()

            # things with events
            for k in [k for k in output.keys() if "events" in k]:
                self.visualizer.event_frame(output[k][0].detach().cpu(), name=k)

            # things with flow
            for k in [k for k in output.keys() if "flow" in k and "raw" not in k]:
                self.visualizer.flow_map(output[k][0].detach().cpu(), name=k)

            # for scalar values
            for k in [k for k in output.keys() if isinstance(output[k], (int, float))]:
                self.visualizer.log_scalar(k, output[k])

    def on_train_batch_end(self, trainer, litmodule, outputs, batch, batch_idx):
        self.on_batch_end(outputs)

    def on_validation_batch_end(self, trainer, litmodule, outputs, batch, batch_idx):
        self.on_batch_end(outputs)
