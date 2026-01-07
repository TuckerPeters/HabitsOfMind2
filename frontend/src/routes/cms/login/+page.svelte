<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { authToken, authApi } from '$lib/api/cmsApi.js';
  import { authFunctions } from '$lib/stores/auth.js';

  let email = '';
  let password = '';
  let error = '';
  let loading = false;
  let showResetPassword = false;
  let resetSuccess = false;
  let resetError = '';

  onMount(() => {
    // If already logged in to CMS, redirect to dashboard
    if ($authToken) {
      goto('/cms');
    }
  });

  async function handleLogin(e) {
    e.preventDefault();
    error = '';
    loading = true;

    try {
      const result = await authApi.login(email, password);

      // Only redirect if login was successful
      if (result && result.success) {
        goto('/cms');
      } else {
        // Should not reach here due to throw, but just in case
        error = result?.error || 'Login failed. Please check your credentials.';
      }
    } catch (err) {
      // Handle authentication failures with specific error messages
      const errorCode = err.code;

      if (errorCode === 'auth/user-not-found' || errorCode === 'auth/wrong-password') {
        error = 'Invalid email or password. Please try again.';
      } else if (errorCode === 'auth/invalid-email') {
        error = 'Invalid email address format.';
      } else if (errorCode === 'auth/user-disabled') {
        error = 'This account has been disabled. Please contact support.';
      } else if (errorCode === 'auth/too-many-requests') {
        error = 'Too many failed login attempts. Please try again later.';
      } else if (err.message?.includes('Not authorized as admin')) {
        error = 'Access denied. You do not have admin privileges.';
      } else {
        error = err.message || 'Login failed. Please check your credentials.';
      }

      // Clear the password field for security
      password = '';
    } finally {
      loading = false;
    }
  }

  async function handleResetPassword(e) {
    e.preventDefault();
    resetError = '';
    resetSuccess = false;
    loading = true;

    try {
      const result = await authFunctions.resetPassword(email);

      if (result.success) {
        resetSuccess = true;
        // Clear the form after 5 seconds and go back to login
        setTimeout(() => {
          showResetPassword = false;
          resetSuccess = false;
          email = '';
        }, 5000);
      } else {
        resetError = result.error || 'Failed to send password reset email.';
      }
    } catch (err) {
      resetError = err.message || 'Failed to send password reset email.';
    } finally {
      loading = false;
    }
  }

  function toggleResetPassword() {
    showResetPassword = !showResetPassword;
    error = '';
    resetError = '';
    resetSuccess = false;
  }
</script>

<svelte:head>
  <title>CMS Login - Habits of Mind</title>
</svelte:head>

