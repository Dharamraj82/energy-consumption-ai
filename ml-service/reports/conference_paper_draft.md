# AI-Based Energy Consumption Prediction System: A Benchmarked Random Forest Approach for Next-Hour Active Power Forecasting

**Conference Research Paper Draft — MCA Project**  
**Project:** AI-Based Energy Consumption Prediction System  
**Repository Working Directory:** `D:\energy-consumption-ai\ml-service`  

---

## Abstract

Accurate short-term residential electricity consumption forecasting is essential for enabling responsive Home Energy Management Systems (HEMS), local battery energy storage scheduling, and demand-side grid integration. However, residential demand profiles exhibit high non-linearity and volatility due to stochastic household occupant behaviors and intermittent major appliance activations. In this paper, we develop and benchmark a leak-free, reproducible machine learning pipeline to forecast next-hour mean household active power ($y_{t+1}$ in kW) using telemetry from the benchmark UCI Individual Household Electric Power Consumption dataset. Over four years of sub-minute telemetry (2,075,259 raw readings) are aggregated to 34,589 hourly sequential observations. An autoregressive feature engineering pipeline generates eight causally compliant temporal and rolling-window predictors with strict zero-leakage enforcement. Four models are evaluated across a chronological 70% training, 15% validation, and 15% untouched held-out test partition: a non-parametric Persistence baseline, an Ordinary Least Squares (OLS) Linear Regression model, an unconstrained Original Random Forest regressor, and a regularized Tuned Random Forest regressor. Systematic hyperparameter tuning guided strictly by validation Mean Absolute Error (MAE) demonstrates that constraining tree depth ($\text{max\_depth}=10$) regularizes against high-frequency household demand volatility while reducing serialized model footprint by 88.2% (from 201.7 MB to 23.8 MB). On the completely held-out out-of-sample test set (5,185 hours), the Tuned Random Forest achieves an MAE of 0.3239 kW, a Root Mean Squared Error (RMSE) of 0.4682 kW, and a coefficient of determination ($R^2$) of 0.5555, representing an error reduction of 13.12% over Persistence and 9.98% over Linear Regression. We provide complete experimental transparency, audit methodological risks such as missing-value interpolation and near-zero percentage error distortion, and validate the end-to-end framework through an automated test suite.

**Keywords:** Household Energy Forecasting, Machine Learning, Random Forest Regressor, Time-Series Forecasting, Smart Meter Telemetry, Hyperparameter Optimization, Temporal Causality.

---

## 1. Introduction

Global transitions toward modernized smart electric grids, distributed rooftop photovoltaics, and localized home battery storage necessitate accurate short-term load forecasting (STLF) at the single-dwelling consumer level [Citation Needed: Smart Grid Residential Load Survey]. While utility-level aggregate load forecasting operates over smooth curves governed by central limit theorem aggregation, individual household electricity consumption is characterized by sudden, high-magnitude spikes and steep drops [Citation Needed: Individual vs Aggregate Load Dynamics]. Activities such as operating an electric water heater, running laundry appliances, or turning on cooking hobs cause immediate step changes in active power demand that challenge classical linear time-series approaches.

To address these non-linear consumption dynamics, modern data-driven forecasting relies increasingly on machine learning algorithms. However, several critical methodological flaws frequently recur in applied research:
1. **Temporal Data Leakage:** Randomly shuffling time-series data or computing global scaling parameters across the entire dataset artificially inflates predictive metrics by leaking future information into the training phase.
2. **Missing Benchmark Parity:** Machine learning models are often presented in isolation without rigorous comparison against naive baselines (such as persistence) or baseline linear regressors evaluated on identical timestamps and feature representations.
3. **Metric Artifacts in Low-Demand Regimes:** In single-family households, standby power during sleeping hours frequently drops below 0.15 kW. Standard percentage metrics like Mean Absolute Percentage Error (MAPE) divide by near-zero denominators, distorting numerical evaluations unless explicit mathematical constraints are applied.
4. **Over-parameterization:** Deep tree ensembles can memorize household-specific historical bursts rather than extracting robust diurnal and autoregressive trends, resulting in unwieldy artifacts unsuitable for embedded edge deployment in smart meters.

