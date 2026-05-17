import numpy as np
from scipy.optimize import minimize

class IRTEngine2PL:
    """
    A 2-Parameter Logistic (2PL) Item Response Theory Engine.
    """

    @staticmethod
    def probability(theta, a, b):
        """
        Calculate the probability of a correct response under the 2PL model.
        
        Args:
            theta (float or np.array): Student ability.
            a (float or np.array): Item discrimination.
            b (float or np.array): Item difficulty.
            
        Returns:
            Probability of a correct response (0 to 1).
        """
        # Cap the exponent to prevent overflow
        z = np.clip(a * (theta - b), -700, 700)
        return 1.0 / (1.0 + np.exp(-z))

    @staticmethod
    def _log_likelihood_ability(theta, responses, a_params, b_params):
        """
        Negative log-likelihood function for estimating ability (theta).
        """
        p = IRTEngine2PL.probability(theta, a_params, b_params)
        # Add small epsilon to prevent log(0)
        p = np.clip(p, 1e-10, 1 - 1e-10)
        ll = np.sum(responses * np.log(p) + (1 - responses) * np.log(1 - p))
        return -ll # Return negative log-likelihood for minimization

    @staticmethod
    def estimate_ability(responses, a_params, b_params, initial_theta=0.0):
        """
        Estimate student ability (theta) using Maximum Likelihood Estimation (MLE).
        
        Args:
            responses (np.array): 1D array of 0s and 1s representing student answers.
            a_params (np.array): 1D array of item discriminations.
            b_params (np.array): 1D array of item difficulties.
            initial_theta (float): Starting value for optimization.
            
        Returns:
            float: Estimated theta.
        """
        # Ensure numpy arrays
        responses = np.array(responses)
        a_params = np.array(a_params)
        b_params = np.array(b_params)
        
        # MLE fails if all answers are correct or all are wrong (perfect scores)
        # In a real system, you'd use MAP (Maximum A Posteriori) with a prior, or cap scores.
        if np.all(responses == 1):
            return 3.0 # Arbitrary high ability cap
        if np.all(responses == 0):
            return -3.0 # Arbitrary low ability cap
            
        res = minimize(
            IRTEngine2PL._log_likelihood_ability, 
            x0=[initial_theta], 
            args=(responses, a_params, b_params),
            method='BFGS'
        )
        return res.x[0]

    @staticmethod
    def _log_likelihood_item(params, responses, thetas):
        """
        Negative log-likelihood function for estimating item parameters (a, b).
        params = [a, b]
        """
        a, b = params
        # Constrain 'a' to be positive
        if a <= 0.01:
            return 1e10
            
        p = IRTEngine2PL.probability(thetas, a, b)
        p = np.clip(p, 1e-10, 1 - 1e-10)
        
        # Handle missing data (np.nan) if present by using a mask
        mask = ~np.isnan(responses)
        ll = np.sum(responses[mask] * np.log(p[mask]) + (1 - responses[mask]) * np.log(1 - p[mask]))
        return -ll

    @staticmethod
    def calibrate_item(responses, thetas, initial_a=1.0, initial_b=0.0):
        """
        Estimate item parameters (a, b) given known student abilities (thetas).
        
        Args:
            responses (np.array): 1D array of responses (0, 1, or np.nan) from multiple students to a single item.
            thetas (np.array): 1D array of student abilities.
            
        Returns:
            tuple: (estimated_a, estimated_b)
        """
        res = minimize(
            IRTEngine2PL._log_likelihood_item,
            x0=[initial_a, initial_b],
            args=(responses, thetas),
            method='Nelder-Mead' # Robust for this kind of optimization
        )
        return res.x[0], res.x[1]

    @staticmethod
    def calibrate_bank(response_matrix, max_iter=5, tol=1e-3):
        """
        Joint Maximum Likelihood Estimation (JMLE) for calibrating both items and students iteratively.
        
        Args:
            response_matrix (np.array): 2D array of shape (num_students, num_items) containing 0s, 1s, or np.nan.
            
        Returns:
            tuple: (thetas, a_params, b_params)
        """
        num_students, num_items = response_matrix.shape
        
        # Initialize parameters
        thetas = np.zeros(num_students)
        a_params = np.ones(num_items)
        b_params = np.zeros(num_items)
        
        for iteration in range(max_iter):
            prev_thetas = thetas.copy()
            prev_b = b_params.copy()
            
            # 1. Estimate Items given current Thetas
            for j in range(num_items):
                item_responses = response_matrix[:, j]
                mask = ~np.isnan(item_responses)
                if np.sum(mask) > 0: # If item was answered by anyone
                    a, b = IRTEngine2PL.calibrate_item(item_responses, thetas)
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
                        initial_theta=thetas[i]
                    )
            
            # Check convergence
            theta_change = np.max(np.abs(thetas - prev_thetas))
            b_change = np.max(np.abs(b_params - prev_b))
            
            if theta_change < tol and b_change < tol:
                print(f"JMLE converged after {iteration+1} iterations.")
                break
                
        return thetas, a_params, b_params

