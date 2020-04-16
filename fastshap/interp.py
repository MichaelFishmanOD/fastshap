# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/01_interpret.ipynb (unless otherwise specified).

__all__ = ['ShapInterpretation']

# Cell
from .core import _prepare_data, _predict
import shap
from fastai2.tabular.all import *

# Cell
class ShapInterpretation():
  "Base interpereter to use the `SHAP` interpretation library"
  def __init__(self, learn:TabularLearner, test_data=None, link='identity', l1_reg='auto', n_samples=128, **kwargs):
    "Initialize `ShapInterpretation` with a Learner, test_data, link, `n_samples`, `l1_reg`, and optional **kwargs"
    self.model = learn.model
    self.dls = learn.dls
    self.class_names = learn.dl.vocab if hasattr(learn.dl, 'vocab') else None # only defined for classification problems
    self.train_data = pd.merge(learn.dls.cats, learn.dls.conts, left_index=True, right_index=True)
    self.test_data, self.test_data_cat, self.test_idx = _prepare_data(learn, test_data, n_samples)
    pred_func = partial(_predict, learn)
    self.explainer = shap.SamplingExplainer(pred_func, self.train_data, **kwargs)
    self.shap_vals = self.explainer.shap_values(self.test_data, l1_reg=l1_reg)
    self.is_multi_output = isinstance(self.shap_vals, list)

  def decision_plot(self, class_id=0, row_idx=-1, **kwargs):
    "Visualize model decision using cumulative `SHAP` values."
    shap_vals, exp_val = _get_values(self, class_id)
    n_rows = shap_vals.shape[0]
    if row_idx == -1:
      print(f'Displaying rows 0-9 of {n_rows} (use `row_idx` to specify another row)')
      return shap.decision_plot(exp_val, shap_vals[:10], self.test_data.iloc[:10], **kwargs)
    print(f'Displaying row {row_idx} of {n_rows} (use `row_idx` to specify another row)')
    return shap.decision_plot(exp_val, shap_vals[row_idx], self.test_data.iloc[row_idx], **kwargs)

  def dependence_plot(self, variable_name:str="", class_id=0, use_cat = False, **kwargs):
    "Plots value of variable on the x-axis and the SHAP value of the same variable on the y-axis"
    if variable_name is "":
      raise ValueError('No variable passed in for `variable_name`')
    shap_vals, _ = _get_values(self, class_id)
    if use_cat:
      return shap.dependence_plot(variable_name, shap_vals, self.test_data_cat, **kwargs)
    else:
      return shap.dependence_plot(variable_name, shap_vals, self.test_data, **kwargs)


  def force_plot(self, class_id=0, matplotlib=False, **kwargs):
    "Visualize the `SHAP` values with additive force layout"
    shap_vals, exp_val = _get_values(self, class_id)
    if not matplotlib: shap.initjs()
    return shap.force_plot(exp_val, shap_vals, self.test_data, matplotlib=matplotlib, **kwargs)

  def summary_plot(self, **kwargs):
    "Displays `SHAP` values which can be interperated for feature importance"
    return shap.summary_plot(self.shap_vals, self.test_data, class_names=self.class_names, **kwargs)

  def waterfall_plot(self, row_idx=None, class_id=0, **kwargs):
    "Plots explaination of single prediction as waterfall plot"
    shap_vals, exp_val = _get_values(self, class_id)
    n_rows = shap_vals.shape[0]
    row_idx = random.randint(0, n_rows-1) if row_idx is None else row_idx
    print(f'Displaying row {row_idx} of {n_rows} (use `row_idx` to specify another row)')
    feat_names = self.test_data.columns
    return shap.waterfall_plot(exp_val, shap_vals[row_idx,:], feature_names=feat_names, **kwargs)

# Cell
def _get_class_info(interp:ShapInterpretation, class_id):
  "Returns class name associated with index, or vice-versa"
  if isinstance(class_id, int): class_idx, class_name = class_id, interp.class_names[class_id]
  else: class_idx, class_name = interp.class_names.o2i[class_id], class_id
  return (class_name, class_idx)

# Cell
def _get_values(interp:ShapInterpretation, class_id=0):
  "Returns `shap_value` and `expected_value`"
  shap_vals = interp.shap_vals
  exp_vals = interp.explainer.expected_value
  if interp.is_multi_output:
    (class_name, class_idx) = _get_class_info(interp, class_id)
    print(f"Classification model detected, displaying score for the class {class_name}.")
    print("(use `class_id` to specify another class)")
    return (shap_vals[class_idx], exp_vals[class_idx])
  else:
    exp_vals = exp_vals[0]
  return (shap_vals, exp_vals)