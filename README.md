# MLF_Final_project
For MLF final project
## Proposal:XGBOOST model for slecting impotant features of stock and forming  unlinear factor 
### Motivation
We know that maching learning can be use to select important features for predictding stocks' performance.In factor investment, people want to find factors that is highly correlated with the return of stock, so we want to use machinglearning to  select the important factors.Besides, when we use the maching learning model to predict the performance of the stock, the prediction itself can be seen as a factor, because if maching learning model works,then the return of investment based on the prediction should be highly correlated with model's prediction.So we want to use maching learning model to produce a factor.
### Goal  
1.Compare different boosting model.  
2.select important features of stock by machine learning.  
3.Forming a factor of stock by maching learning.
### Data source
We select 32 features data of all A-shares on the last trading day of each month from 2010 to 2020 from Wind.We also get the return data of stock and index SH300 and the data  about wether the stock is on list or suspended from trading form Wind. 
#### Features selected  
![image text](https://github.com/RAY185/MLF_Final_project/blob/main/result_summary_img/features_selected.png)
### Label the data and form the training set and test set 
We lable stock according to its return.The top 30 percent of stocks are marked as 1, the bottom 30 percent as -1.Then combine them as sample for each period.  
We take sample in (t,t+5) as the training set and t+6 as the test set,where t is from 2010 to 2014. In the training set, we randomly select 90% as training set,10% as validation set.  
For each period we eliminate the stock that has been listed within 3 months, and the stock that has been suspended from trading.
### Valuation of the model 
We valuate the model by the accutacy rate and AUC. Besides, we do backtest on the features to see wether it is consisitent with the importance score the model give.And we also do backtest on the predict score the model give,which can be interprate as as the probability of the stock's label being 1.The backtest framework is a single factor test framework, and we mainly use the IC_IR ration and long-short return evaluation the effectiveness of the factor(feature). 
### Result analysis
#### Average accuracy and auc
#### accuracy and auc of XGBoosting with optimized hyper-parameter
![image text](https://github.com/RAY185/MLF_Final_project/blob/main/result_summary_img/accuracy%20and%20auc%20of%20XGBoosting.png)  
#### accuracy and auc of Adaboost with optimized hyper-parameter  
![image text](https://github.com/RAY185/MLF_Final_project/blob/main/result_summary_img/accuracy%20and%20auc%20of%20Adaboosting.png)  
#### accuracy and auc of GBDT with optimized hyper-parameter  
![image text](https://github.com/RAY185/MLF_Final_project/blob/main/result_summary_img/accuracy%20and%20auc%20of%20GBDT.png)  
In general, the accuracy and auc of these three models is not high, among which XGBoosting is the best and Adaboosting is the worst.  
#### Relationship between importance and IC_IR  
We choose the most important 3 features and the least imprtant 3 features to do the single factor bactest to see whether their performance is consistent with the imprtance given by XGBoosting model with optimal hyper-parameter. The result shows that as the importance decrease the IC_IR ratiao decrease, which shows the performance of the feature is consistent with the model given importance.    
![image text](https://github.com/RAY185/MLF_Final_project/blob/main/result_summary_img/absolute%20IC_IR%20ratio.png)
#### IC_IR and long_short return of predict_score factor
![image text](https://github.com/RAY185/MLF_Final_project/blob/main/result_summary_img/IC_predict_score_final_m.png)
![image text](https://github.com/RAY185/MLF_Final_project/blob/main/result_summary_img/L-S_predict_score_final_m.png)  
When we use the predict_score as a 'factor', the result shows it is better than other single feature.We can think it as an unlinearly conbined feature. In our experiment, it shows that we can get a better 'factor' by using machine learning to combine some factors.