### Contributions of this Work
In this paper, developed as part of an MCA research project on AI-Based Energy Consumption Prediction, we address these challenges through a principled, end-to-end empirical study:
- **Strictly Causal System Design:** We establish an autoregressive and rolling feature pipeline derived exclusively from historical telemetry ($T \le t$) to forecast mean active power for hour $t+1$ without lookahead bias.
- **Audited Chronological Evaluation:** The dataset is split into chronological partitions: 70% Training (Dec 2006 – Sep 2009), 15% Validation (Sep 2009 – Apr 2010), and an untouched 15% Held-Out Test set (Apr 2010 – Nov 2010). Model selection and hyperparameter optimization are confined strictly to the validation split.
- **Fair Multi-Model Benchmarking:** We compare four distinct paradigms on identical test timestamps: a non-parametric Persistence baseline, an Ordinary Least Squares (OLS) Linear Regression model, an Original Random Forest regressor, and a regularized Tuned Random Forest regressor.
- **Empirical Demonstration of Regularization:** We show that tuning the Random Forest primarily serves as structural regularization: restricting maximum tree depth yields a modest but reliable test MAE improvement (from 0.3283 kW to 0.3239 kW) while reducing model storage size from 201.7 MB down to 23.8 MB.
- **Methodological Integrity:** We report the exact empirical metrics obtained in code, evaluate residual distributions, audit interpolation leakage risks at boundary timestamps, and document all findings alongside an open test suite of 42 automated tests.

---

## 2. Related Work

Short-term residential load forecasting has historically evolved across statistical time-series analysis and machine learning methodologies.

### 2.1 Statistical and Classical Autoregressive Approaches
Classical forecasting frameworks primarily utilized Autoregressive Integrated Moving Average (ARIMA) and Seasonal ARIMA (SARIMA) formulations [Citation Needed: Box & Jenkins Time Series Analysis]. While effective for linear trends and stable cyclic periodicity, classical autoregressive models assume wide-sense stationarity and struggled to model the abrupt, non-linear step-functions caused by thermostat switching and intermittent appliance cycles [Citation Needed: Residential ARIMA Limitations]. Persistence models, wherein the load at the next time step is projected to equal current load, remain a standard benchmark in time-series literature; any viable predictive architecture must demonstrably outperform persistence to justify operational deployment.

### 2.2 Machine Learning and Tree-Based Ensembles
With the proliferation of high-resolution Advanced Metering Infrastructure (AMI), supervised machine learning algorithms have emerged as robust alternatives. Linear regression models provide transparent baselines by learning linear combinations of multi-lag and calendar indicators. Support Vector Regression (SVR) and Artificial Neural Networks (ANNs) capture non-linear relationships, but can be sensitive to scaling and computationally demanding [Citation Needed: Machine Learning for Smart Grid STLF].

Random Forests, proposed by Breiman (2001) [Citation Needed: Breiman Random Forests 2001], construct ensembles of de-correlated decision trees trained via bootstrap aggregation (bagging) and random subspace feature selection. Random Forests have demonstrated notable robustness in energy forecasting due to their invariance to monotonic feature transformations, natural resistance to noise, and ability to approximate arbitrary non-linear partition boundaries without requiring complex scaling.

### 2.3 Benchmarks on the UCI Household Electric Power Dataset
The UCI Individual Household Electric Power Consumption dataset, collected by Hebrail and Berard (2012) [Citation Needed: Hebrail & Berard UCI Dataset], represents a widely recognized standard in residential energy research. While several studies in the literature claim high predictive accuracy on this dataset, many employ random train-test splitting (which invalidates time-series independence by predicting intermediate hours from adjacent temporal points) or evaluate only short sample windows. This paper uses the full 4-year continuous sequence, enforces strict chronological partitioning, and preserves all raw experimental results for peer replication.

---

## 3. Methodology & System Architecture

The overall pipeline of the proposed AI-Based Energy Consumption Prediction System is illustrated in the architectural workflow:

