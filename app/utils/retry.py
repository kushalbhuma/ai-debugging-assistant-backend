from tenacity import retry, stop_after_attempt, wait_fixed

llm_retry = retry(
    stop=stop_after_attempt(2),
    wait=wait_fixed(1),
    reraise=True
)