import numpy as np
from scipy.optimize import minimize

class IRTEngine2PL:
    """
    A 2/3-Parameter Logistic (2PL/3PL) Item Response Theory Engine.
    Supports both 2PL and 3PL models via the guessing parameter c.
    
    2PL: P(θ) = 1 / (1 + e^(-a(θ - b)))
    3PL: P(θ) = c + (1 - c) / (1 + e^(-a(θ - b)))
    """

    @staticmethod
    def probability(theta, a, b, c=0.0):
        """
        Calculate the probability of a correct response under the 2PL/3PL model.
        
        Args:
            theta (float or np.array): Student ability.
            a (float or np.array): Item discrimination.
            b (float or np.array): Item difficulty.
            c (float or np.array): Guessing parameter (default 0.0 for 2PL).
            
        Returns:
            Probability of a correct response (0 to 1).
        """
        # Cap the exponent to prevent overflow
        z = np.clip(a * (theta - b), -700, 700)
        p_star = 1.0 / (1.0 + np.exp(-z))
        return c + (1.0 - c) * p_star

    @staticmethod
    def _log_likelihood_ability(theta, responses, a_params, b_params, c_params):
        """
        Negative log-likelihood function for estimating ability (theta).
        Supports 3PL model with guessing parameter.
        """
        p = IRTEngine2PL.probability(theta, a_params, b_params, c_params)
        # Add small epsilon to prevent log(0)
        p = np.clip(p, 1e-10, 1 - 1e-10)
        ll = np.sum(responses * np.log(p) + (1 - responses) * np.log(1 - p))
        return -ll # Return negative log-likelihood for minimization

    @staticmethod
    def estimate_ability(responses, a_params, b_params, c_params=None, initial_theta=0.0):
        """
        Estimate student ability (theta) using Maximum Likelihood Estimation (MLE).
        
        Args:
            responses (np.array): 1D array of 0s and 1s representing student answers.
            a_params (np.array): 1D array of item discriminations.
            b_params (np.array): 1D array of item difficulties.
            c_params (np.array or None): 1D array of guessing parameters. Defaults to 0.0 (2PL).
            initial_theta (float): Starting value for optimization.
            
        Returns:
            float: Estimated theta.
        """
        # Ensure numpy arrays
        responses = np.array(responses)
        a_params = np.array(a_params)
        b_params = np.array(b_params)
        
        if c_params is None:
            c_params = np.zeros_like(a_params)
        else:
            c_params = np.array(c_params)
        
        # MLE fails if all answers are correct or all are wrong (perfect scores)
        # In a real system, you'd use MAP (Maximum A Posteriori) with a prior, or cap scores.
        if np.all(responses == 1):
            return 3.0 # Arbitrary high ability cap
        if np.all(responses == 0):
            return -3.0 # Arbitrary low ability cap
            
        res = minimize(
            IRTEngine2PL._log_likelihood_ability, 
            x0=[initial_theta], 
            args=(responses, a_params, b_params, c_params),
            method='BFGS'
        )
        return res.x[0]

    @staticmethod
    def _log_likelihood_item(params, responses, thetas, model='3PL'):
        """
        Negative log-likelihood function for estimating item parameters.
        
        For 2PL: params = [a, b]
        For 3PL: params = [a, b, c]
        """
        if model == '3PL':
            a, b, c = params
            # Constrain 'c' to [0, 0.5] range (reasonable guessing bounds)
            if c < 0.0 or c > 0.5:
                return 1e10
        else:
            a, b = params
            c = 0.0
            
        # Constrain 'a' to be positive
        if a <= 0.01:
            return 1e10
            
        p = IRTEngine2PL.probability(thetas, a, b, c)
        p = np.clip(p, 1e-10, 1 - 1e-10)
        
        # Handle missing data (np.nan) if present by using a mask
        mask = ~np.isnan(responses)
        ll = np.sum(responses[mask] * np.log(p[mask]) + (1 - responses[mask]) * np.log(1 - p[mask]))
        return -ll

    @staticmethod
    def calibrate_item(responses, thetas, initial_a=1.0, initial_b=0.0, initial_c=0.25, model='3PL'):
        """
        Estimate item parameters (a, b, c) given known student abilities (thetas).
        
        Args:
            responses (np.array): 1D array of responses (0, 1, or np.nan) from multiple students to a single item.
            thetas (np.array): 1D array of student abilities.
            initial_a (float): Starting discrimination value.
            initial_b (float): Starting difficulty value.
            initial_c (float): Starting guessing value (only used in 3PL).
            model (str): '2PL' or '3PL'.
            
        Returns:
            tuple: (estimated_a, estimated_b) for 2PL or (estimated_a, estimated_b, estimated_c) for 3PL.
        """
        if model == '3PL':
            x0 = [initial_a, initial_b, initial_c]
        else:
            x0 = [initial_a, initial_b]
            
        res = minimize(
            IRTEngine2PL._log_likelihood_item,
            x0=x0,
            args=(responses, thetas, model),
            method='Nelder-Mead' # Robust for this kind of optimization
        )
        
        if model == '3PL':
            a, b, c = res.x
            return a, b, np.clip(c, 0.0, 0.5)
        else:
            return res.x[0], res.x[1]

    @staticmethod
    def calibrate_bank(response_matrix, max_iter=5, tol=1e-3, model='3PL'):
        """
        Joint Maximum Likelihood Estimation (JMLE) for calibrating both items and students iteratively.
        
        Args:
            response_matrix (np.array): 2D array of shape (num_students, num_items) containing 0s, 1s, or np.nan.
            max_iter (int): Maximum number of JMLE iterations.
            tol (float): Convergence tolerance.
            model (str): '2PL' or '3PL'.
            
        Returns:
            tuple: (thetas, a_params, b_params) for 2PL or (thetas, a_params, b_params, c_params) for 3PL.
        """
        num_students, num_items = response_matrix.shape
        
        # Initialize parameters
        thetas = np.zeros(num_students)
        a_params = np.ones(num_items)
        b_params = np.zeros(num_items)
        c_params = np.full(num_items, 0.25) if model == '3PL' else np.zeros(num_items)
        
        for iteration in range(max_iter):
            prev_thetas = thetas.copy()
            prev_b = b_params.copy()
            
            # 1. Estimate Items given current Thetas
            for j in range(num_items):
                item_responses = response_matrix[:, j]
                mask = ~np.isnan(item_responses)
                if np.sum(mask) > 0: # If item was answered by anyone
                    if model == '3PL':
                        a, b, c = IRTEngine2PL.calibrate_item(
                            item_responses, thetas, 
                            initial_a=a_params[j], initial_b=b_params[j], initial_c=c_params[j],
                            model='3PL'
                        )
                        c_params[j] = np.clip(c, 0.0, 0.5)
                    else:
                        a, b = IRTEngine2PL.calibrate_item(
                            item_responses, thetas,
                            initial_a=a_params[j], initial_b=b_params[j],
                            model='2PL'
                        )
                    a_params[j] = np.clip(a, 0.1, 3.0) # Reasonable bounds for a
                    b_params[j] = np.clip(b, -3.0, 3.0) # Reasonable bounds for b
            
            # 2. Recenter b_params to anchor the scale (Mean of b = 0)
            # This is crucial in JMLE to solve the identifiability problem
            b_mean = np.mean(b_params)
            b_params = b_params - b_mean
            
            # 3. Estimate Thetas given current Items
            for i in range(num_students):
                student_responses = response_matrix[i, :]
                mask = ~np.isnan(student_responses)
                if np.sum(mask) > 0:
                    thetas[i] = IRTEngine2PL.estimate_ability(
                        student_responses[mask], 
                        a_params[mask], 
                        b_params[mask],
                        c_params[mask] if model == '3PL' else None,
                        initial_theta=thetas[i]
                    )
            
            # Check convergence
            theta_change = np.max(np.abs(thetas - prev_thetas))
            b_change = np.max(np.abs(b_params - prev_b))
            
            if theta_change < tol and b_change < tol:
                print(f"JMLE converged after {iteration+1} iterations.")
                break
        
        if model == '3PL':
            return thetas, a_params, b_params, c_params
        else:
            return thetas, a_params, b_params