```text
Raw Telemetry (UCI Dataset 235: 2,075,259 records)
       │
       ▼
Hourly Resampling & Interpolation (34,589 sequential hours)
       │
       ▼
Causal Feature Engineering (8 predictors, N = 34,565 leak-free samples)
       │
       ├─── 70% Chronological Training (24,195 samples) ────────► Model Fitting (OLS, RF)
       ├─── 15% Chronological Validation (5,185 samples) ──────► Hyperparameter Search & Selection
       └─── 15% Untouched Held-Out Test (5,185 samples) ────────► Final Out-of-Sample Evaluation
```

### 3.1 Dataset Specification and Ingestion
Telemetry was gathered from the UCI Machine Learning Repository (Dataset ID: 235). The raw data spans 47 months from December 16, 2006 (17:24:00) to November 26, 2010 (21:02:00), comprising 2,075,259 minute-level readings of household electrical quantities. 

The primary target of interest is **`Global_active_power`**, representing household mean active power in kilowatts (kW). Raw minute readings were aggregated into continuous hourly intervals using an arithmetic mean:
$$\bar{y}_\tau = \frac{1}{|M_\tau|} \sum_{m \in M_\tau} y_m$$
where $M_\tau$ is the set of minute observations recorded in hour $\tau \in \{1, \dots, 34589\}$. 

A total of 421 missing hourly values (~1.2% of the four-year series) arose due to intermittent meter disconnections or equipment maintenance. Because autoregressive lag features require an unbroken temporal sequence, missing hourly intervals were imputed using time-based linear interpolation across the hourly index.

### 3.2 Feature Engineering and Strict Temporal Causality
To eliminate lookahead bias and future-information leakage, all predictive features for forecasting active power at hour $t+1$ are constructed strictly from telemetry recorded at or prior to observation hour $t$. The feature space consists of eight variables:

1. **Short-Term Autoregressive Lags:**
   - $\text{lag\_1} = y_t$: Mean active power at the current observation hour $t$ (kW).
   - $\text{lag\_2} = y_{t-1}$: Mean active power 1 hour prior to observation hour $t$ (kW).
   - $\text{lag\_3} = y_{t-2}$: Mean active power 2 hours prior to observation hour $t$ (kW).
2. **Diurnal Seasonal Lag:**
   - $\text{lag\_24} = y_{t-23}$: Mean active power exactly 24 hours prior to the target hour $t+1$ (kW).
3. **Rolling Window Aggregations:**
   - $\text{rolling\_mean\_3h} = \frac{1}{3} \sum_{k=0}^{2} y_{t-k}$: 3-hour backward moving average over $[t-2, t-1, t]$ (kW), capturing short-term consumption momentum.
   - $\text{rolling\_mean\_24h} = \frac{1}{24} \sum_{k=0}^{23} y_{t-k}$: 24-hour backward moving average over $[t-23, \dots, t]$ (kW), capturing daily baseline consumption.
4. **Deterministic Calendar Variables:**
   - $\text{hour} \in \{0, 1, \dots, 23\}$: The hour of the day corresponding to observation time $t$.
   - $\text{day\_of\_week} \in \{0, 1, \dots, 6\}$: Day of the week ($0 = \text{Monday}, 6 = \text{Sunday}$).
5. **Target Variable:**
   - $\text{target} = y_{t+1}$: Mean active power at hour $t+1$ (kW).

Due to the 24-hour lookback window, the first 23 rows cannot compute `lag_24` and are dropped. Similarly, the final row of the dataset cannot observe $y_{t+1}$ and is dropped. This leaves an unbroken, leak-free design matrix of **$N = 34,565$ observations**.

### 3.3 Chronological Dataset Partitioning
Standard random cross-validation randomly shuffles observations, which breaks temporal autocorrelation and permits models to interpolate points using both past and future neighbors. To enforce genuine predictive causality, data was partitioned strictly along chronological boundaries using a 70% / 15% / 15% division:

- **Training Set (70%):** 24,195 samples  
  *Span:* December 17, 2006 (16:00:00) to September 20, 2009 (18:00:00). Used exclusively for fitting model coefficients and tree splits.
