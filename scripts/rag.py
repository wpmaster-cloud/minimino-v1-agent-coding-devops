#!/usr/bin/env python3
# name: RAG Tool
# description: Embedding and retrieval tool for semantic document search using NVIDIA NIM.
"""RAG for Minimino. Usage:
  python3 scripts/rag.py index <file_path>
  python3 scripts/rag.py query <question>
"""
import sys, os, json, textwrap, urllib.request, redis
import re

def _sanitize(val):
    """Match Go's sanitizeAgentID: lowercase, non-alnum-except-:-_- → '-', trim edges."""
    val = re.sub(r'[^a-z0-9\-_:]', '-', val.strip().lower())
    return val.strip('-_')

NIM_URL     = os.environ.get("NIM_API_URL", "https://integrate.api.nvidia.com/v1").replace("/chat/completions", "").rstrip("/")
NIM_KEY     = os.environ.get("NIM_API_KEYS", os.environ.get("NIM_API_KEY", "")).split(",")[0].strip()
EMBED_MODEL = os.environ.get("NIM_EMBED_MODEL", "nvidia/nv-embedqa-e5-v5")
PREFIX      = _sanitize(os.environ.get("MINIMINO_REDIS_PREFIX", "minimino"))
AGENT_ID    = _sanitize(os.environ.get("AGENT_NAME", "agent"))
CHUNKS_KEY  = f"{PREFIX}:agent:{AGENT_ID}:doc:rag:chunks"

# Redis URL: prefer REDIS_URL, fallback to a local default
_redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# Vector Database (Redis) Setup
redis_client = redis.Redis.from_url(_redis_url, decode_responses=True)

CHUNK_WORDS = 400

def extract_text(path):
    ext = path.rsplit(".", 1)[-1].lower()
    if ext == "pdf":
        try:
            import pdfplumber
            with pdfplumber.open(path) as pdf:
                return "\n".join(p.extract_text() or "" for p in pdf.pages)
        except ImportError:
            return "error: pdfplumber not installed. Run: pip install pdfplumber"
    if ext == "docx":
        try:
            import docx
            return "\n".join(p.text for p in docx.Document(path).paragraphs)
        except ImportError:
            return "error: python-docx not installed. Run: pip install python-docx"
    if ext in ("xlsx", "xls"):
        try:
            import pandas as pd
            return pd.read_excel(path).to_string()
        except ImportError:
            return "error: pandas and openpyxl not installed. Run: pip install pandas openpyxl"
    if ext == "csv":
        try:
            import pandas as pd
            return pd.read_csv(path).to_string()
        except ImportError:
            return "error: pandas not installed. Run: pip install pandas"
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception as e:
        return f"error reading file: {e}"

def chunk(text):
    words = text.split()
    return [" ".join(words[i:i+CHUNK_WORDS]) for i in range(0, len(words), CHUNK_WORDS)]

def embed(texts, input_type="passage"):
    if not NIM_KEY:
        raise ValueError("NIM_API_KEY not set")
    body = json.dumps({"model": EMBED_MODEL, "input": texts, "input_type": input_type}).encode()
    req = urllib.request.Request(f"{NIM_URL}/embeddings", data=body,
        headers={"Authorization": f"Bearer {NIM_KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return [item["embedding"] for item in json.loads(r.read())["data"]]

def cosine(a, b):
    dot = sum(x*y for x,y in zip(a,b))
    na = sum(x*x for x in a)**0.5; nb = sum(x*x for x in b)**0.5
    return dot/(na*nb) if na and nb else 0.0

def get_redis():
    import redis
    return redis.from_url(_redis_url, decode_responses=True)

def cmd_index(path):
    text = extract_text(path)
    if text.startswith("error:"):
        print(text); return
    chunks = chunk(text)
    if not chunks:
        print("Empty file, nothing to index."); return
    embeddings = []
    for i in range(0, len(chunks), 8):
        embeddings.extend(embed(chunks[i:i+8]))
    r = get_redis()
    fname = os.path.basename(path)
    existing = [k for k in r.hkeys(CHUNKS_KEY) if k.startswith(f"{fname}:")]
    if existing: r.hdel(CHUNKS_KEY, *existing)
    pipe = r.pipeline()
    for i, (t, e) in enumerate(zip(chunks, embeddings)):
        pipe.hset(CHUNKS_KEY, f"{fname}:{i}", json.dumps({"file": fname, "text": t, "embedding": e}))
    pipe.execute()
    print(f"Indexed {len(chunks)} chunks from {path}")

def cmd_query(question, top_k=5):
    try:
        q_emb = embed([question], input_type="query")[0]
    except Exception as e:
        print(f"Embedding error: {e}"); return
    r = get_redis()
    all_chunks = r.hgetall(CHUNKS_KEY)
    if not all_chunks:
        print("No documents indexed. Use index_document first."); return
    scored = sorted(
        ((cosine(q_emb, json.loads(v)["embedding"]), json.loads(v)["file"], json.loads(v)["text"])
         for v in all_chunks.values()),
        reverse=True
    )[:top_k]
    for i, (sim, fname, text) in enumerate(scored):
        print(f"[{i+1}] {fname} (score: {sim:.4f})\n{textwrap.fill(text[:600], 80)}\n")

if __name__ == "__main__":
    if len(sys.argv) < 3: print(__doc__); sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "index":
        cmd_index(sys.argv[2])
    elif cmd == "query":
        cmd_query(" ".join(sys.argv[2:]))
    else:
        print(f"Unknown command: {cmd}\n" + __doc__)
