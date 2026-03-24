## Page 1

Received 2 April 2024, accepted 21 May 2024, date of publication 29 May 2024, date of current version 10 June 2024.

Digital Object Identifier 10.1109/ACCESS.2024.3406670

Stateless System Performance Prediction and Health Assessment in Cloud Environments: Introducing cSysGuard, an Ensemble Modeling Approach

NUTT CHAIRATANA 1 AND RATHACHAI CHAWUTHAI 2

1Department of Robotics and AI Engineering, School of Engineering, King Mongkut’s Institute of Technology Ladkrabang, Bangkok 10520, Thailand 2Department of Computer Engineering, School of Engineering, King Mongkut’s Institute of Technology Ladkrabang, Bangkok 10520, Thailand

Corresponding author: Rathachai Chawuthai (rathachai.ch@kmitl.ac.th)

ABSTRACT Stateless cloud computing presents remarkable scalability and cost-effectiveness by offering dynamically adjustable resources tailored to fluctuating demands, eliminating the constraints of stateful architectures. However, the challenges presented by dynamic workload are substantial in the context of system health monitoring, frequently leading to service interruptions owing to insufficient resources. It underscores the need for the development of more efficient monitoring systems. Our study introduces cSysGuard, a novel framework designed to enhance monitoring capabilities within cloud environments. The methodology employs an ensemble regression model with a stacking strategy to forecast dynamic performance metrics. The algorithm also leverages a classification model to assess the system’s health based on forecasted metrics, effectively identifying potential failures in the future. Under the configuration utilized, our evaluations demonstrated increased predictive performance with cSysGuard in forecasting various metrics compared to traditional models. The results showed an improvement of up to a remarkable 2.28-fold increase, varying significantly based on the specific metric under consideration. In addition, the effectiveness of health assessment was achieved through Decision Trees with hyperparameter tuning, resulting in a macroaveraged F1 score of 89.79%. This research contributes to both the theoretical and practical aspects of server monitoring, presenting a solution that assesses system performance metrics and health to tackle dynamic challenges in cloud infrastructure.

INDEX TERMS Cloud computing, stacking ensemble models, machine learning, non-functional testing, predictive maintenance, resource allocation, proactive system metrics, stateless application.

I. INTRODUCTION Cloud computing, renowned for its scalability [1] and flexibility [2], has revolutionized the management of system resources. Within its broad spectrum, stateless cloud computing plays a crucial role. This paradigm facilitates the flexible allocation of resources without retaining session information [3], significantly aiding in instance scaling. In such cases, it significantly enhances system reliability and adaptability to fluctuating demands while maintaining

The associate editor coordinating the review of this manuscript and

---

## Page 2

II. LITERATURE REVIEW This section provides a comprehensive synthesis of cloud computing with machine-learning backgrounds, insights from prior studies, and the techniques utilized in our research.

A. ADAPTATION: CLOUD WITH MACHINE LEARNING Although cloud applications introduce innovative resource management strategies, they also present challenges in monitoring resources. Its variable nature complicates the effective tracking of fluctuating system metrics. Consequently, resource utilization can result in inefficiency and diminished system performance. It underscores the need for more flexible monitoring methods to precisely assess and adapt to the ever-changing requirements of cloud environments. Therefore, there is growing interest in leveraging machine learning techniques to address these challenges [12], [13], [14], [15], [16], [17], [18], [19], [20], [21], [22], [23], [24], [25], [26], [27], [28]. Machine learning-driven predictive analytics, widely used in many fields [29], can analyze complex data patterns to identity potential anomalies. This proactive approach enhances system reliability and resource allocation, ensuring scalable and responsive services. Integrating machine learning with cloud computing represents a significant advancement in improving system resource management.

---

## Page 3

FIGURE 1. RMSE-based performance of meta models. This figure illustrates the fluctuating performances of different meta-models for CPU requests (unit: percent) over 20 minutes in a dynamic environment.

C. TECHNIQUE This subsection provides a comprehensive overview of the essential techniques and a foundation for understanding the advancements in our study area.

1) LOW-PASS BUTTERWORTH FILTER The low-pass Butterworth filter, a key concept in signal processing [30], attenuates high-frequency noise while maintaining signal integrity. Characterized by its maximally flat magnitude response and ripple-free passband, the filter ensures a smooth frequency response up to the cutoff frequency, making it ideal for applications requiring undistorted outputs. Its transfer function, defined by the filter order, influences the steepness of the roll-off at the cut-off point [31]. Higher-order filters offer a faster passband-to-stopband transition but increase the complexity and risk of phase distortion. In the data analysis, the filter actively smooths out noise and data variations, bolstering the reliability of the analytical results.

2) SYNTHETIC MINORITY OVERSAMPLING TECHNIQUE The synthetic minority over-sampling technique (SMOTE) addresses imbalanced data by generating synthetic samples for the minority class, thereby improving the data distribution for machine learning applications. It creates new instances through interpolation between minority samples and their neighbors [32], enhancing diversity and reducing overfitting risks. However, its effectiveness depends on careful parameter tuning, including the number of neighbors and the amount of synthetic data generated. The versatility of SMOTE makes it applicable across various domains, from fraud detection to medical diagnoses, where it significantly contributes to more equitable and accurate predictive modeling.

3) ENSEMBLE MODEL: STACKING The stacking approach in ensemble models features a multilayered structure, each recognized as a Level-N layer, for enhanced prediction. Initially, the base models process the data independently, offering diverse analytical perspectives. Higher-level models then collectively analyze their outputs to enhance predictive accuracy. Each subsequent level integrates and improves upon the previous ones [33], reducing biases and variances, thus enhancing the overall predictive accuracy. Fig. 2 visually represents the multi-layer stacking approach, presenting the flow from Level-0 to Level-N layers.

