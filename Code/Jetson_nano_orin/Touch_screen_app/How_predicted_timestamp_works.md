The system determines the `expectedTimeDelta` by calculating a dynamically weighted moving average of historical light bulb flash deltas, followed by a linear projection against the current system time.

**Base Expected Time Delta Calculation**
The mathematical model shifts its weights based on the number of available historical flash events ($N$) stored in the system's `LIGHT_BULB_FLASH_DELTA_ARRAY`. If persistent settings fail to load or fall outside the bounds of **0** and **15.0**, the system defaults to a constant of **8.0**. Assuming valid live data, the generalized equation is:

$$E[\Delta t] = \sum_{i=1}^{\min(N, 5)} w_i^{(N)} \cdot \Delta t_i$$

Here, $\Delta t_i$ represents the recorded time gaps between flashes, ordered from the most recent ($i=1$) to the oldest ($i=5$). The specific piecewise definitions for these weights are:

* **When $N \ge 5$:** 
$$E[\Delta t] = 0.30\Delta t_1 + 0.25\Delta t_2 + 0.20\Delta t_3 + 0.15\Delta t_4 + 0.10\Delta t_5$$



* **When $N = 4$:** 
$$E[\Delta t] = 0.40\Delta t_1 + 0.25\Delta t_2 + 0.20\Delta t_3 + 0.15\Delta t_4$$



* **When $N = 3$:** 
$$E[\Delta t] = 0.60\Delta t_1 + 0.30\Delta t_2 + 0.10\Delta t_3$$



* **When $N = 2$:** 
$$E[\Delta t] = 0.70\Delta t_1 + 0.30\Delta t_2$$



* **When $N < 2$:** $E[\Delta t]$ strictly falls back to the most recent `actual_flash_delta` measurement without any weighted averaging.



**Missing Data Substitution**
If the script detects that an initial data point is missing in the sequence (flagged by `first_missing == True`), the algorithm intervenes by substituting the most recently computed prediction from `PREDICTED_TIME_DELTA_ARRAY` in place of the $\Delta t_1$ value before executing the weighted math.

**Forward Prediction Step**
Once the expected delta is established, the script calculates the exact predicted coordinate for the next anticipated flash. This relies on $t_{\text{currentRel}}$, which represents the system's relative epoch time since the application initially started:

$$t_{\text{nextFlash}} = t_{\text{currentRel}} + E[\Delta t]$$

This final predicted timestamp ($t_{\text{nextFlash}}$) is then pushed into the `PREDICTED_TIME_DELTA_ARRAY` to drive the system's analytical graphing functions.

Are you planning to test alternative weight distributions for these historical data points to handle sudden acceleration or deceleration?
