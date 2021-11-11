# MLF_Final_project
For MLF final project
## Proposal:XGBOOST model for slecting impotant features of stock and forming  unlinear factor 
### Motivation
We know that maching learning can be use to select important features for predictding stocks' performance.In factor investment, people want to find factors that is highly correlated with the return of stock, so we want to use machinglearning to  select the important factors.Besides, when we use the maching learning model to predict the performance of the stock, the prediction itself can be seen as a factor, because if maching learning model works,then the return of investment based on the prediction should be highly correlated with model's prediction.So we want to use maching learning model to produce a factor.
### Goal
1.select important features of stock by maching learning.  
2.Forming a factor of stock by maching learning.
### Introdcution of XGBOOST
XGBOOST is an improvement of GBDT.It uses the residual of the fommer model to tarin the next model, the reason we choose XGBoost is that it is more effecient.  
#### The procedure picture of XGBOOST
![image text](https://github.com/RAY185/MLF_Final_project/blob/main/result_summary_img/363bb7633db44dc6a7b801941326631.png)
### Data source
We select 18 features data of all A-shares on the last trading day of each month from 2010 to 2020 from Wind.We also get the return data of stock and index SH300 and the data  about wether the stock is on list or suspended from trading form Wind. 
### Label the data and form the training set and test set 
We lable stock according to its return.The top 30 percent of stocks are marked as 1, the bottom 30 percent as -1.Then combine them as sample for each period.  
We take sample in (t,t+5) as the training set and t+1 as the test set,where t is from 2010 to 2014. In the training set, we randomly select 90% as training set,10% as validation set.  
For each period we eliminate the stock that has been listed within 3 months, and the stock that has been suspended from trading.
### Valuation of the model 
We valuate the model by the accutacy rate and AUC. Besides, we do backtest on the features to see wether it is consisitent with the importance score the model give.And we also do backtest on the predict score the model give,which can be interprate as as the probability of the stock's label being 1.The backtest framework is a single factor test framework, and we mainly use the IC_IR ration and long-short return evaluation the effectiveness of the factor(feature). 
### Result at present(need change)
#### Average accuracy and auc
![image text](https://github.com/RAY185/MLF_Final_project/blob/main/result_summary_img/82071ea694abc377282ef994e907471.png)
#### Relationship between importance and IC_IR
![image text](https://github.com/RAY185/MLF_Final_project/blob/main/result_summary_img/473a32f914178b92667ed7267edf3ed.png)
#### IC_IR and long_short return of predict_score factor
![image text](https://github.com/RAY185/MLF_Final_project/blob/main/result_summary_img/IC_predict_score_final_m.png)
![image text](https://github.com/RAY185/MLF_Final_project/blob/main/result_summary_img/L-S_predict_score_final_m.png)
