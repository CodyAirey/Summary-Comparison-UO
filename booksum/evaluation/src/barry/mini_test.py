from bary_score import BaryScoreMetric
from depth_score import DepthScoreMetric
from infolm import InfoLM


metric_call = BaryScoreMetric()

ref = [
        'I like my cakes very much',
        'I hate these cakes!']
hypothesis = ['I like my cakes very much',
                  'I like my cakes very much']

metric_call.prepare_idfs(hypothesis,ref)
final_preds = metric_call.evaluate_batch(hypothesis, ref)
print(final_preds)