---

## Page 4

FIGURE 2. Multi-layer stacking in ensemble modeling. This figure depicts the layered architecture of our ensemble model, from initial Level-0 models to advanced aggregation layers, highlighting the sequential prediction and refinement process.

Long Short-Term Memory (LSTM). The GRU incorporates a simplified gating mechanism to address the vanishing gradient problem [42], balancing computational efficiency with the ability to learn long-term dependencies. This advantage makes the GRU suitable for complex tasks such as language modeling and nuanced time-series analysis. Alternatively, LSTM selectively retains or forgets information [43], making it practical for extended sequences. Its capability to handle long-term dependencies makes LSTM ideal for challenging tasks, such as predictive text generation, advanced time series forecasting, and language translation.

5) CLASSIFICATION ANALYTICS Decision Trees are known to simplify complex decisionmaking. They created an intuitive, tree-like structure by segmenting datasets into branches based on feature values [44]. This method divides data into smaller, more manageable subsets, effectively handling nonlinear relationships among variables and facilitating hierarchical decision processes. A Support Vector Machine (SVM) is used in classification and regression tasks. It offers robust performance in highdimensional spaces owing to its margin maximization principle, which forms a hyperplane for data classification [45]. K-Nearest Neighbors (KNN) is an instance-based algorithm that classifies data by analyzing the majority class among its ‘‘K’’ nearest neighbors, relying on a similarity principle [46]. The algorithm’s accuracy is sensitive to the chosen number of neighbors and the specific distance metric applied, thereby impacting its adaptability to various data. Logistic Regression, essential for binary classification in machine learning [47], uses a logistic function to convert predictor variables into probabilities, thereby accommodating nonlinear variable relationships. In various fields, like medical diagnosis and spam detection, employing maximum likelihood estimation for coefficient calculation is pivotal. Neural Networks, inspired by the structure of biological neurons, are composed of complex interconnected layers of artificial neurons or nodes [48]. It begins with an input layer, includes one or more hidden layers, and ends with an output layer. Each node simulates a biological neuron, calculates a weighted sum of inputs, and applies a nonlinear transformation commonly termed the activation function.

6) EVALUATION METHOD The Root Mean Square Error (RMSE) is a critical metric for assessing regression tasks, quantifying the square root of the mean of the squared discrepancies between the predicted and actual values. By squaring the errors before averaging, the RMSE heavily penalizes the larger discrepancies, making it particularly sensitive to significant prediction errors. This characteristic enhances its utility in offering a precise measure of model accuracy. The formula is detailed in (1)

n X

RMSE =

---

## Page 5

FIGURE 3. cSysGuard architecture. This figure demonstrates the process of system preprocessing, data collection, performance metrics forecasting, health assessment, and continuous model refinement.

where yk represents the actual value, ˆyk denotes the predicted value, and n signifies the number of observations. A lower RMSE indicates better accuracy compared to a higher one. The F1 score is a key metric for evaluating classification tasks. It is computed by harmonically averaging precision, which is the ratio of true positives to all positive predictions, indicating the accuracy of positive classifications, and recall, the ratio of true positives to all actual positives, reflecting the ability to identify all relevant instances. These calculations are elaborated in (2), (3), and (4) for class n.

Precisionn = TPn TPn + FPn (2)

Recalln = TPn TPn + FNn (3)

F1-Scoren = 2 × Precisionn × Recalln

Precisionn + Recalln (4)

In addition to these equations, TP represents true positives, FP signifies false positives, and FN indicates false negatives. An F1 score of 1 signifies perfect precision and recall, indicating that all predictions are accurate and complete. Conversely, a score of 0 represents the lowest accuracy, where the model fails to identify any true positive values.

III. METHODOLOGY OVERVIEW This section provides a detailed overview of the methodology used in our study, focusing on the design and data handling of cSysGuard.

FIGURE 4. cSysGuard execution workflow. The figure illustrates cSysGuard’s operational sequence, which mainly encompasses the stages of preprocessing, data prediction, and model refinement.

simulation, data aggregator, controller, metrics and health predictor, ensemble refiner, and preprocessor. Each is integral to the prediction process. The following sections briefly describe the system workflow and each element, elucidating their functions and collaborative interactions.

---

## Page 6

predictors to generate and store the forecast. In addition to preserving model performance, the refinement process is activated at predefined intervals to utilize the latest dataset to align models with current data trends. Post-refinement, updated models are stored. This cycle of prediction and refinement recurs over time, ensuring cSysGuard’s processes are perpetually optimized and up-to-date.

2) APPLICATION SIMULATION This component emulates an application cloud environment, providing a means to acquire the dataset. The study leveraged Digital Ocean’s cloud service [49], deploying three Linux virtual machines [50], each with 1vCPU, 1GB of memory, and a 10GB disk. The API gateway is responsible for routing requests to the stateless application service, which utilizes a database for data storage. Our target service incorporates a monitoring tool called Prometheus [51] to collect and store metrics over time methodically. In addition, the simulator employs a custom script to simulate dynamic workloads, manipulating the intensity of various metrics in unique combinations for each request. For instance, one scenario may involve high CPU and memory usage with low usage in other metrics, whereas another could stress high bandwidth usage while keeping the rest low. This approach enables the model to evaluate the system’s performance under fluctuating conditions, focusing on randomness and swift changes. These assumptions mirror real-world cloud environments, enhancing the generalizability of cSysGuard by ensuring it can adapt to unpredictable and rapidly changing workloads.

