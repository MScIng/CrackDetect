# To Do

## Model, Training and Feature Extraction
- [ ] Extract new features, using more than acc only
  - [ ] Check if this fixes std = 0 issue
- [X] Normalize inputs before feature extraction
- [ ] Find out why some features have std = 0
  - [ ] Also find out if for different signals they always output the same, i.e. channel 13 is always 14.7 or whatever
  - [ ] If can't find out and fix, then remove features with std = 0 before training
- [ ] Reduce step-size to avoid loss explosion (gradients exploding?)
  - [ ] If this doesn't work then we can do gradient clipping
- [X] Create Feature Data Set
  - [x] Implement transforms
    - [x] Normalize each feature
      - [x] Rocket feature transformation
      - [X] Problem: Some stds are 0 (current solution: pick max(stds, 1e-12), but causes features and loss to explode)
      - [x] New solution: Mean over feature_means and feature_stds instead
    - [x] Targets need to be in same range ([0, 1]?)
      - [x] Load Max and Min
      - [x] ```new_target = ((target - Min) / (Max - Min))```
      - [ ] Check that everything works
- [X] Implement new data loader
- [x] Feature extraction script
  - [x] Save features to file
    - [x] MultiRocket Features
    - [x] Hydra Features
    - [x] Save Max and Min targets
    - [x] Calculate and save statistics on features (mean, std)
      - [x] Hydra Statistics
      - [x] MultiRocket Statistics

 
- [x] Train script needs to batch over features
- [x] Train script needs to run epochs over data
- [x] Saving best model during training
- [x] Train script needs to follow Hydra/MR implementation
- [ ] Figure out which signals to extract features from
  
## Predicting
- [x] Modify predict script to follow train script
- [x] Load features for prediction (avoid long predict inference time)
- [x] Figure out what is happening with correlations...
- [ ] Cross correlation between target and predictions for different lags - report the lowest
- [ ] Report baseline RMSE with predictions (average of targets (?))


## Data loaders
- [ ] Evaluate whether we want to keep the transform arguments - they are currently big time unused, could be confusing

## Aflevering
- [ ] Comments, comments, comments... and more comments
- [ ] NO MAGIC NUMBERS (TOMMY BLIVER KED AF DET)
- [ ] Henvis til rapporten i koden (ligninger, osv.)