- **Validation Set (15%):** 5,185 samples  
  *Span:* September 20, 2009 (19:00:00) to April 24, 2010 (19:00:00). Used exclusively for model benchmarking, hyperparameter grid search, and model selection.
- **Held-Out Test Set (15%):** 5,185 samples  
  *Span:* April 24, 2010 (20:00:00) to November 26, 2010 (20:00:00). Kept untouched until final out-of-sample evaluation.

```text
Sequence Timeline (Total N = 34,565 hours):
├─────────────────────── Train (70%) ───────────────────────┼──── Val (15%) ────┼──── Test (15%) ────┤
2006-12-17 16:00                                    2009-09-20 18:00    2010-04-24 19:00     2010-11-26 20:00
```

### 3.4 Model Formulations

#### A. Persistence Baseline
The Persistence model serves as the primary non-parametric time-series benchmark, projecting that the electricity demand in the next hour will simply equal the observed demand in the current hour:
$$\hat{y}_{t+1} = y_t = \text{lag\_1}$$
No training parameters are fitted. Any learned model must surpass this baseline to demonstrate value.

#### B. Ordinary Least Squares (OLS) Linear Regression
The Linear Regression baseline constructs a global hyperplane across the 8-dimensional feature space $\mathbf{x}_t \in \mathbb{R}^8$:
$$\hat{y}_{t+1} = \mathbf{w}^T \mathbf{x}_t + b$$
Coefficients $\mathbf{w}$ and intercept $b$ are determined via Ordinary Least Squares minimization on the training partition:
$$\min_{\mathbf{w}, b} \sum_{i=1}^{N_{\text{train}}} \left( y_{i} - (\mathbf{w}^T \mathbf{x}_i + b) \right)^2$$

#### C. Random Forest Regressor
The Random Forest regressor builds an ensemble of $B$ randomized regression trees $\{T_1, T_2, \dots, T_B\}$. Each individual tree $T_b$ is trained on an independent bootstrap sample of the training data. At each candidate split node, a random subset of $m$ features ($\text{max\_features} \le p = 8$) is evaluated to find the feature $j$ and split threshold $s$ that minimizes mean squared error impurity:
$$\Delta I = \text{Var}(S) - \left( \frac{|S_L|}{|S|}\text{Var}(S_L) + \frac{|S_R|}{|S|}\text{Var}(S_R) \right)$$
Ensemble prediction averages the outputs of all $B$ trees:
$$\hat{y}_{t+1} = \frac{1}{B} \sum_{b=1}^{B} T_b(\mathbf{x}_t)$$
The original (unconstrained) Random Forest model was instantiated with $B = 250$ trees, $\text{max\_depth} = 20$, $\text{min\_samples\_leaf} = 2$, $\text{max\_features} = 1.0$, and fixed seed $\text{random\_state}=42$.

### 3.5 Quantitative Evaluation Metrics
Model accuracy is evaluated using four complementary metrics:

1. **Mean Absolute Error (MAE):**
   $$\text{MAE} = \frac{1}{N} \sum_{i=1}^{N} |y_i - \hat{y}_i|$$
   MAE measures average absolute error magnitude directly in physical units (kW) and is robust to extreme outliers.
2. **Root Mean Squared Error (RMSE):**
   $$\text{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^{N} (y_i - \hat{y}_i)^2}$$
   RMSE applies quadratic penalties to large forecast deviations, reflecting grid stress caused by peak load underestimation.
3. **Coefficient of Determination ($R^2$):**
   $$R^2 = 1 - \frac{\sum_{i=1}^{N} (y_i - \hat{y}_i)^2}{\sum_{i=1}^{N} (y_i - \bar{y})^2}$$
   $R^2$ measures the proportion of variance in active power explained by the model relative to a mean-value baseline.
4. **Mean Absolute Percentage Error (MAPE) with Epsilon Floor:**
   Standard MAPE is computed as:
   $$\text{MAPE} = \frac{100\%}{N} \sum_{i=1}^{N} \frac{|y_i - \hat{y}_i|}{\max(|y_i|, \epsilon)}$$
   In residential consumption, standby loads during night hours frequently hover near 0.1 kW. Dividing by values close to zero causes severe arithmetic inflation. To prevent numerical distortion, we incorporate an explicit floor parameter of $\epsilon = 10^{-4}$ kW ($0.1$ W). While reported for completeness, MAE and RMSE remain our authoritative decision metrics.