3) DATA AGGREGATOR This component is responsible for updating and structuring the dataset for modeling and analysis. Initially, the process aggregates the system data from the application service and then transforms the metrics into a suitable format for predictive modeling. To enhance the accuracy of the forecasts, it also performs a noise reduction process to minimize data inconsistencies. Finally, the component forwards the processed dataset to the controller for further processing.

5) METRICS AND HEALTH PREDICTOR This component mainly oversees the prediction process, including forecasting system performance metrics and health assessments. Once activated by the controller, the prediction process is initiated with the most recent dataset as the input. Represented as an ensemble regression model, the first three layers—Level 0, Level 1, and Weight Aggregation—mainly focus on forecasting performance metrics, as detailed in Section IV. Besides, we incorporate several sets of predictors within the forecasting layers, with each set specializing in specific metrics. Upon completion, it consolidates and forwards the results to the final layer for system health assessment, requiring inputs from all metric sets for a thorough evaluation, as detailed in Section V. Moreover, each layer sends its predictions to the controller for storage, serving as valuable data for subsequent model evaluation and refinement. This component ensures precise and timely predictions through a comprehensive and systematic ensemble architecture.

6) ENSEMBLE REFINER This component maintains the regression model’s proficiency in identifying the trends and data characteristics. Upon activation by the controller, the refiner fine-tunes the Level-0 and Level-1 models by utilizing the latest dataset. Similarly, it adjusts the Level-1 weights based on the range of historical predictions, dynamically aligning the models’ strengths with their predictive efficacy. Once completed, the system promptly updates the repository with the newly refined model and weights. Through this iterative refinement, the component enhances the adaptability and precision of the models, ensuring they remain effective in a dynamic environment.

7) PREPROCESSOR This component is essential for setting up the models cSysGuard requires to initiate the primary process. The preprocessor commences by retrieving the list of models from the system configuration. Then, it actively compiles the models with predefined parameters and training datasets. Upon completion, the calibrated models are stored in the repository. However, the preprocessing step is optional if the repository already contains the models.

---

## Page 7

TABLE 1. Transformed system performance metrics dataset with server health in 40 seconds.

FIGURE 5. System performance metrics across different parameters. This figure displays a series of graphs that showcase CPU and memory requests, inbound and outbound bandwidth, transaction rates, and average response times, all measured over a 10-minute period.

FIGURE 6. Comparative predictions and RMSE with/without low-pass butterworth filter. This figure displays the 10-minute predictions for LSTM, GRU, and ARIMA models in CPU requests, illustrating the comparison between scenarios with filtered and unfiltered data.

Eventually, the system performs a noise reduction process utilizing a low-pass Butterworth filter to minimize data inconsistencies. To demonstrate an enhanced forecasting accuracy, Fig. 6 showcases the impact of noise reduction by contrasting the predictions and RMSE of LSTM, GRU, and ARIMA models using both noise-filtered and raw data inputs with actual values. It highlights the enhancement achieved by applying a filter to reduce noise. The process then yields and stores a well-refined dataset for further analysis.


=== DETECTED IMAGE-BASED TABLES ===

**Caption:** TABLE 1.

| CPU Request | Memory Request | Inbound Bandwidth (MB/s) | Outbound Bandwidth (MB/s) |
| :---------- | :------------- | :----------------------- | :------------------------ |
| 0.12        | 0.505          | 3160                     | 3430                      |
| 0.124       | 0.504          | 3590                     | 3120                      |
| 0.186       | 0.542          | 5920                     | 5290                      |
| 0.126       | 0.505          | 3530                     | 3900                      |
| 0.184       | 0.526          | 4890                     | 4310                      |
| 0.150       | 0.534          | 4610                     | 4090                      |
| 0.174       | 0.533          | 6250                     | 5490                      |
| 0.164       | 0.535          | 3490                     | 3150                      |

===================================

---

## Page 8

FIGURE 7. Regression prediction sequence. This figure displays the prediction cycle, integrating o observations and p forecast steps within a set interval k over n predictive cycles.

covers the intricacies of Level-0 and Level-1 learners, Weight Aggregation, and the approaches used for comparing models and tuning hyperparameters in regression models.

A. LEVEL-0 LEARNER Level-0 learners comprise base models designed for timeseries prediction that utilize datasets aggregated directly from the system for their training. At each predefined interval, these models use the most recent dataset to predict forthcoming values, considering two key elements: the predetermined count of past data points (observation steps) and the quantity of future data points (prediction steps) to be predicted. To illustrate, Fig. 7 visualizes the sequence of time series predictions, showcasing observation steps ‘‘o’’ and prediction steps ‘‘p’’ for each interval ‘‘k’’ across ‘‘n’’ predictions. cSysGuard allows the adjustment of these parameters to meet user-specific requirements. In this study, we configured the settings with 30 observation steps and five forecast steps, aligning the interval with the forecasting steps. Our setup has operated various models, including the ARIMA, SARIMA, ETS, CNN, TCN, RNN, GRU, and LSTM. Each brings a unique forecasting approach, enabling us to capture various aspects and patterns within the data. In addition to deep learning, we incorporated two hidden layers into the architecture: the first equipped with 64 neurons and the second with 32 neurons, both employing ReLU activation. We used the default settings provided by the Statsmodels [54] and TensorFlow [55] libraries. Despite this, we observed that the library’s default parameter values for deep learning led to suboptimal predictions. Therefore, parameter adjustments are required. Table 2 outlines the model-fitting configuration, ensuring the retention of initial learning proficiency of deep learning models. Upon prediction, the models forward the results to the subsequent layer, Level 1.

