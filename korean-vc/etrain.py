from encoder.visualizations import Visualizations
from encoder.data_objects import SpeakerVerificationDataLoader, SpeakerVerificationDataset
from encoder.params_model import *
from encoder.model import SpeakerEncoder
from utils.profiler import Profiler
from pathlib import Path
import torch


def sync(device: torch.device):
    if device.type == "cuda":
        torch.cuda.synchronize(device)


def train(run_id: str, clean_data_root: Path, models_dir: Path, umap_every: int, save_every: int,
          backup_every: int, vis_every: int, force_restart: bool, visdom_server: str,
          no_visdom: bool):
    dataset = SpeakerVerificationDataset(clean_data_root)
    loader = SpeakerVerificationDataLoader(
        dataset,
        speakers_per_batch,
        utterances_per_speaker,
        num_workers=8,
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    loss_device = torch.device("cpu")

    model = SpeakerEncoder(device, loss_device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate_init)
    init_step = 1

    state_fpath = models_dir.joinpath(run_id + ".pt")
    backup_dir = models_dir.joinpath(run_id + "_backups")

    if not force_restart:
        if state_fpath.exists():
            print("기존 모델 \"%s\"을(를) 찾았으므로 해당 모델을 로드하고 학습을 재개합니다." % run_id)
            checkpoint = torch.load(state_fpath)
            init_step = checkpoint["step"]
            model.load_state_dict(checkpoint["model_state"])
            optimizer.load_state_dict(checkpoint["optimizer_state"])
            optimizer.param_groups[0]["lr"] = learning_rate_init
        else:
            print("모델 \"%s\"을(를) 찾을 수 없으므로 처음부터 학습을 시작합니다." % run_id)
    else:
        print("처음부터 학습을 시작합니다.")
    model.train()

    vis = Visualizations(run_id, vis_every, server=visdom_server, disabled=no_visdom)
    vis.log_dataset(dataset)
    vis.log_params()
    device_name = str(torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU")
    vis.log_implementation({"Device": device_name})

    profiler = Profiler(summarize_every=10, disabled=False)
    for step, speaker_batch in enumerate(loader, init_step):
        profiler.tick("블로킹, 배치 대기 (스레드)")

        inputs = torch.from_numpy(speaker_batch.data).to(device)
        sync(device)
        profiler.tick("%s로 데이터 이동" % device)
        embeds = model(inputs)
        sync(device)
        profiler.tick("순전파")
        embeds_loss = embeds.view((speakers_per_batch, utterances_per_speaker, -1)).to(loss_device)
        loss, eer = model.loss(embeds_loss)
        sync(loss_device)
        profiler.tick("손실 계산")

        model.zero_grad()
        loss.backward()
        profiler.tick("역전파")
        model.do_gradient_ops()
        optimizer.step()
        profiler.tick("파라미터 업데이트")

        vis.update(loss.item(), eer, step)

        if umap_every != 0 and step % umap_every == 0:
            print("투영 그래프를 그리고 저장 중 (스텝 %d)" % step)
            backup_dir.mkdir(exist_ok=True)
            projection_fpath = backup_dir.joinpath("%s_umap_%06d.png" % (run_id, step))
            embeds = embeds.detach().cpu().numpy()
            vis.draw_projections(embeds, utterances_per_speaker, step, projection_fpath)
            vis.save()

        if save_every != 0 and step % save_every == 0:
            print("모델 저장 중 (스텝 %d)" % step)
            torch.save({
                "step": step + 1,
                "model_state": model.state_dict(),
                "optimizer_state": optimizer.state_dict(),
            }, state_fpath)

        if backup_every != 0 and step % backup_every == 0:
            print("백업 생성 중 (스텝 %d)" % step)
            backup_dir.mkdir(exist_ok=True)
            backup_fpath = backup_dir.joinpath("%s_bak_%06d.pt" % (run_id, step))
            torch.save({
                "step": step + 1,
                "model_state": model.state_dict(),
                "optimizer_state": optimizer.state_dict(),
            }, backup_fpath)

        profiler.tick("기타 (시각화, 저장)")


if __name__ == "__main__":
    run_id = "mu_run"
    clean_data_root = Path("F:/Korean-Voice-Cloning/KsponSpeech/SV2TTS/encoder")
    models_dir = Path("F:/Korean-Voice-Cloning/encoder/saved_models")
    umap_every = 10
    save_every = 50
    backup_every = 100
    vis_every = 200
    force_restart = False
    visdom_server = "http://localhost"
    no_visdom = False

    train(run_id, clean_data_root, models_dir, umap_every, save_every, backup_every, vis_every,
          force_restart, visdom_server, no_visdom)