---

## 4. Hyperparameter Optimization & Model Selection

To explore whether model performance could be improved and over-parameterization reduced, hyperparameter tuning was conducted systematically using **only the validation partition**. 

### 4.1 Search Grid Design
A multi-dimensional grid of 20 configurations was evaluated across key tree parameters:
- Number of estimators: $B \in \{150, 250, 400\}$
- Maximum tree depth: $\text{max\_depth} \in \{10, 20, 30, \text{None}\}$
- Minimum samples per leaf: $\text{min\_samples\_leaf} \in \{1, 2, 4\}$
- Feature subspace fraction: $\text{max\_features} \in \{0.7, 1.0\}$

Each candidate model was fitted on the 24,195 training samples and evaluated on the 5,185 validation samples.

```text
Table: Representative Hyperparameter Candidates on Chronological Validation Set
┌──────────────┬───────────────┬───────────┬──────────────┬──────────────┬──────────────┬──────────────┐
│ Candidate ID │ n_estimators  │ max_depth │ min_leaf     │ max_features │ Val MAE (kW) │ Val RMSE(kW) │
├──────────────┼───────────────┼───────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ 1 (Original) │ 250           │ 20        │ 2            │ 1.0          │ 0.3747       │ 0.5443       │
│ 2            │ 150           │ 10        │ 2            │ 1.0          │ 0.3707       │ 0.5414       │
│ 3            │ 150           │ 20        │ 2            │ 1.0          │ 0.3750       │ 0.5451       │
│ 5            │ 150           │ None      │ 2            │ 1.0          │ 0.3757       │ 0.5455       │
│ 10           │ 150           │ 20        │ 2            │ 0.7          │ 0.3735       │ 0.5416       │
│ 11           │ 150           │ 10        │ 2            │ 0.7          │ 0.3720       │ 0.5416       │
│ 14 (Tuned)*  │ 250           │ 10        │ 2            │ 1.0          │ 0.3703       │ 0.5411       │
│ 18           │ 400           │ 10        │ 2            │ 1.0          │ 0.3704       │ 0.5410       │
└──────────────┴───────────────┴───────────┴──────────────┴──────────────┴──────────────┴──────────────┘
* Candidate 14 achieved the lowest Validation MAE (0.3703 kW) and was selected as the final model.
```

### 4.2 Analysis of Hyperparameter Dynamics and Regularization
The validation search revealed clear structural insights:
1. **Tree Depth Regularization:** Unconstrained or deep trees ($\text{max\_depth} \ge 20$ or $\text{None}$) consistently exhibited higher validation error ($\text{Val MAE} \approx 0.3747 - 0.3757$ kW). When depth was capped at $\text{max\_depth} = 10$, validation MAE dropped to $0.3703$ kW. Limiting depth acts as explicit regularization, preventing individual decision paths from memorizing idiosyncratic, high-frequency appliance activations in the training set.
2. **Diminishing Returns of Ensemble Size:** Increasing $B$ from 150 to 250 yielded a minor validation MAE reduction (from $0.3707$ kW to $0.3703$ kW), but scaling further to $B = 400$ produced no additional gain ($0.3704$ kW) while increasing training time by 59% (from 10.29s to 16.42s).
3. **Artifact Compression:** The original model ($\text{max\_depth}=20$) generated deep trees requiring **201.7 MB** of storage on disk. By pruning maximum depth to 10, the serialized artifact size shrank to **23.8 MB**—an **88.2% reduction in memory footprint** with no loss in accuracy.

Guided strictly by minimum validation MAE, Candidate 14 (`n_estimators=250, max_depth=10, min_samples_leaf=2, max_features=1.0`) was selected as the final production configuration.

---

## 5. Experimental Results and Discussion

### 5.1 Consolidated Benchmark Results
Table 1 presents the empirical performance of all four evaluated models across both the chronological validation split (5,185 hours) and the untouched held-out test split (5,185 hours).