TABLE 2. Parameters influencing performance in deep learning model training.

This layer comprises three distinct models: Linear Regression, Random Forest, and Feedforward Neural Networks. Linear Regression provides simplicity and interoperability to effectively capture linear relationships within the data. Random Forest contributes to reducing overfitting and improving generalization. Feedforward Neural Networks excel at capturing complex, nonlinear patterns and interactions in the data. This combination leverages the strengths of each model, ensuring that the stacking approach can effectively generalize across different metrics and system behaviors to enhance the predictive accuracy and robustness of cSysGuard. For Linear Regression and Random Forest, we employed the standard parameters provided by the Scikit-learn library [56]. For Feedforward Neural Networks, we replicated the deep learning structure and model-fitting parameters of Level-0 models using the TensorFlow library. To optimally balance cSysGuard’s predictive performance and computational complexity, we adopted a selective approach to determine which Level-0 models would be fed into specific Level-1 models for predictions. The selection depends on the impact each model has on the predictive performance for particular metrics, evaluated by the Pearson correlation coefficient, r [58], which is defined as follows:

r = P(xi −¯x)(yi −¯y) pP(xi −¯x)2 P(yi −¯y)2 (5)


=== DETECTED IMAGE-BASED TABLES ===

**Caption:** TABLE 2.

| Adjusted Parameter | Values | Default |
| --- | --- | --- |
| Epochs | 50 | 1 |
| Batch Sizes | 32 | none |
| Default Parameter | Values |  |
| Shuffle | true |  |
| Validation Split | 0.0 |  |
| Validation Steps | none |  |
| Validation Batch Size | none |  |
| Validation Frequency | 1 |  |
| Initial Epoch | 0 |  |
| Steps Per Epoch | none |  |
| Callbacks | none |  |
| Class Weight | none |  |
| Sample Weight | none |  |

===================================

---

## Page 9

FIGURE 8. Incremental performance improvement in level-1 models. This figure illustrates RMSE progression for Level-1 models predicting CPU requests (unit: percent), highlighting the incremental performance enhancements achieved with each addition of a Level-0 model.

FIGURE 9. Correlation analysis of level-0 models in CPU request prediction. This figure ranks the base models based on the Pearson correlation scores.

FIGURE 10. Consolidated performance analysis of level-1 models. This figure synthesizes the RMSE achievements of Level-1 models in forecasting CPU requests (unit: percent), encapsulating the collective efficacy derived from integrating multiple Level-0 models.

C. WEIGHTED AGGREGATION LAYER The weighted aggregation layer is the final regression stage for predicting forthcoming metrics. To effectively leverage the contributions of each Level-1 model, the system receives predictive model outputs and refines the final prediction using a weight-averaging method [60] by assigning higher weights to more accurate models. In addition to the weight calculation, the layer computes the Performance Vector (PV) of Level-1 learners based on past t refinement iterations. The PV is represented as a 3 × t matrix:





PELR,1 PELR,2 · · · PELR,t

 (6)



PV =

PERF,1 PERF,2 · · · PERF,t

PEFF,1 PEFF,2 · · · PEFF,t

where it consolidates the prediction errors, measured by RMSE, for Linear Regression (LR), Random Forest (RF), and Feedforward Neural Networks (FF) across t refinement iterations. The refinement process enables ongoing updates to the model performance, ensuring sustained accuracy in a rapidly changing cloud environment. Nevertheless, incorporating the RMSE directly as weights presents a significant challenge, as it may not adequately reflect model correlations. A model with a slightly lower RMSE may not enhance the ensemble diversity if similar to another model. To mitigate this issue, we developed a normalized weighting system derived from the PV. The calculation scales the errors into normalized weights, identified as NormWeighti,j, converting them to a range between 0 and 1 for comparability across different models. The weight normalization formula is outlined in (7):

NormWeighti,j = exp(−α × PEi,j) P

k∈{LR,RF,FF} exp(−α × PEk,j) (7)

---

## Page 10

study aimed to maximize each weight value while ensuring that outcomes stayed within an acceptable range as controlled by α. This strategy allows for a more pronounced distinction in model weights, which is particularly beneficial when the models’ performances are nearly identical. To derive the final prediction, we integrated the outputs from our Level-1 learners through a weighted averaging approach. The final prediction for a given time point m, represented by Pm, is determined as (8):

Pm = X

k∈{LR,RF,FF} NormWeightk,j × Pk,m (8)

where each model’s prediction, denoted as Pk,m, is multiplied by its respective normalized weight, NormWeightk,m. This process guarantees that each model’s contribution to the final prediction is proportional to its performance. By harmonizing the models’ strengths, this approach yields a more precise and reliable ensemble forecast.

D. MODEL COMPARISON Our approach evaluated cSysGuard’s efficacy in forecasting system metrics by comparing its performance with traditional models used in the Level-0 layer. We utilized RMSE to compare and benchmark the performance across different metrics. This method clearly explains the precision and dependability of cSysGuard, emphasizing its capability to manage dynamic environments effectively.

TABLE 3. Range of hyperparameters for recurrent neural networks (RNN) and random forest (RF) tuning in CPU request analysis.

depth), minimum samples for a split (min sample split), minimum samples per leaf (min sample leaf), maximum number of features considered for splitting a node (max features), maximum number of leaf nodes (max-leaf nodes), minimum impurity decrease for a split (min impurity decrease), whether bootstrap samples are used (bootstrap), and the function to measure the quality of a split (criterion).

