# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/01_interpret.ipynb (unless otherwise specified).

__all__ = ['ShapInterpretation']

# Cell
from .core import _prepare_data, _predict
import shap
from fastai2.tabular.all import *

# Cell
class ShapInterpretation():
  "Base interpereter to use the `SHAP` interpretation library"
  def __init__(self, learn:TabularLearner, test_data=None, link='identity', l1_reg='auto', matplotlib=False, **kwargs):
    "Initialize `ShapInterpretation` with a Learner, test_data, link, `n_samples`, `l1_reg`, and optional **kwargs"
    self.model = learn.model
    self.dls = learn.dls
    self.class_names = learn.dl.vocab
    self.train_data = learn.dls.all_cols
    self.test_data = _prepare_data(learn, test_data)
    self.is_mat = matplotlib
    pred_func = partial(_predict, learn)
    self.explainer = shap.SamplingExplainer(pred_func, self.train_data, **kwargs)
    self.shap_vals = self.explainer.shap_values(self.test_data, l1_reg=l1_reg)
    self.is_multi_output = isinstance(self.shap_vals, list)

  def decision_plot(self, class_id=0, idx=-1, **kwargs):
    "Visualize model decision using cumulative `SHAP` values."
    shap_vals, exp_val = _get_values(self, class_id)
    if idx == -1:
      return shap.decision_plot(exp_val, shap_vals[:10], self.test_data.iloc[:10], **kwargs)
    return shap.decision_plot(exp_val, shap_vals[idx], self.test_data.iloc[idx], **kwargs)

  def dependence_plot(self, variable_name:str="", class_id=0, idx:int=0, **kwargs):
    "Plots value of variable on the x-axis and the SHAP value of the same variable on the y-axis"
    if variable_name is "":
      raise ValueError('No variable passed in for `variable_name`')
    shap_vals, _ = _get_values(self, class_id)
    return shap.dependence_plot(variable_name, shap_vals, self.test_data, **kwargs)

  def force_plot(self, class_id=0, **kwargs):
    "Visualize the `SHAP` values with additive force layout"
    shap_vals, exp_val = _get_values(self, class_id)
    if not self.is_mat: shap.initjs()
    return shap.force_plot(exp_val, shap_vals, self.test_data, matplotlib=self.is_mat, **kwargs)

  def summary_plot(self, **kwargs):
    "Displays `SHAP` values which can be interperated for feature importance"
    return shap.summary_plot(self.shap_vals, self.test_data, class_names=self.class_names, **kwargs)

  def waterfall_plot(self, row_idx=None, class_id=0, **kwargs):
    "Plots explaination of single prediction as waterfall plot"
    shap_vals, exp_val = _get_values(self, class_id)
    n_rows = shap_vals.shape[0]
    row_idx = random.randint(0, n_rows-1) if row_idx is not None else row_idx
    print(f'Displaying row {row_idx} of {n_rows} (use `row_idx` to specify another row)')
    feat_names = self.test_data.columns
    return shap.waterfall_plot(exp_val, shap_vals[row_idx,:], feature_names=feat_names, **kwargs)

# Cell
def _get_class_info(interp:ShapInterpretation, class_id):
  "Returns class name associated with index, or vice-versa"
  if isinstance(class_id, int): class_idx, class_name = class_id, interp.class_names[class_id]
  else: class_idx, class_name = interp.class_names.o2i[class_id], class_id
  return (class_name, class_idx)