```text
Table 1: Consolidated Benchmark Performance Across Chronological Splits
┌──────────────────────────┬─────────────────────────────┬────────────────────────────────────────────────────────┐
│                          │    Validation Set (15%)     │                   Held-Out Test Set (15%)              │
│ Model                    ├─────────┬─────────┬─────────┼─────────┬─────────┬────────┬──────────┬────────────────┤
│                          │ MAE(kW) │ RMSE(kW)│ R²      │ MAE(kW) │ RMSE(kW)│ R²     │ MAPE (%) │ MAE Red. vs BL │
├──────────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼────────┼──────────┼────────────────┤
│ Persistence Baseline     │ 0.4555  │ 0.6844  │ 0.4147  │ 0.3728  │ 0.5752  │ 0.3291 │ 44.75%   │ Reference      │
│ Linear Regression (OLS)  │ 0.4405  │ 0.6096  │ 0.5355  │ 0.3598  │ 0.5058  │ 0.4811 │ 50.08%   │ +3.49%         │
│ Random Forest (Original) │ 0.3747  │ 0.5443  │ 0.6297  │ 0.3283  │ 0.4734  │ 0.5454 │ 44.78%   │ +11.94%        │
│ Random Forest (Tuned)*   │ 0.3703  │ 0.5411  │ 0.6340  │ 0.3239  │ 0.4682  │ 0.5555 │ 44.19%   │ +13.12%        │
└──────────────────────────┴─────────┴─────────┴─────────┴─────────┴─────────┴────────┴──────────┴────────────────┘
* Selected best model based on lowest Validation MAE. All test metrics evaluated strictly out-of-sample.
```

### 5.2 Comparative Analysis Across Model Paradigms
The progression across the four models illustrates key characteristics of residential load forecasting:

1. **Persistence vs. Linear Regression:**  
   The Persistence model provides a competitive benchmark, reflecting the autocorrelation between adjacent hours. However, Linear Regression leverages multi-lag terms (`lag_2`, `lag_3`, `lag_24`), moving averages, and deterministic calendar features (`hour`, `day_of_week`), reducing test MAE from 0.3728 kW to 0.3598 kW (a 3.49% improvement) and improving $R^2$ from 0.3291 to 0.4811.
2. **Linear Regression vs. Random Forest:**  
   Transitioning from Linear Regression to the non-linear Random Forest yields a substantial leap in accuracy. The Original Random Forest reduces test MAE to 0.3283 kW (an 8.75% error reduction over Linear Regression and 11.94% over Persistence), with test $R^2$ climbing to 0.5454. The tree ensemble's ability to model non-linear interactions—such as differing consumption thresholds between weekdays and weekends, or time-of-day specific power states—proves markedly superior to a single linear hyperplane.
3. **Impact of Hyperparameter Tuning:**  
   Tuning the Random Forest yields a modest numerical gain in error metrics: test MAE improves from 0.3283 kW to 0.3239 kW (a +1.34% relative improvement; +13.12% cumulative over Persistence), test RMSE improves from 0.4734 kW to 0.4682 kW, and $R^2$ increases to 0.5555. Crucially, the primary benefit of tuning is structural stability and resource efficiency: restricting tree depth regularizes against high-variance leaf predictions while slashing disk requirements by 88.2%.

### 5.3 Visual Evidence and Empirical Audits
The experimental findings are corroborated by seven diagnostic figures generated from the pipeline artifacts:

