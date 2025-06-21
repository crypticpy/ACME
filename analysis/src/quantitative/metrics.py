"""Statistical metrics calculator with confidence intervals."""

from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.proportion import proportion_confint


class MetricsCalculator:
    """Calculate statistical metrics with proper confidence intervals."""
    
    @staticmethod
    def calculate_proportion_ci(
        successes: int, 
        n: int, 
        confidence: float = 0.95,
        method: str = "wilson"
    ) -> Tuple[float, float]:
        """
        Calculate confidence interval for a proportion.
        
        Args:
            successes: Number of successes
            n: Total number of trials
            confidence: Confidence level (default 0.95)
            method: Method to use ('wilson', 'normal', 'agresti_coull')
            
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        if n == 0:
            return (0.0, 0.0)
        
        if method == "wilson":
            # Wilson score interval (recommended for small samples)
            z = stats.norm.ppf(1 - (1 - confidence) / 2)
            p_hat = successes / n
            
            denominator = 1 + z**2 / n
            centre = (p_hat + z**2 / (2 * n)) / denominator
            margin = z * np.sqrt(p_hat * (1 - p_hat) / n + z**2 / (4 * n**2)) / denominator
            
            return (max(0, centre - margin), min(1, centre + margin))
        
        elif method == "normal":
            # Normal approximation (only for large samples)
            return proportion_confint(successes, n, alpha=1-confidence, method='normal')
        
        elif method == "agresti_coull":
            # Agresti-Coull interval
            return proportion_confint(successes, n, alpha=1-confidence, method='agresti_coull')
        
        else:
            raise ValueError(f"Unknown method: {method}")
    
    @staticmethod
    def calculate_mean_ci(
        data: Union[List[float], np.ndarray, pd.Series],
        confidence: float = 0.95
    ) -> Dict[str, float]:
        """
        Calculate confidence interval for a mean.
        
        Args:
            data: Numeric data
            confidence: Confidence level (default 0.95)
            
        Returns:
            Dictionary with mean, ci_lower, ci_upper, std_error
        """
        data = np.array(data)
        data = data[~np.isnan(data)]  # Remove NaN values
        
        if len(data) == 0:
            return {
                "mean": np.nan,
                "ci_lower": np.nan,
                "ci_upper": np.nan,
                "std_error": np.nan,
                "n": 0
            }
        
        mean = np.mean(data)
        std_error = stats.sem(data)
        ci = stats.t.interval(confidence, len(data) - 1, mean, std_error)
        
        return {
            "mean": mean,
            "ci_lower": ci[0],
            "ci_upper": ci[1],
            "std_error": std_error,
            "n": len(data)
        }
    
    @staticmethod
    def calculate_bootstrap_ci(
        data: Union[List[float], np.ndarray],
        statistic_func: callable,
        confidence: float = 0.95,
        n_bootstrap: int = 10000
    ) -> Dict[str, float]:
        """
        Calculate bootstrap confidence interval for any statistic.
        
        Args:
            data: Input data
            statistic_func: Function to calculate the statistic
            confidence: Confidence level
            n_bootstrap: Number of bootstrap samples
            
        Returns:
            Dictionary with statistic value and confidence interval
        """
        data = np.array(data)
        n = len(data)
        
        # Calculate the statistic on original data
        original_stat = statistic_func(data)
        
        # Bootstrap
        bootstrap_stats = []
        for _ in range(n_bootstrap):
            bootstrap_sample = np.random.choice(data, size=n, replace=True)
            bootstrap_stats.append(statistic_func(bootstrap_sample))
        
        # Calculate percentiles
        alpha = 1 - confidence
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100
        
        ci_lower = np.percentile(bootstrap_stats, lower_percentile)
        ci_upper = np.percentile(bootstrap_stats, upper_percentile)
        
        return {
            "statistic": original_stat,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "bootstrap_std": np.std(bootstrap_stats),
            "n_bootstrap": n_bootstrap
        }
    
    @staticmethod
    def calculate_difference_ci(
        group1: Union[List[float], np.ndarray],
        group2: Union[List[float], np.ndarray],
        confidence: float = 0.95,
        method: str = "t-test"
    ) -> Dict[str, float]:
        """
        Calculate confidence interval for difference between two groups.
        
        Args:
            group1: First group data
            group2: Second group data
            confidence: Confidence level
            method: Method to use ('t-test', 'mann-whitney')
            
        Returns:
            Dictionary with difference, CI, and test statistics
        """
        group1 = np.array(group1)[~np.isnan(group1)]
        group2 = np.array(group2)[~np.isnan(group2)]
        
        if method == "t-test":
            # Two-sample t-test
            mean_diff = np.mean(group1) - np.mean(group2)
            
            # Pooled standard deviation
            n1, n2 = len(group1), len(group2)
            var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
            pooled_se = np.sqrt(var1/n1 + var2/n2)
            
            # Degrees of freedom (Welch's t-test)
            df = (var1/n1 + var2/n2)**2 / ((var1/n1)**2/(n1-1) + (var2/n2)**2/(n2-1))
            
            # Confidence interval
            t_critical = stats.t.ppf(1 - (1 - confidence) / 2, df)
            ci_lower = mean_diff - t_critical * pooled_se
            ci_upper = mean_diff + t_critical * pooled_se
            
            # Test statistic
            t_stat = mean_diff / pooled_se
            p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df))
            
            return {
                "difference": mean_diff,
                "ci_lower": ci_lower,
                "ci_upper": ci_upper,
                "t_statistic": t_stat,
                "p_value": p_value,
                "df": df,
                "method": "Welch's t-test"
            }
        
        elif method == "mann-whitney":
            # Mann-Whitney U test (non-parametric)
            statistic, p_value = stats.mannwhitneyu(group1, group2, alternative='two-sided')
            
            # Effect size (rank-biserial correlation)
            n1, n2 = len(group1), len(group2)
            r = 1 - (2 * statistic) / (n1 * n2)
            
            # Bootstrap CI for median difference
            def median_diff(x, y):
                return np.median(x) - np.median(y)
            
            bootstrap_diffs = []
            for _ in range(1000):
                boot1 = np.random.choice(group1, size=n1, replace=True)
                boot2 = np.random.choice(group2, size=n2, replace=True)
                bootstrap_diffs.append(median_diff(boot1, boot2))
            
            ci_lower = np.percentile(bootstrap_diffs, (1 - confidence) / 2 * 100)
            ci_upper = np.percentile(bootstrap_diffs, (1 + confidence) / 2 * 100)
            
            return {
                "median_difference": median_diff(group1, group2),
                "ci_lower": ci_lower,
                "ci_upper": ci_upper,
                "u_statistic": statistic,
                "p_value": p_value,
                "effect_size_r": r,
                "method": "Mann-Whitney U test"
            }
    
    @staticmethod
    def calculate_correlation_ci(
        x: Union[List[float], np.ndarray],
        y: Union[List[float], np.ndarray],
        confidence: float = 0.95,
        method: str = "pearson"
    ) -> Dict[str, float]:
        """
        Calculate confidence interval for correlation coefficient.
        
        Args:
            x, y: Two variables to correlate
            confidence: Confidence level
            method: 'pearson' or 'spearman'
            
        Returns:
            Dictionary with correlation and CI
        """
        # Remove missing values
        mask = ~(np.isnan(x) | np.isnan(y))
        x = np.array(x)[mask]
        y = np.array(y)[mask]
        
        n = len(x)
        
        if method == "pearson":
            r, p_value = stats.pearsonr(x, y)
            
            # Fisher z-transformation for CI
            z = 0.5 * np.log((1 + r) / (1 - r))
            se = 1 / np.sqrt(n - 3)
            z_critical = stats.norm.ppf(1 - (1 - confidence) / 2)
            
            ci_lower_z = z - z_critical * se
            ci_upper_z = z + z_critical * se
            
            # Transform back
            ci_lower = (np.exp(2 * ci_lower_z) - 1) / (np.exp(2 * ci_lower_z) + 1)
            ci_upper = (np.exp(2 * ci_upper_z) - 1) / (np.exp(2 * ci_upper_z) + 1)
            
        elif method == "spearman":
            r, p_value = stats.spearmanr(x, y)
            
            # Bootstrap CI for Spearman correlation
            bootstrap_corrs = []
            for _ in range(1000):
                indices = np.random.choice(n, size=n, replace=True)
                bootstrap_corrs.append(stats.spearmanr(x[indices], y[indices])[0])
            
            ci_lower = np.percentile(bootstrap_corrs, (1 - confidence) / 2 * 100)
            ci_upper = np.percentile(bootstrap_corrs, (1 + confidence) / 2 * 100)
        
        return {
            "correlation": r,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "p_value": p_value,
            "n": n,
            "method": method
        }
    
    @staticmethod
    def calculate_sample_size(
        effect_size: float,
        power: float = 0.8,
        alpha: float = 0.05,
        test_type: str = "two-sample"
    ) -> int:
        """
        Calculate required sample size for statistical power.
        
        Args:
            effect_size: Expected effect size (Cohen's d)
            power: Desired statistical power
            alpha: Significance level
            test_type: 'two-sample', 'one-sample', or 'correlation'
            
        Returns:
            Required sample size
        """
        from statsmodels.stats.power import (
            tt_ind_solve_power, tt_solve_power, zt_ind_solve_power
        )
        
        if test_type == "two-sample":
            n = tt_ind_solve_power(
                effect_size=effect_size,
                power=power,
                alpha=alpha,
                ratio=1.0,
                alternative='two-sided'
            )
            return int(np.ceil(n))
        
        elif test_type == "one-sample":
            n = tt_solve_power(
                effect_size=effect_size,
                power=power,
                alpha=alpha,
                alternative='two-sided'
            )
            return int(np.ceil(n))
        
        elif test_type == "correlation":
            # For correlation, effect size is r
            z = 0.5 * np.log((1 + effect_size) / (1 - effect_size))
            z_alpha = stats.norm.ppf(1 - alpha / 2)
            z_beta = stats.norm.ppf(power)
            n = ((z_alpha + z_beta) / z) ** 2 + 3
            return int(np.ceil(n))
        
        else:
            raise ValueError(f"Unknown test type: {test_type}")