---
name: Embeddings
description: Embed text as vectors and search them semantically using the NVIDIA API and Redis vector search
---

# Embeddings

Generate text embeddings via the NVIDIA API and store/search them in Redis using RediSearch vector indexing.

**Important:** All Redis keys and index names must be namespaced to avoid collisions in the shared Redis instance. The prefix is auto-built from `K8S_NAMESPACE` and `AGENT_NAME`. The examples below use `$PREFIX` as shorthand — set it first:

```bash
PREFIX="minimino:${K8S_NAMESPACE:-default}:agent:${AGENT_NAME:-minimino}"
```

## API Details

- **Endpoint:** `https://integrate.api.nvidia.com/v1/embeddings`
- **Auth:** `Authorization: Bearer $NIM_API_KEYS` (first key from the comma-separated list)
- **Model:** `nvidia/nv-embedqa-e5-v5`
- **Dimensions:** 1024

## 1. Generate an Embedding

```bash
curl -s -X POST https://integrate.api.nvidia.com/v1/embeddings \
  -H "Authorization: Bearer $(echo $NIM_API_KEYS | cut -d, -f1)" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nvidia/nv-embedqa-e5-v5",
    "input": ["YOUR TEXT HERE"],
    "input_type": "passage"
  }'
```

For search queries, use `"input_type": "query"` instead of `"passage"`.

Response format:
```json
{
  "data": [{ "embedding": [0.123, -0.456, ...] }]
}
```

## 2. Create a Vector Index in Redis (once)

```bash
redis-cli FT.CREATE "${PREFIX}:emb-idx" ON HASH PREFIX 1 "${PREFIX}:emb:" \
  SCHEMA text TEXT name TAG vec VECTOR FLAT 6 \
  TYPE FLOAT32 DIM 1024 DISTANCE_METRIC COSINE
```

Ignore "Index already exists" errors.

## 3. Store an Embedding

Convert the float array to a binary blob and store it as a Redis HASH:

```bash
python3 -c "
import struct, subprocess, json, sys
embedding = json.loads(sys.argv[1])
blob = struct.pack(f'{len(embedding)}f', *embedding)
subprocess.run(['redis-cli', 'HSET', sys.argv[2], 'text', sys.argv[3], 'name', sys.argv[4], 'vec', blob.decode('latin-1')], check=True)
" '$EMBEDDING_JSON_ARRAY' '${PREFIX}:emb:my-key' 'the original text' 'my-key'
```

## 4. Search by Similarity

```bash
redis-cli FT.SEARCH "${PREFIX}:emb-idx" "*=>[KNN 5 @vec \$query_vec]" \
  PARAMS 2 query_vec "$QUERY_VECTOR_BLOB" \
  RETURN 3 text name __vec_score \
  DIALECT 2
```

## Typical Workflow

1. Set `PREFIX` variable from env vars
2. Generate embedding for your text (input_type: passage)
3. Ensure the index exists (step 2, idempotent)
4. Store the embedding with its text and a key name
5. To search: generate embedding for query (input_type: query), then run FT.SEARCH