V. SYSTEM HEALTH ASSESSMENT This section describes the system health assessment approach, focusing on layer concepts, model comparisons, and hyperparameter tuning in the classification models.


=== DETECTED IMAGE-BASED TABLES ===

**Caption:** TABLE 3.

| Range of Hyperparameters for RNN (Level-0) | Range of Values |
| :--------------------------------------: | :-------------: |
|          Observation Steps             |       5 to 100    |
|          Learning Rate                  |     0.001 to 0.1  |
|          Number of Neurons in Layer 1   |       20 to 80    |
|          Number of Neurons in Layer 2   |       20 to 80    |
|          Activation Functions in Layer 1 | relu, tanh, sigmoid |
|          Activation Functions in Layer 2 | relu, tanh, sigmoid |
|          Epochs                          |       10 to 150   |
|          Batch Size                      |       16 to 64    |

| Range of Hyperparameters for RF (Level-1) | Range of Values |
| :--------------------------------------: | :-------------: |
|          Number of Estimators            |       10 to 1000  |
|          Min Sample Split                |       3 to 30    |
|          Min Sample Leaf                 |       2 to 20    |
|          Max Features                    |       1 to 20    |
|          Max Leaf Nodes                  |       10 to 1000  |
|          Min Impurity Decrease           |       0 to 0.1    |
|          Bootstrap                       |       true, false |
|          Criterion                        |       squared error, absolute error, poisson, friedman mse |

===================================

---

## Page 11

FIGURE 11. Sliding window technique in classification prediction. This figure demonstrates the sliding window technique for system health assessment, featuring the window size ws of regression predictions rp over n cycles, resulting in classification predictions cp.

data, leading to more accurate forecasts of future system conditions. In addition to the imbalanced nature of our dataset [63], characterized by a higher prevalence of ‘‘healthy’’ statuses, there is a risk of models favoring the majority class and underperforming on the crucial but rarer ‘‘unhealthy’’ class. To address this, we implemented SMOTE to enhance the representation of the minority class, thereby enhancing the model equity by creating synthetic instances of this class to improve its detection.

B. MODEL COMPARISON An essential aspect of our methodology is the comparative analysis of various machine learning models to assess their performance efficacy. For this analysis, we selected five prominent models: Decision Trees, Support Vector Machines, K-Nearest Neighbors, Logistic Regression, and Neural Networks. These models were initially performed with the default parameters provided by the Scikit-learn and TensorFlow libraries [55], [56]. In addition to Neural Networks, our configuration featured a two-layered structure: the first layer had six nodes using the ReLU activation function, and the second comprised a single node with a Sigmoid activation function. To enhance the model’s generalizability, the evaluation process employed 10-fold cross-validation, conducting several training rounds and validation on different data splits to derive the average scores. We utilized precision, recall, and F1 score with macro averaging [64], ensuring equal weighting of each category in the assessment throughout the cross-validation process. The model with the highest macroaveraged F1 score is the most optimal, as it demonstrates a balanced trade-off between precision and recall, with the specifics detailed in (9), (10), and (11).

Precisionmacro = Precisionhealthy + Precisionunhealthy

2 (9)

TABLE 4. Hyperparameter ranges in decision tree tuning.

F1-Scoremacro = 2 × Precisionmacro × Recallmacro

Precisionmacro + Recallmacro (11)

C. HYPERPARAMETER TUNING Subsequently, we carefully refined the model’s hyperparameters through Bayesian optimization to enhance its predictive capabilities with our dataset. We methodically tested a range of parameter values to identify the combination that resulted in the highest macro-averaged F1 score. This process allowed us to optimize the model’s accuracy and tailor the model specifically to the nuances of the dataset. Table 4 presents the hyperparameters of the Decision Trees, identified as the top-performing model in Section VI-B. These influential hyperparameters encompass max depth, min sample split, min sample leaf, criterion, max features, max-leaf nodes, and min impurity decrease.

VI. RESULT AND DISCUSSION This section presents our empirical findings for machinelearning models in system metrics and health forecasting. It also provides an insightful discussion of the findings.

A. SYSTEM METRICS FORECASTING EVALUATION This subsection details the experimental results of the system metrics forecasting, including two main categories: model comparison and hyperparameter tuning.


=== DETECTED IMAGE-BASED TABLES ===

**Caption:** TABLE 4.

| Parameter | Range of Values |
| --- | --- |
| Max Depth | 3 to 500 |
| Min Samples Split | 2 to 100 |
| Min Samples Leaf | 1 to 100 |
| Criterion | gini, entropy |
| Max Features | none, auto, sqrt, log2 |
| Max Leaf Nodes | 10 to 1000 |
| Min Impurity Decrease | 0 to 5 |

===================================

---

## Page 12

TABLE 5. RMSE-based performance comparison of cSysGuard with selected level-0 models across specific metrics.

FIGURE 12. System performance metrics prediction. This figure compares cSysGuard’s prediction results with those of commonly used models (GRU, RNN, LSTM, ARIMA, CNN) against actual results for CPU and memory requests, bandwidth, transaction rates, and response times.

tasks. These results demonstrate that cSysGuard effectively surpasses traditional models in certain areas, reinforcing its robustness and adaptability in diverse system-metric forecasting scenarios. Additionally, Fig. 12 visualizes the predicted values compared to the actual values for various metrics. Each graph compares the performance of cSysGuard with commonly used models such as GRU, RNN, LSTM, ARIMA, and CNN. The visualizations clarify cSysGuard’s predictive capabilities, highlighting its effectiveness in forecasting diverse system metrics. Given their alignment with performance benchmarks and the vast array of adjustable parameters, we opted for RNN and Random Forest as our Level-0 and Level-1 models in our optimization experiment.