- **Benchmark Error Comparison (`reports/figures/model_mae_comparison.png`):** Demonstrates the step-wise reduction in test MAE across the evaluated architectures, highlighting the distinct performance tier occupied by tree ensembles over linear baselines.
- **Multi-Model Tracking Trajectory (`reports/figures/model_comparison_actual_vs_predicted.png`):** A dual-panel time-series visualization comparing all models against actual load. Over a 168-hour (one-week) window, Persistence exhibits a constant one-step phase lag, while Linear Regression underestimates peak consumption. In contrast, the Tuned Random Forest closely tracks both evening peak demand (18:00–22:00) and low night-time baselines.
- **Validation Tuning Comparison (`reports/figures/model_tuning_comparison.png`):** Directly compares the Original vs. Tuned configurations across validation MAE (0.3747 kW $\to$ 0.3703 kW) and RMSE (0.5443 kW $\to$ 0.5411 kW).
- **Actual vs. Predicted Scatter (`reports/figures/actual_vs_predicted.png`):** Displays scatter points for all 5,185 held-out test hours against the ideal $y = x$ line. Predictions cluster tightly along the diagonal throughout the 0.2–2.5 kW range, with increased dispersion occurring only during rare, extreme demand spikes (> 4.0 kW).
- **Residual Distribution and Bias (`reports/figures/error_summary.png` & `residuals_plot.png`):** The residual error distribution ($\epsilon_i = y_i - \hat{y}_i$) exhibits a near-zero mean bias ($\mu = -0.007$ kW), confirming that the model does not suffer from systematic under- or over-forecasting. The residual standard deviation is 0.468 kW, aligning with the test RMSE.
- **Feature Importance Analysis (`reports/figures/feature_importance.png`):** Evaluates Mean Decrease in Impurity (MDI / Gini importance) across all 8 feature inputs:
  - `lag_1` (Immediate prior hour): **0.488** (Dominant predictor; household state persistence)
  - `rolling_mean_3h` (Short-term moving average): **0.135** (Captures multi-hour activity trends)
  - `lag_24` (Same hour yesterday): **0.133** (Captures daily diurnal periodicity)
  - `hour` (Hour of day): **0.089** (Encodes scheduled daily routines)
  - `rolling_mean_24h` (Daily baseline): **0.054**
  - `lag_2`: **0.041**
  - `lag_3`: **0.033**
  - `day_of_week`: **0.027**

This ranking confirms that short-term temporal continuity (`lag_1`, `rolling_mean_3h`) combined with daily periodicity (`lag_24`, `hour`) accounts for over 84% of total predictive power.

---

## 6. Critical Limitations and Methodological Considerations

To maintain scientific integrity, several critical methodological questions and operational boundaries must be addressed:

### 6.1 Audit of Missing-Value Interpolation and Split Boundaries
Linear interpolation was applied to impute 421 missing hours (~1.2%) in the resampled series to provide an unbroken sequence for lag calculations. In time-series research, interpolating across split boundaries can inadvertently leak future information into past splits if a missing sequence bridges the partition boundary.

To evaluate this risk, we performed an empirical audit of the time-series around the exact partition transitions:
- **Train/Validation Boundary:** September 20, 2009 (18:00:00). An inspection of a 4-day window centered on this timestamp revealed **0 missing hours**.
- **Validation/Test Boundary:** April 24, 2010 (19:00:00). An inspection of a 4-day window centered on this timestamp revealed **0 missing hours**.

Because no missing data occurred within multi-day windows around the split points, the linear interpolation did not compute slopes across partition boundaries. The splits remain strictly causally independent.

### 6.2 Interpretation of Percentage Error (MAPE) in Low-Power Regimes
While MAPE is widely cited in macroeconomic load studies, its application to single-household telemetry requires careful qualification. In the test partition, standby active power frequently dropped below 0.15 kW during late-night hours. Under these conditions:
$$\frac{|y_i - \hat{y}_i|}{y_i} = \frac{|0.12 - 0.22|}{0.12} = 83.3\%$$
Even though the absolute error magnitude is a negligible 0.10 kW (100 Watts), the percentage error is artificially inflated. This denominator asymmetry explains why the test MAPE across all models remains in the 44%–50% range despite strong absolute accuracy (Test MAE of 0.3239 kW on a series with standard deviation $\approx 0.70$ kW). For practical grid management and battery dispatch, physical metric units (MAE and RMSE in kW) are the authoritative indicators of operational performance.

