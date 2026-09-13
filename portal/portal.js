const copyStatus = document.getElementById('copy-status');
const copyFallback = document.getElementById('copy-fallback');
const copyFeedback = document.querySelector('.portal-copy-feedback');
let feedbackTimer;

document.getElementById('theme-toggle').hidden = false;

document.querySelectorAll('[data-copy-path]').forEach(button => {
  button.hidden = false;
  button.addEventListener('click', async () => {
    // Share the public short URL even when this page is previewed locally.
    const url = new URL(button.dataset.copyPath, 'https://zhuconv.github.io').href;
    button.disabled = true;
    clearTimeout(feedbackTimer);
    copyStatus.textContent = '';
    copyFallback.hidden = true;

    try {
      await navigator.clipboard.writeText(url);
      copyStatus.textContent = `Copied ${url}`;
      copyFeedback.classList.add('is-visible');
      feedbackTimer = setTimeout(() => {
        copyFeedback.classList.remove('is-visible');
        copyStatus.textContent = '';
      }, 3500);
    } catch (_) {
      copyStatus.textContent = 'Select and copy the link below:';
      copyFallback.value = url;
      copyFallback.hidden = false;
      copyFeedback.classList.add('is-visible');
      copyFallback.focus();
      copyFallback.select();
    } finally {
      button.disabled = false;
    }
  });
});