<div class="login-page">
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <div class="brand-logo">🧠</div>
        <h1>Habits of Mind CMS</h1>
        <p>{showResetPassword ? 'Reset Your Password' : 'Content Management System'}</p>
      </div>

      {#if !showResetPassword}
        <form on:submit={handleLogin} class="login-form">
          {#if error}
            <div class="error-alert">
              <span class="error-icon">⚠️</span>
              <span>{error}</span>
            </div>
          {/if}

          <div class="form-group">
            <label for="email">Email Address</label>
            <input
              id="email"
              type="email"
              bind:value={email}
              placeholder="admin@habitsofmind.org"
              required
              disabled={loading}
            />
          </div>

          <div class="form-group">
            <label for="password">Password</label>
            <input
              id="password"
              type="password"
              bind:value={password}
              placeholder="Enter your password"
              required
              disabled={loading}
            />
          </div>

          <button type="submit" class="login-btn" disabled={loading}>
            {#if loading}
              <span class="spinner"></span>
              Logging in...
            {:else}
              🔐 Login to CMS
            {/if}
          </button>

          <div class="forgot-password-link">
            <button type="button" class="link-btn" on:click={toggleResetPassword}>
              Forgot your password?
            </button>
          </div>
        </form>
      {:else}
        <form on:submit={handleResetPassword} class="login-form">
          {#if resetSuccess}
            <div class="success-alert">
              <span class="success-icon">✓</span>
              <span>Password reset email sent! Check your inbox.</span>
            </div>
          {/if}

          {#if resetError}
            <div class="error-alert">
              <span class="error-icon">⚠️</span>
              <span>{resetError}</span>
            </div>
          {/if}

          <p class="reset-description">
            Enter your email address and we'll send you a link to reset your password.
          </p>

          <div class="form-group">
            <label for="reset-email">Email Address</label>
            <input
              id="reset-email"
              type="email"
              bind:value={email}
              placeholder="admin@habitsofmind.org"
              required
              disabled={loading || resetSuccess}
            />
          </div>

          <button type="submit" class="login-btn" disabled={loading || resetSuccess}>
            {#if loading}
              <span class="spinner"></span>
              Sending...
            {:else}
              📧 Send Reset Link
            {/if}
          </button>

          <div class="forgot-password-link">
            <button type="button" class="link-btn" on:click={toggleResetPassword}>
              ← Back to Login
            </button>
          </div>
        </form>
      {/if}

      <div class="login-footer">
        <a href="/">← Back to Website</a>
      </div>
    </div>
  </div>
</div>

<style>
  .login-page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
  }

  .login-container {
    width: 100%;
    max-width: 440px;
  }

  .login-card {
    background: white;
    border-radius: 16px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    overflow: hidden;
  }

  .login-header {
    background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
    color: white;
    padding: 40px 32px;
    text-align: center;
  }

  .brand-logo {
    font-size: 64px;
    margin-bottom: 16px;
    animation: float 3s ease-in-out infinite;
  }

  @keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
  }

  .login-header h1 {
    margin: 0 0 8px;
    font-size: 28px;
    font-weight: 700;
  }

  .login-header p {
    margin: 0;
    color: rgba(255, 255, 255, 0.7);
    font-size: 16px;
  }

  .loading-section {
    padding: 60px 32px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 20px;
  }

  .loading-section p {
    color: #4a5568;
    font-size: 16px;
    font-weight: 600;
  }

  .spinner-large {
    width: 40px;
    height: 40px;
    border: 4px solid #e2e8f0;
    border-top-color: #667eea;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  .login-form {
    padding: 32px;
  }

  .form-group {
    margin-bottom: 24px;
  }

  .form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #2d3748;
    font-size: 14px;
  }

  .form-group input {
    width: 100%;
    padding: 14px 16px;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    font-size: 16px;
    transition: all 0.3s;
    font-family: inherit;
  }

  .form-group input:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }

  .form-group input:disabled {
    background: #f7fafc;
    cursor: not-allowed;
  }

  .error-alert {
    background: #fed7d7;
    color: #c53030;
    padding: 14px 16px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 20px;
    border: 1px solid #fc8181;
  }

  .error-icon {
    font-size: 20px;
  }

  .success-alert {
    background: #c6f6d5;
    color: #2f855a;
    padding: 14px 16px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 20px;
    border: 1px solid #9ae6b4;
  }

  .success-icon {
    font-size: 20px;
    font-weight: bold;
  }

  .login-btn {
    width: 100%;
    padding: 16px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.3s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
  }

  .login-btn:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
  }

  .login-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }

  .spinner {
    width: 16px;
    height: 16px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .forgot-password-link {
    margin-top: 16px;
    text-align: center;
  }

  .link-btn {
    background: none;
    border: none;
    color: #667eea;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: color 0.3s;
    text-decoration: none;
    padding: 0;
  }

  .link-btn:hover {
    color: #764ba2;
    text-decoration: underline;
  }

  .reset-description {
    margin-bottom: 24px;
    color: #4a5568;
    font-size: 14px;
    line-height: 1.6;
  }

  .login-help {
    margin-top: 24px;
    padding: 16px;
    background: #f7fafc;
    border-radius: 8px;
    text-align: center;
    font-size: 14px;
  }

  .login-help p {
    margin: 4px 0;
    color: #4a5568;
  }

  .login-help code {
    background: #e2e8f0;
    padding: 2px 8px;
    border-radius: 4px;
    font-family: 'Monaco', 'Menlo', monospace;
    color: #2d3748;
    font-size: 13px;
  }

  .login-footer {
    padding: 20px 32px;
    background: #f7fafc;
    text-align: center;
    border-top: 1px solid #e2e8f0;
  }

  .login-footer a {
    color: #667eea;
    text-decoration: none;
    font-weight: 600;
    transition: color 0.3s;
  }

  .login-footer a:hover {
    color: #764ba2;
  }

  @media (max-width: 480px) {
    .login-page {
      padding: 16px;
    }

    .login-header {
      padding: 32px 24px;
    }

    .login-form {
      padding: 24px;
    }
  }
</style>