TABLE 6. Optimal parameters for recurrent neural networks (RNN) and random forest (RF) tuning in CPU request analysis.

TABLE 7. RMSE-based performance of recurrent neural networks (RNN), random forest (RF), and cSysGuard in CPU request (unit: percent).

enhanced the predictive capabilities of the subsequent layers in the architecture. This finding suggests a synergistic effect, where refining one system component positively influences overall efficacy, thereby underscoring the interconnected nature of the models within the system.


=== DETECTED IMAGE-BASED TABLES ===

**Caption:** TABLE 5.

| cSysGuard | GRU | LSTM | RNN |
| --- | --- | --- | --- |
| **CPU Request (percent)** | 4.793 | 4.917 | 5.008 | 4.796 |
| **Memory Request (percent)** | 1.494 | 1.518 | 1.553 | 1.487 |
| **Inbound Bandwidth (MB/s)** | 2778 | 2795 | 2827 | 2787 |
| **Outbound Bandwidth (MB/s)** | 2368 | 2388 | 2416 | 2368 |
| **TPS** | 0.635 | 0.641 | 0.646 | 0.637 |
| **Response Time (ms)** | 640.2 | 649.1 | 665.7 | 642.3 |

===================================

**Caption:** TABLE 6.

| Optimal RNN (Level-0) Parameters | Value |
| --- | --- |
| Observation Steps | 64 |
| Learning Rate | 0.001 |
| Number of Neurons in Layer 1 | 49 |
| Number of Neurons in Layer 2 | 55 |
| Activation Functions in Layer 1 | relu |
| Activation Functions in Layer 2 | relu |
| Epochs | 100 |
| Batch Size | 16 |

| Optimal RF (Level-1) Parameters | Value |
| --- | --- |
| Number of Estimators | 545 |
| Max Depth | 27 |
| Min Sample Split | 5 |
| Min Sample Leaf | 10 |
| Max Features | auto |
| Max Leaf Nodes | 13 |
| Min Impurity Decrease | 0.00035269496460264014 |
| Bootstrap | true |
| Criterion | friedman mse |

===================================

**Caption:** TABLE 7.

| Base Performance | RNN | RF | cSysGuard |
| --- | --- | --- | --- |
| Level-0: Tuned RNN | 4.695 | 4.736 | 4.691 |
| Level-1: Tuned RF | 4.695 | 4.706 | 4.684 |

===================================

---

## Page 13

TABLE 8. Performance of base models and tuned decision trees in system health assessment.

TABLE 9. Optimal parameters for tuning decision trees.

1) MODEL COMPARISON Table 8 presents a comparative analysis of various base models’ performance, focusing on the macro-averaged precision, recall, and F1 score. The analysis reveals that the Decision Trees outperform the other base models by achieving the highest F1 score. This performance highlights its efficiency in accurately identifying positive instances while minimizing false positives, as evidenced by its high recall and precision. Such a balanced effectiveness profile underscores the suitability of Decision Trees for reliable system health status prediction, establishing it as a robust choice for such assessments. Based on the evaluation, we focused on Decision Trees for in-depth analysis during hyperparameter tuning.

FIGURE 13. Confusion matrix visualization for system health assessment. This figure illustrates the averaged confusion matrix, capturing the predictive accuracy of server status as healthy or unhealthy.

data, offering a transparent and quantifiable measure of cSysGuard’s predictive accuracy. The matrix delineates two principal classes indicative of server status: ‘‘healthy’’ and ‘‘unhealthy.’’ In this matrix, columns represent predicted labels, and rows correspond to actual labels. This graphical representation is crucial for evaluating the precision and reliability of our model in distinguishing the server’s operational states.


=== DETECTED IMAGE-BASED TABLES ===

**Caption:** TABLE 8.

| Base Performance | Macro-avg Precision | Macro-avg Recall | Macro-avg F1 Score |
| --- | --- | --- | --- |
| Decision Trees | 0.8856 | 0.8802 | 0.8812 |
| Support Vector Machine | 0.8255 | 0.8231 | 0.8223 |
| K-Nearest Neighbors | 0.8372 | 0.7819 | 0.7736 |
| Neural Networks | 0.8515 | 0.8159 | 0.8060 |
| Logistic Regression | 0.8380 | 0.8380 | 0.8368 |
| Optimal Performance | 0.9012 | 0.8968 | 0.8979 |

===================================

**Caption:** TABLE 9.

| Parameter | Values |
| --- | --- |
| Max Depth | 129 |
| Min Samples Split | 2 |
| Min Samples Leaf | 1 |
| Criterion | gini |
| Max Features | none |
| Max Leaf Nodes | 637 |
| Min Impurity Decrease | 0 |

===================================

---

## Page 14

TABLE 10. RMSE performance comparison: Single Meta-Model, CloudInsight, and cSysGuard (simple averaging: cSG-SA & weighted averaging: cSG-WA) across metrics.

their effectiveness and compare them to the cSysGuard architecture. Table 10 presents the comparative effectiveness of each methodology. Employing CloudInsight or a single metamodel does not match the performance efficacy of cSysGuard’s configuration (cSG-WA). Alternatively, while using a simple averaging strategy in cSysGuard (cSG-SA) aligns closely with the current version, the critical advantage of weighted averaging is its flexibility; it enables users to tailor weight calculations based on specific needs, such as Level-1 model error sensitivity or collected error range. This flexibility enhances overall performance to favor betterperforming models by fine-tuning their weights, emphasizing the importance of cSysGuard’s nuanced three-tier layering strategy.