### 6.3 Single-Dwelling Telemetry and Exogenous Weather Features
The dataset represents telemetry from a single household located in Sceaux, France. While internal lifestyle routines (morning and evening routines, weekend shifts) are captured well by calendar features, residential space heating and cooling loads are heavily driven by external weather conditions (ambient outdoor temperature, solar irradiance, relative humidity). Because localized meteorological telemetry is absent from the UCI dataset, the model cannot anticipate unseasonal temperature drops. Integrating outdoor weather telemetry represents a necessary extension before deploying to diverse geographical areas.

### 6.4 Non-Claims on Complex Architectures
We explicitly note that complex alternative architectures—such as Genetic Algorithm feature selection, Extreme Gradient Boosting (XGBoost), Long Short-Term Memory networks (LSTM), Gated Recurrent Units (GRU), or heterogeneous meta-model stacking—were not implemented in this study. The regularized Random Forest was selected to provide an interpretable, reproducible, and computationally efficient benchmark.

---

## 7. System Implementation and Reproducibility

The complete ML service is organized as an enterprise-grade, reproducible Python module adhering to strict separation of concerns:

- `src/ml/data_loader.py`: Ingestion of raw UCI telemetry and hourly arithmetic resampling.
- `src/ml/preprocessing.py`: Chronological dataset splitting and missing-value handling.
- `src/ml/features.py`: Deterministic, causal generation of lag and rolling features.
- `src/ml/train.py`: Model fitting for Linear Regression and Random Forest ensembles.
- `src/ml/evaluate.py`: Computation of physical and percentage error metrics, residual distributions, and feature importances.
- `src/ml/predict.py`: Standalone inference CLI verifying serialized artifact loading and single-instance prediction.
- `tests/`: Comprehensive test suite containing 42 automated unit tests verifying timestamp monotonicity, leakage-free feature alignment, chronological splitting fractions, model persistence, and metadata consistency.

All 42 automated tests pass with 0 errors and 0 failures, ensuring complete reproducibility of all reported figures and metrics.

---

## 8. Conclusion and Future Work

In this paper, we presented a benchmarked, leak-free machine learning system for next-hour household active power forecasting using four years of continuous telemetry. Through strict chronological partitioning (70% train / 15% validation / 15% held-out test), we evaluated Persistence, Linear Regression, Original Random Forest, and Tuned Random Forest models. 

Our empirical results demonstrate that:
1. Non-linear tree ensembles significantly outperform persistence and linear baselines, achieving a 13.12% test MAE reduction over persistence.
2. Hyperparameter optimization through tree-depth regularization ($\text{max\_depth}=10$) mitigates overfitting to intermittent appliance spikes while compressing model size by 88.2% (23.8 MB vs. 201.7 MB), facilitating deployment in resource-constrained smart meter environments.
3. Feature importance analysis confirms that immediate past consumption (`lag_1`), short-term momentum (`rolling_mean_3h`), and diurnal periodicity (`lag_24`, `hour`) provide over 84% of total predictive signal.

Future work will focus on integrating real-time ambient temperature streams from local weather APIs, extending the architecture across multi-building smart meter cohorts, and evaluating lightweight gradient boosting architectures for sub-second edge inference.

---

## References

1. Breiman, L. (2001). Random forests. *Machine Learning*, 45(1), 5-32. `[Citation Needed: Verify publication volume and page details]`
2. Hebrail, G., & Berard, A. (2012). Individual Household Electric Power Consumption Data Set. *UCI Machine Learning Repository*. Available: https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption
3. Box, G. E., Jenkins, G. M., Reinsel, G. C., & Ljung, G. M. (2015). *Time Series Analysis: Forecasting and Control*. John Wiley & Sons. `[Citation Needed: Verify textbook edition cited]`
4. Hyndman, R. J., & Athanasopoulos, G. (2018). *Forecasting: Principles and Practice* (2nd ed.). OTexts. `[Citation Needed: Verify online reference access]`
5. Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research*, 12, 2825-2830.
6. McKinney, W. (2010). Data structures for statistical computing in Python. In *Proceedings of the 9th Python in Science Conference* (pp. 56-61).
7. [Citation Needed: Key reference on residential short-term load forecasting using smart meter data].
8. [Citation Needed: Key benchmark study evaluating tree-based regression on residential power consumption].

---
*End of Conference Paper Draft.*
