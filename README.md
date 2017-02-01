# MatrixFactorization

## 1. naive mf
矩阵分解：
$$\mathbf{R} \approx \mathbf{P} \times \mathbf{Q}^T = \hat{\mathbf{R}}$$

令：
$$\hat{r}_{ij} = p_i^T q_j = \sum_{k=1}^k{p_{ik}q_{kj}}$$

Loss Function：
$$e_{ij}^2 = (r_{ij} - \hat{r}_{ij})^2 = (r_{ij} - \sum_{k=1}^K{p_{ik}q_{kj}})^2$$

求梯度：
$$\frac{\partial}{\partial p_{ik}}e_{ij}^2 = -2(r_{ij} - \hat{r}_{ij})(q_{kj}) = -2 e_{ij} q_{kj}$$

$$  \frac{\partial}{\partial q_{ik}}e_{ij}^2 = -2(r_{ij} - \hat{r}_{ij})(p_{ik}) = -2 e_{ij} p_{ik}$$

得到更新法则：
$$p'_{ik} = p_{ik} + \alpha \frac{\partial}{\partial p_{ik}}e_{ij}^2 = p_{ik} + 2\alpha e_{ij} q_{kj} $$

$$q'_{kj} = q_{kj} + \alpha \frac{\partial}{\partial q_{kj}}e_{ij}^2 = q_{kj} + 2\alpha e_{ij} p_{ik} $$

加入正则项：
$$e_{ij}^2 = (r_{ij} - \sum_{k=1}^K{p_{ik}q_{kj}})^2 + \frac{\beta}{2} \sum_{k=1}^K{(||P||^2 + ||Q||^2)}$$

新的更新法则：
$$p'_{ik} = p_{ik} + \alpha \frac{\partial}{\partial p_{ik}}e_{ij}^2 = p_{ik} + \alpha(2 e_{ij} q_{kj} - \beta p_{ik} )$$

$$q'_{kj} = q_{kj} + \alpha \frac{\partial}{\partial q_{kj}}e_{ij}^2 = q_{kj} + \alpha(2 e_{ij} p_{ik} - \beta q_{kj} )$$

## 2. MF via ADMM

$$
\begin{align}
	({U}_{*i} )_{t+1} & =  ({U}_{*i})_t + \tau_t (\epsilon_{i,j} ({V}_{*j}^p )_t - \lambda_1({U}_{*i} )_t )\\
	({V}_{*j}^p )_{t+1} & =  \frac{\tau_t}{1+\rho \tau_t} \left [ \frac{1 - \lambda_2\tau_t}{1+\rho\tau_t} ({V}_{*j}^p)_t + \epsilon_{i,j}({U}_{*i})_t + \rho({\bar{V}}_{*j} )_t - (\Theta_{*j}^p )_t \right ] \\
	{\bar{V}}_{t+1} & =  \frac{1}{P} \sum_{p=1}^P {V}_{t+1}^p \\
	{\Theta}_{t+1}^p & =   {\Theta}_t^p + \rho({V}_{t+1}^p - {\bar{V}}_{t+1}) \\
	\epsilon_{i,j} & =  R_{i,j} - \left [ ({U}_{*i})_t \right ]^T ({V}_{*j}^p)_t 
\end{align}
$$