TABLE 11. Comparative analysis of prediction and refinement times (unit: seconds) for Selected ML models and cSysGuard (cSG).

of the employed models and the capabilities of its operating machine.

E. SYSTEM SPECIFICATION BIAS As Section III-A2 outlined, our methodology deployed the system with specific configurations, including CPU type, memory capacity, and the operating system used. It is essential to acknowledge that differences in these specifications can influence the overall modeling process and its predictive outcomes. Such variations, in turn, can potentially affect the predictive accuracy and generalizability of cSysGuard. Therefore, the study recommends that users consider adjusting cSysGuard’s setup to suit their server specifications. Users can select different models and quantities, optimize parameters, fine-tune data configuration and prediction interval, or adjust Level-1 model error sensitivity. cSysGuard offers flexibility to align with users’ operational goals and requirements, maximizing the advantages of ensemble learning.


=== DETECTED IMAGE-BASED TABLES ===

**Caption:** TABLE 11.

| CloudInsight, and cSysGuard (simple averaging: cSSA & weighted averaging: cSG-WA) across metrics. | 1 Meta-Model (Mehmood et al.) | Cloud Insight (Kim et al.) | cSG-SA | cSG-WA |
| --- | --- | --- | --- | --- |
| CPU Request (percent) | 6.6708 | 4.9131 | 4.6914 | 4.6845 |
| Memory Request (percent) | 2.1594 | 1.5442 | 1.4943 | 1.4941 |
| Inbound Bandwidth (MB/s) | 4052.5 | 2887.4 | 2778.2 | 2777.6 |
| Outbound Bandwidth (MB/s) | 3536.6 | 2462.9 | 2369.0 | 2368.7 |
| TPS | 0.9117 | 0.6377 | 0.6346 | 0.6348 |
| Response Time (ms) | 978.21 | 780.79 | 640.41 | 640.20 |

| (unit: seconds) for Selected ML models and cSysGuard (cSG). | RNN | GRU | LSTM | cSG |
| --- | --- | --- | --- | --- |
| Prediction Process | 0.382 | 0.362 | 1.061 | 2.366 |
| Refinement Process (Parallel Training) | 74.29 | 132.40 | 141.84 | 152.55 |

===================================

**Caption:** TABLE 10.

| 1 Meta-Model | Cloud Insight | cSG-SA | cSG-WA |
| --- | --- | --- | --- |
| **CPU Request (percent)** | 6.6708 | 4.9131 | 4.6914 | 4.6845 |
| **Memory Request (percent)** | 2.1594 | 1.5442 | 1.4943 | 1.4941 |
| **Inbound Bandwidth (MB/s)** | 4052.5 | 2887.4 | 2778.2 | 2777.6 |
| **Outbound Bandwidth (MB/s)** | 3536.6 | 2462.9 | 2369.0 | 2368.7 |
| **TPS** | 0.9117 | 0.6377 | 0.6346 | 0.6348 |
| **Response Time (ms)** | 978.21 | 780.79 | 640.41 | 640.20 |

===================================

---

## Page 15

consider integrating other system failures, such as networkrelated issues, security breaches, and application-level errors. By addressing these additional dimensions, cSysGuard will become a more versatile framework adaptable to a broader range of scenarios and capable of providing comprehensive monitoring across various aspects of system health.

REFERENCES

---

## Page 16

