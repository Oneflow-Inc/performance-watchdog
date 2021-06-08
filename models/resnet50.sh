set -ex

benchmark_dir=${ONEFLOW_BENCHMARK_DIR:-"$PWD"}
gpu_num_per_node=${ONEFLOW_BENCHMARK_GPU_NUM_PER_NODE:-1}
cd $benchmark_dir/Classification/cnns

rm -rf core.*
rm -rf ./output

export PYTHONUNBUFFERED=1
export NCCL_LAUNCH_MODE=PARALLEL

vram_size=$(nvidia-smi --query-gpu="memory.total" --id=0 --format=csv,noheader,nounits)

if (( ${vram_size} > 8000 )); then
    batch_size_per_device=72
fi

if (( ${vram_size} > 16000 )); then
    batch_size_per_device=144
fi

DATA_ROOT=/dataset/ImageNet/ofrecord
iter_num=20
python3 of_cnn_train_val.py \
     --train_data_dir=$DATA_ROOT/train \
     --train_data_part_num=256 \
     --val_data_dir=$DATA_ROOT/validation \
     --val_data_part_num=256 \
     --num_nodes=1 \
     --gpu_num_per_node=${gpu_num_per_node} \
     --optimizer="sgd" \
     --momentum=0.875 \
     --label_smoothing=0.1 \
     --learning_rate=0.768 \
     --loss_print_every_n_iter=1 \
     --batch_size_per_device=${batch_size_per_device} \
     --val_batch_size_per_device=50 \
     --channel_last=False \
     --fuse_bn_relu=True \
     --fuse_bn_add_relu=True \
     --nccl_fusion_threshold_mb=16 \
     --nccl_fusion_max_ops=24 \
     --gpu_image_decoder=True \
     --num_epoch=1 \
     --model="resnet50" \
     --num_examples="$(($batch_size_per_device * $gpu_num_per_node * iter_num))"
