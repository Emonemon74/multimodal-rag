# Docker

Build the image:

```bash
docker build -t multimodal-rag .
```

Run the container:

```bash
docker run --rm -p 8000:8000 --env-file .env multimodal-rag
```
