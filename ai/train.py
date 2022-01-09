import os
import json

import numpy as np
import pandas as pd
import torch
import pytorch_lightning as pl
from pytorch_lightning.callbacks import EarlyStopping # ,LearningRateMonitor

from pytorch_forecasting import Baseline, NBeats, TimeSeriesDataSet #,TemporalFusionTransformer
from pytorch_forecasting.data import NaNLabelEncoder #, GroupNormalizer
from predict import StockPredictionService


class BaseParameter:
    def __init__(self):
        self.batch_size:int = 4
        self.n_loader_worker:int = 2
        self.max_epoch:int = 100
        self.patience:int = 15
        self.lr:float = 4e-3

def preprocessing_data(data:dict):

    df = pd.read_json(data, orient="key")
    df["date"] = pd.to_datetime(df["date"])

    new_df = df.copy()
    new_df["group"] = 1
    new_df["time_idx"] = range(new_df.shape[0])
    # new_df["dayofweek"] = list(map(str, new_df['date'].dt.dayofweek))
    new_df = new_df.astype({"last_price":"float"}) 
    return new_df[["last_price", "group", "time_idx"]]

def set_loaders(new_df:pd.DataFrame, config:dict, params:BaseParameter):

    context_length = config["input_window"]
    prediction_length = config["output_window"]
    print((context_length, prediction_length))

    training_cutoff = new_df["time_idx"].max() - prediction_length
    training = TimeSeriesDataSet(
        new_df[lambda x: x.time_idx < training_cutoff],
        time_idx="time_idx",
        target="last_price",
        categorical_encoders={"group": NaNLabelEncoder().fit(new_df.group)},
        group_ids=["group"],
        time_varying_unknown_reals=["last_price"], #["last_price", "start_price","high_price", "low_price", "volume"],
        max_encoder_length=context_length,
        max_prediction_length=prediction_length,
        allow_missing_timesteps=True,
        add_target_scales=False,
    )

    validation = TimeSeriesDataSet.from_dataset(training, new_df, min_prediction_idx=training_cutoff)
    train_loader = training.to_dataloader(train=True, batch_size=params.batch_size, num_workers=params.n_loader_worker)
    val_loader = validation.to_dataloader(train=False, batch_size=params.batch_size, num_workers=params.n_loader_worker)

    return train_loader, val_loader, training_tsdset

def nbeats_train(new_df:pd.DataFrame, config:dict, params:BaseParameter):

    train_loader, val_loader, training_tsdset = set_loaders(new_df, config, params)
    early_stop_callback = EarlyStopping(
        monitor="val_loss", min_delta=1e-4, patience=params.patience, verbose=False, mode="min"
        )
    trainer = pl.Trainer(
        max_epochs=params.max_epoch,
        gpus=0,
        gradient_clip_val=0.1,
        weights_summary="top",
        callbacks=[early_stop_callback],
        limit_train_batches=15,
    )

    net = NBeats.from_dataset(
        training_tsdset, 
        learning_rate=params.lr, 
        log_interval=10, 
        log_val_interval=1, 
        log_gradient_flow=False, 
        weight_decay=1e-2, 
        backcast_loss_ratio=1.0,
    )
    print(f"Number of parameters in network: {net.size()/1e3:.1f}k")

    trainer.fit(
        net,
        train_dataloaders=train_loader,
        val_dataloaders=val_loader,
    )

    best_model_path = trainer.checkpoint_callback.best_model_path
    best_model = NBeats.load_from_checkpoint(best_model_path)

    return best_model, val_loader

def save_bentoml_model(model, stock_code):
    svc = StockPredictionService()
    svc.pack(f'forecast_{stock_code}', model)
    svc.save()
    return

if __name__ == "__main__":

    job_id = os.environ["job_id"]
    data_path = f"/code/data/{job_id}"
    with open(os.path.join(data_path, "data.json"), "r", encoding="UTF-8") as f:
        data = json.load(f)

    with open(os.path.join(data_path, "config.json"), "r", encoding="UTF-8") as c:
        config = json.load(c)

    params = BaseParameter()
    df = preprocessing_data(data)
    best_model, valid_loader = nbeats_train(df, config, params)

    actuals = torch.cat([y[0] for _, y in iter(valid_loader)])
    predictions = best_model.predict(valid_loader)
    mae = (actuals - predictions).abs().mean()

    save_bentoml_model(best_model, config.stock_code)