# TinyCMax

|   Warping  |                             Events, flow, accumulated events, image of warped events       |
|-----------|:--------------------------------------------------------------------:|
|   Linear   | <img src="assets/linear.gif" alt="linear" style="display: block; margin: 0 auto;"> |
| Iterative  | <img src="assets/iterative.gif" alt="iterative" style="display: block; margin: 0 auto;"> |

Minimal implementation of the contrast maximization (CMax) framework for self-supervised learning (SSL) from events. Related publications:

1. [Self-Supervised Learning of Event-Based Optical Flow with Spiking Neural Networks](https://proceedings.neurips.cc/paper/2021/hash/39d4b545fb02556829aab1db805021c3-Abstract.html)
    - Sequential pipeline with recurrent spiking networks
    - CMax assuming linear motion within the deblurring window
2. [Taming Contrast Maximization for Learning Sequential, Low-latency, Event-based Optical Flow](https://openaccess.thecvf.com/content/ICCV2023/html/Paredes-Valles_Taming_Contrast_Maximization_for_Learning_Sequential_Low-latency_Event-based_Optical_Flow_ICCV_2023_paper.html)
    - Sequential pipeline with recurrent networks
    - Multi-reference, multi-scale CMax with iterative warping, allowing for non-linear motion

In this repo, we implement CMax with both linear and iterative warping, and train a simple ConvGRU network in a sequential setting on the [UZH-FPV](https://fpv.ifi.uzh.ch/) dataset.

Training curves and trained model checkpoints can be found on [Weights & Biases](https://wandb.ai/huizerd/tinycmax).

## Installation

Requires a NVIDIA GPU to run due to CUDA dependencies.

```
git clone --recurse-submodules git@github.com:Huizerd/tinycmax.git && cd tinycmax
conda env create -f env.yaml && conda activate tinycmax && pre-commit install
```

## Usage

### Downloading and formatting UZH-FPV
```
python tinycmax/uzh_fpv.py 
```

### Visualizing events in Rerun
```
python show.py
```

### Training
```
python train.py
```
- Logging to Weights & Biases:
    - Follow the [quickstart](https://docs.wandb.ai/quickstart/): sign up and run `wandb login` in the command line
    - Check you have a `logs` folder in repo root
    - Run command with `logger=wandb logger.notes="some notes"` added
- Visualize in Rerun:
    - Run command with `+callbacks=live_vis` added
    - Live visualization:
        - Run `rerun` in separate window (with environment activated)
        - Set IP (e.g. `server=127.0.0.1:9876`) in [`live_vis.yaml`](config/callbacks/live_vis.yaml)
    - Save to file:
        - Set `mode=save` in [`live_vis.yaml`](config/callbacks/live_vis.yaml) to log to an `.rrd` file
        - Download file, then open in Rerun locally to visualize

### Validation
```
python validate.py runid=<run_id>
```
- Run selection:
    - Get `run_id` from Weights & Biases (e.g. `eio65zrj`)
    - Add `checkpoint=<checkpoint_id>` to select specific checkpoint (e.g. `latest` (default) or `v0`, `v1`, etc.)
    - To use a pre-trained model, leave [`wandb.yaml`](config/logger/wandb.yaml) as-is and provide a `run_id` and `checkpoind_id` from our [Weights & Biases](https://wandb.ai/huizerd/tinycmax)
- Visualize in Rerun: same as above

### Generating videos
```
python validate.py runid=rb5gp4fv +callbacks=file_log +datamodule.val_recordings="[[indoor_forward_11_davis,[53e6,63e6]]]"
```

## To do

- Better unify warp modes (with both PyTorch and CUDA implementations to allow CPU)
- Implement fixed event count frames
- (Add DSEC)
- (Add smoothing loss)