[36] G. James, D. Witten, T. Hastie, and R. Tibshirani, ‘‘Linear regression,’’ in An Introduction to Statistical Learning (Springer Texts in Statistics). New York, NY, USA: Springer, 2021, doi: 10.1007/978-1-0716-1418-1_3. [37] Y. Liu, Y. Wang, and J. Zhang, ‘‘New machine learning algorithm: Random forest,’’ in Information Computing and Applications (Lecture Notes in Computer Science), vol. 7473, B. Liu, M. Ma, and J. Chang, Eds. Berlin, Germany: Springer, 2012, doi: 10.1007/978-3-642-34062-8. [38] S. Skansi, ‘‘Feedforward neural networks,’’ in Introduction to Deep Learning (Undergraduate Topics in Computer Science). Cham, Switzerland: Springer, 2018, doi: 10.1007/978-3-319-73004-2_4. [39] S. Tripathy and R. Singh, ‘‘Convolutional neural network: An overview and application in image classification,’’ in Proc. 3rd Int. Conf. Sustain. Comput., vol. 1404. Singapore: Springer, 2022, doi: 10.1007/978-981-164538-9_15. [40] C. Lea, R. Vidal, A. Reiter, and G. D. Hager, ‘‘Temporal convolutional networks: A unified approach to action segmentation,’’ in Proc. Comput. Vis. ECCV Workshops, in Lecture Notes in Computer Science, vol. 9915. Cham, Switzerland: Springer, 2016, pp. 47–54. [41] S. A. Marhon, C. J. F. Cameron, and S. C. Kremer, ‘‘Recurrent neural networks,’’ in Handbook on Neural Information Processing (Intelligent Systems Reference Library), vol. 49, M. Bianchini, M. Maggini, and L. Jain, Eds. Berlin, Heidelberg: Springer, 2013, doi: 10.1007/978-3-64236657-4_2. [42] S. Kostadinov. (Dec. 16, 2017). Understanding GRU Networks. Towards Data Sci. Accessed: Jan. 17, 2024. [Online]. Available: https://towardsdatascience.com/understanding-gru-networks2ef37df6c9be [43] K. Smagulova and A. P. James, ‘‘Overview of long short-term memory neural networks,’’ in Deep Learning Classifiers With Memristive Networks (Modeling and Optimization in Science and Technologies), vol. 14, A. James, Ed. Cham, Switzerland: Springer, 2020, doi: 10.1007/978-3030-14524-8_11. [44] J. R. Quinlan, ‘‘Induction of decision trees,’’ Mach. Learn., vol. 1, no. 1, pp. 81–106, Mar. 1986, doi: 10.1007/bf00116251. [45] C. Cortes and V. Vapnik, ‘‘Support-vector networks,’’ Mach. Learn., vol. 20, pp. 273–297, Jul. 1995, doi: 10.1007/BF00994018. [46] T. Cover and P. Hart, ‘‘Nearest neighbor pattern classification,’’ IEEE Trans. Inf. Theory, vol. IT-13, no. 1, pp. 21–27, Jan. 1967, doi: 10.1109/TIT.1967.1053964. [47] J. S. Cramer, ‘‘The origins and development of the logit model,’’ in Logit Models From Economics and Other Fields. Cambridge, U.K.: Cambridge Univ. Press, 2003, pp. 149–157, doi: 10.1017/CBO9780511615412.010. [48] B. Mer, J. Reinhardt, and M. T. Strickland, ‘‘Neural networks: An introduction,’’ in Physics of Neural Networks, 2nd ed. Berlin, Germany: Springer, 1995, doi: 10.1007/978-3-642-57760-4. [49] Digital Ocean. Accessed: Jan. 14, 2024. [Online]. Available: https://www.digitalocean.com [50] Google Cloud. What is a Virtual Machine? Accessed: Jan. 14, 2024. [Online]. Available: https://cloud.google.com/learn/what-is-a-virtualmachine [51] Prometheus. Accessed: Jun. 15, 2023. [Online]. Available: https:// prometheus.io [52] Zabbix. Accessed: May 26, 2023. [Online]. Available: https:// www.zabbix.com [53] MDN Web Docs: HTTP Response Status Codes. Accessed: Jun. 15, 2023. [Online]. Available: https://developer.mozilla.org/en-U.S./ docs/Web/HTTP/Status [54] Statsmodels. Accessed: Jan. 15, 2023. [Online]. Available: https://www. statsmodels.org [55] TensorFlow. Accessed: Jan. 15, 2023. [Online]. Available: https://www. tensorflow.org

[56] Scikit-learn. Accessed: Jan. 15, 2023. [Online]. Available: https://www. scikit-learn.org [57] N. Chairatana and R. Chawuthai, Jan. 31, 2024, ‘‘Cloud stateless system performance metrics and status,’’ IEEE Dataport, doi: 10.21227/8wf22y40. [58] S. Turney. (Jun. 22, 2023). Pearson Correlation Coefficient. Scribbr. Accessed: Jan. 15, 2024. [Online]. Available: https://www.scribbr.com/ statistics/pearson-correlation-coefficient [59] B. Saji. (2021). Elbow Method for Finding the Optimal Number of Clusters in K-Means. Analytics Vidhya. Accessed: Jan. 15, 2024. [Online]. Available: https://www.analyticsvidhya.com/blog/2021/01/indepth-intuition-of-k-means-clustering-algorithm-in-machine-learning [60] D. Schumacher. Understanding Weighted Average. SERP AI. Accessed: Jan. 15, 2024. [Online]. Available: https://serp.ai/weighted-average [61] ScienceDirect. Integer Overflow. Accessed: Jan. 15, 2024. [Online]. Available: https://www.sciencedirect.com/topics/computerscience/integer-overflow [62] W. Wang. (2020). Bayesian Optimization Concept Explained in Layman Terms. Towards Data Sci. Accessed: Jan. 15, 2024. [Online]. Available: https://towardsdatascience.com/bayesian-optimizationconcept-explained-in-layman-terms-1d2bcdeaf12f [63] J. Brownlee. (2020). A Gentle Introduction to Imbalanced Classification. Mach. Learn. Mastery. Accessed: Jun. 15, 2023. [Online]. Available: https://machinelearningmastery.com/what-is-imbalanced-classification [64] A. Tariq. (2023). What is the Difference Between Micro and Macro Averaging? Educative. Accessed: Jun. 15, 2023. [Online]. Available: https://www.educative.io/answers/what-is-the-difference-between-microand-macro-averaging

NUTT CHAIRATANA received the B.Eng. degree in computer innovation engineering from the King Mongkut’s Institute of Technology Ladkrabang, Bangkok, Thailand, in 2022, where he is currently pursuing the M.Eng. degree in robotics and computational intelligence systems with the Department of Robotics and AI Engineering. From 2022 to 2023, he was a Software Engineer with RentSpree. He is a Machine Learning Engineer with Kasikorn Business-Technology Group, Thailand.

RATHACHAI CHAWUTHAI received the B.Eng. degree in computer engineering from the King Mongkut’s Institute of Technology Ladkrabang, Bangkok, Thailand, in 2006; the M.Eng. degree in information management from Asian Institute of Technology, Pathum Thani, Thailand, in 2012; and the Ph.D. degree in informatics from SOKENDAI and National Institute of Informatics, Kanagawa, Japan, in 2016. From 2006 to 2010, he was a Software Engineer with Thomson Reuters. From 2012 to 2013, he was a Senior Software Engineer with Punsarn Asia. From 2013 to 2016, he was a Research Assistant with the National Institute of Informatics. He is currently an Assistant Professor with the King Mongkut’s Institute of Technology Ladkrabang.

---
