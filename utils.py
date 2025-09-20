# utils.py
import os, time, random, functools, requests
from dotenv import load_dotenv
from datetime import datetime
from requests.exceptions import RequestException

load_dotenv()

UA = os.getenv("USER_AGENT", "AI-Component-Aggregator/1.0")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
DATABASE_PATH = os.getenv("DATABASE_PATH", "components.db")

def jitter(base=1.0):
    return base + random.random()

def retry(max_retries=3, backoff=2.0):
    def deco(fn):
        @functools.wraps(fn)
        def wrap(*a, **kw):
            for i in range(max_retries):
                try:
                    return fn(*a, **kw)
                except Exception as e:
                    if i == max_retries - 1:
                        raise
                    sleep = (backoff ** i) * jitter()
                    time.sleep(sleep)
            # unreachable
        return wrap
    return deco

@retry(max_retries=3, backoff=2)
def get(url, headers=None, params=None, timeout=30):
    h = {"User-Agent": UA}
    if headers:
        h.update(headers)
    r = requests.get(url, headers=h, params=params, timeout=timeout)
    r.raise_for_status()
    return r

@retry(max_retries=2, backoff=1.5)
def head(url, headers=None, timeout=10):
    h = {"User-Agent": UA}
    if headers:
        h.update(headers)
    try:
        r = requests.head(url, headers=h, timeout=timeout, allow_redirects=True)
        return r
    except RequestException:
        # some servers do not respond to HEAD — fallback to GET with small range
        r = requests.get(url, headers=h, timeout=timeout, stream=True)
        return r

def iso_now():
    return datetime.utcnow().isoformat() + "Z"
