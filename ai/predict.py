import os
from typings import List

import bentoml
from bentoml import env, artifacts, api, BentoService
from bentoml.adapters import DataframeInput, FileInput, JsonInput, JsonOutput
from bentoml.frameworks.pytorch import PytorchModelArtifact
from bentoml.types import JsonSerializable, InferenceTask, InferenceError

@env(infer_pip_packages=False)
@bentoml.artifacts([PytorchModelArtifact('ts'), PytorchModelArtifact('text')])

class StockPredictionService(bentoml.BentoService):
	
    @api(
        input=JsonInput(), 
        output=JsonOutput, 
        route='v1/price/predict', 
        batch=False) # if batch=True input type must be List[]
    def predict_price(self, parsed_json: JsonSerializable, task: InferenceTask) -> InferenceResult:
        
        df = self.artifacts.model_a.predict(parsed_json["data"])
        return InferenceResult(
                  data=self.artifacts.ts.predict(df),
                  http_status=200,
                  http_headers={"Content-Type": "application/json"},
              )
          else:
              return InferenceError(err_msg="application/json output only", http_status=400)

class NewsService(bentoml.BentoService):

    @api(
        input=JsonInput(), 
        output=JsonOutput, 
        route='v1/text_abb/predict', 
        mb_max_latency=200, 
        mb_max_batch_size=500, 
        batch=True) # mb = micro batch
    def predict_abbreviation(self, parsed_json: List[JsonSerializable], task: InferenceTask) -> InferenceResult:
        # assume the output of model_a will be the input of model_b in this example:
        df = self.artifacts.model_a.predict(parsed_json["data"])
	
        return InferenceResult(
                  data=self.artifacts.text.predict(df),
                  http_status=200,
                  http_headers={"Content-Type": "application/json"},
              )
          else:
              return InferenceError(err_msg="application/json output only", http_status=400)