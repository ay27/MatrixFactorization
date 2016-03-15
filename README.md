# MatrixFactorization

### 1. naive mf
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
