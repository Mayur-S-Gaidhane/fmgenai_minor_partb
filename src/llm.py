import os, json

def call_llm(prompt: str,
             system_prompt: str | None = None,
             model: str = "gpt-4o-mini",
             temperature: float = 0.2,
             max_tokens: int = 64) -> str:
    """
    Provider-agnostic caller:
      - PROVIDER=ollama (recommended here): uses local Ollama (no cost).
      - PROVIDER=openai (optional): requires OPENAI_API_KEY and openai package.
    """
    provider = os.environ.get("PROVIDER", "ollama").lower()
    if provider == "ollama":
        return _call_ollama(prompt, system_prompt, temperature, max_tokens)
    elif provider == "openai":
        return _call_openai(prompt, system_prompt, model, temperature, max_tokens)
    else:
        raise RuntimeError(f"Unknown PROVIDER: {provider}")

def _call_ollama(prompt, system_prompt, temperature, max_tokens):
    import urllib.request
    url = "http://localhost:11434/api/chat"
    model = os.environ.get("OLLAMA_MODEL", "mistral:7b-instruct")
    payload = {
        "model": model,
        "messages": [],
        "options": {"temperature": temperature, "num_predict": max_tokens}
    }
    if system_prompt:
        payload["messages"].append({"role": "system", "content": system_prompt})
    payload["messages"].append({"role": "user", "content": prompt})
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    # Ollama streams; collect content parts
    content = []
    with urllib.request.urlopen(req) as r:
        for line in r:
            try:
                obj = json.loads(line.decode("utf-8"))
                if "message" in obj and "content" in obj["message"]:
                    content.append(obj["message"]["content"])
            except Exception:
                pass
    return "".join(content).strip()

def _call_openai(prompt, system_prompt, model, temperature, max_tokens):
    try:
        from openai import OpenAI
    except Exception as e:
        raise RuntimeError("OpenAI provider requested but 'openai' package not installed.") from e
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Set OPENAI_API_KEY to use OpenAI provider.")
    client = OpenAI(api_key=api_key)
    msgs = []
    if system_prompt:
        msgs.append({"role": "system", "content": system_prompt})
    msgs.append({"role": "user", "content": prompt})
    resp = client.chat.completions.create(
        model=model,
        messages=msgs,
        temperature=temperature,
        max_tokens=max_tokens,
        n=1,
    )
    return resp.choices[0].message.content.strip()
