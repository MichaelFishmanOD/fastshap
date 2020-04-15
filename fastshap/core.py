# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_core.ipynb (unless otherwise specified).

__all__ = []

# Cell
from fastai2.tabular.all import *

# Cell
def _prepare_data(learn:Learner, test_data=None, n_samples:int=128):
  "Prepares train and test data for `SHAP`, pass in a learner with optional data"
  no_user_provided_test_data = test_data is None
  if isinstance(test_data, pd.DataFrame):
    test_data_og = test_data.copy()
    dl = learn.dls.test_dl(test_data)
  elif isinstance(test_data, TabDataLoader):
    dl = test_data
  elif test_data is None:
    try:
      dl = learn.dls[1]
    except IndexError:
      print('No validation dataloader, using `train`')
      dl = learn.dls[0]
  else:
    raise ValueError('Input is not supported. Please use either a `DataFrame` or `TabularDataLoader`')
  test_data = pd.merge(dl.cats, dl.conts, left_index=True, right_index=True)

  n_samples = min(n_samples, len(test_data))
  idx =  np.sort(np.random.choice(np.array(test_data.index), size=n_samples, replace=False))
  test_data = test_data.loc[idx]
#   If we were passed a test_data dataframe, create test_data_cat, which has the original categorical values instead of codes
  try:
        test_data_cat = test_data.copy()
        for c in test_data_og.columns:
            if c in test_data_cat.columns:
                test_data_cat[c] = test_data_og[c]
  except NameError:
    test_data_cat = None
  return test_data, test_data_cat

# Cell
def _predict(learn:TabularLearner, data:np.array):
  "Predict function for some data on a fastai model"
  device = 'cuda' if torch.cuda.is_available() else 'cpu'
  model = learn.model.to(device)
  dl = learn.dls[0]
  nb_cat_cols = len(dl.dataset.cat_names)
  nb_cont_cols = len(dl.dataset.cont_names)
  x_cat = torch.from_numpy(data[:, :nb_cat_cols]).to(device, torch.int64)
  x_cont = torch.from_numpy(data[:, -nb_cont_cols:]).to(device, torch.float32)
  with torch.no_grad():
    pred_probs = learn.model(x_cat, x_cont).cpu().numpy()
  return pred_probs