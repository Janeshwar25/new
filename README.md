Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

Install the latest PowerShell for new features and improvements! https://aka.ms/PSWindows

PS C:\Users\jchowdha> cd Desktop/g
PS C:\Users\jchowdha\Desktop\g> py -m uvicorn app.routes:app --host 127.0.0.1 --port 8000 --reload
INFO:     Will watch for changes in these directories: ['C:\\Users\\jchowdha\\Desktop\\g']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [4700] using StatReload
INFO:     Started server process [13920]
INFO:     Waiting for application startup.
'[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1081)' thrown while requesting HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/./modules.json
Retrying in 1s [Retry 1/5].
[KB] Indexing failed: Cannot send a request, as the client has been closed.
Traceback (most recent call last):
  File "C:\Users\jchowdha\Desktop\g\agent\knowledge_base_indexer.py", line 144, in ensure_knowledge_base_index
    ok = add_documents_to_store(all_chunks, cfg)
  File "C:\Users\jchowdha\Desktop\g\agent\vector_store.py", line 35, in add_documents_to_store
    embeddings = get_embedding_model(config)
  File "C:\Users\jchowdha\Desktop\g\agent\embedding_service.py", line 4, in get_embedding_model
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
  File "C:\Users\jchowdha\AppData\Roaming\Python\Python314\site-packages\langchain_huggingface\embeddings\huggingface.py", line 97, in __init__
    self._client = model_cls(
                   ~~~~~~~~~^
        self.model_name, cache_folder=self.cache_folder, **self.model_kwargs
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\jchowdha\AppData\Roaming\Python\Python314\site-packages\sentence_transformers\util\decorators.py", line 41, in wrapper
    return func(*args, **kwargs)
  File "C:\Users\jchowdha\AppData\Roaming\Python\Python314\site-packages\sentence_transformers\sentence_transformer\model.py", line 184, in __init__
    super().__init__(
    ~~~~~~~~~~~~~~~~^
        model_name_or_path=model_name_or_path,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<13 lines>...
        default_prompt_name=default_prompt_name,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\jchowdha\AppData\Roaming\Python\Python314\site-packages\sentence_transformers\base\model.py", line 204, in __init__
    modules, self.module_kwargs = self._load_modules(
                                  ~~~~~~~~~~~~~~~~~~^
        model_name_or_path,
        ^^^^^^^^^^^^^^^^^^^
    ...<7 lines>...
        config_kwargs=config_kwargs,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\jchowdha\AppData\Roaming\Python\Python314\site-packages\sentence_transformers\base\model.py", line 972, in _load_modules
    modules_json_path = load_file_path(
        model_name_or_path,
    ...<4 lines>...
        local_files_only=local_files_only,
    )
  File "C:\Users\jchowdha\AppData\Roaming\Python\Python314\site-packages\sentence_transformers\util\file_io.py", line 116, in load_file_path
    return hf_hub_download(
        model_name_or_path,
    ...<6 lines>...
        local_files_only=local_files_only,
    )
  File "C:\Users\jchowdha\AppData\Roaming\Python\Python314\site-packages\huggingface_hub\utils\_validators.py", line 88, in _inner_fn
    return fn(*args, **kwargs)
  File "C:\Users\jchowdha\AppData\Roaming\Python\Python314\site-packages\huggingface_hub\file_download.py", line 1010, in hf_hub_download
    return _hf_hub_download_to_cache_dir(
        # Destination
    ...<15 lines>...
        dry_run=dry_run,
    )
  File "C:\Users\jchowdha\AppData\Roaming\Python\Python314\site-packages\huggingface_hub\file_download.py", line 1143, in _hf_hub_download_to_cache_dir
    _get_metadata_or_catch_error(
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        repo_id=repo_id,
        ^^^^^^^^^^^^^^^^
    ...<10 lines>...
        retry_on_errors=True,
        ^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\jchowdha\AppData\Roaming\Python\Python314\site-packages\huggingface_hub\file_download.py", line 1682, in _get_metadata_or_catch_error
    metadata = get_hf_file_metadata(
        url=url,
    ...<4 lines>...
        retry_on_errors=retry_on_errors,
    )
  File "C:\Users\jchowdha\AppData\Roaming\Python\Python314\site-packages\huggingface_hub\utils\_validators.py", line 88, in _inner_fn
    return fn(*args, **kwargs)
  File "C:\Users\jchowdha\AppData\Roaming\Python\Python314\site-packages\huggingface_hub\file_download.py", line 1604, in get_hf_file_metadata
    response = _httpx_follow_relative_redirects_with_backoff(
        method="HEAD", url=url, headers=hf_headers, timeout=timeout, retry_on_errors=retry_on_errors
    )
  File "C:\Users\jchowdha\AppData\Roaming\Python\Python314\site-packages\huggingface_hub\utils\_http.py", line 685, in _httpx_follow_relative_redirects_with_backoff
    response = http_backoff(
        method=method,
    ...<3 lines>...
        **no_retry_kwargs,
    )
  File "C:\Users\jchowdha\AppData\Roaming\Python\Python314\site-packages\huggingface_hub\utils\_http.py", line 559, in http_backoff
    return next(
        _http_backoff_base(
    ...<9 lines>...
        )
    )
  File "C:\Users\jchowdha\AppData\Roaming\Python\Python314\site-packages\huggingface_hub\utils\_http.py", line 467, in _http_backoff_base
    response = client.request(method=method, url=url, **kwargs)
  File "C:\Users\jchowdha\AppData\Roaming\Python\Python314\site-packages\httpx\_client.py", line 825, in request
    return self.send(request, auth=auth, follow_redirects=follow_redirects)
           ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\jchowdha\AppData\Roaming\Python\Python314\site-packages\httpx\_client.py", line 901, in send
    raise RuntimeError("Cannot send a request, as the client has been closed.")
RuntimeError: Cannot send a request, as the client has been closed.
INFO:     Application startup complete.
Failed to connect to MongoDB: localhost:27017: [WinError 10061] No connection could be made because the target machine actively refused it (configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms), Timeout: 5.0s, Topology Description: <TopologyDescription id: 6a240dff9b50a6f9e7dcfdd7, topology_type: Unknown, servers: [<ServerDescription ('localhost', 27017) server_type: Unknown, rtt: None, error=AutoReconnect('localhost:27017: [WinError 10061] No connection could be made because the target machine actively refused it (configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms)')>]>
MongoDB portfolio summary unavailable: localhost:27017: [WinError 10061] No connection could be made because the target machine actively refused it (configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms), Timeout: 5.0s, Topology Description: <TopologyDescription id: 6a240dff9b50a6f9e7dcfdd7, topology_type: Unknown, servers: [<ServerDescription ('localhost', 27017) server_type: Unknown, rtt: None, error=AutoReconnect('localhost:27017: [WinError 10061] No connection could be made because the target machine actively refused it (configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms)')>]>
'[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1081)' thrown while requesting HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/./modules.json
Retrying in 1s [Retry 1/5].
Failed to load vector store: Cannot send a request, as the client has been closed.
[Enterprise] Unexpected error in enterprise provider
Traceback (most recent call last):
  File "C:\Users\jchowdha\Desktop\g\agent\providers\enterprise_provider.py", line 75, in generate_rag_response
    response = client.generate_response(
               ^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'EnterpriseLLMClient' object has no attribute 'generate_response'
🔴 ENTERPRISE LLM GATEWAY FAILED 🔴
Error: Enterprise LLM unexpected error: 'EnterpriseLLMClient' object has no attribute 'generate_response'

STRICT ENTERPRISE-ONLY MODE:
  ✗ No fallback providers available
  ✗ No public LLMs allowed
  ✗ No automatic switching

ACTION REQUIRED:
  1. Check enterprise gateway connectivity
  2. Verify OAuth2 credentials
  3. Review gateway logs
  4. Contact IT/DevOps

Enterprise LLM Gateway exception:
Traceback (most recent call last):
  File "C:\Users\jchowdha\Desktop\g\agent\providers\enterprise_provider.py", line 75, in generate_rag_response
    response = client.generate_response(
               ^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'EnterpriseLLMClient' object has no attribute 'generate_response'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\jchowdha\Desktop\g\agent\llm_manager.py", line 144, in answer_query
    content = enterprise_provider.generate_rag_response(
        messages,
        config=self.config,
        temperature=0.1
    )
  File "C:\Users\jchowdha\Desktop\g\agent\providers\enterprise_provider.py", line 92, in generate_rag_response
    raise RuntimeError(f"Enterprise LLM unexpected error: {str(e)}")
RuntimeError: Enterprise LLM unexpected error: 'EnterpriseLLMClient' object has no attribute 'generate_response'
🔴 ENTERPRISE LLM GATEWAY FAILED - NO FALLBACK AVAILABLE
Traceback (most recent call last):
  File "C:\Users\jchowdha\Desktop\g\agent\providers\enterprise_provider.py", line 75, in generate_rag_response
    response = client.generate_response(
               ^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'EnterpriseLLMClient' object has no attribute 'generate_response'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\jchowdha\Desktop\g\agent\llm_manager.py", line 144, in answer_query
    content = enterprise_provider.generate_rag_response(
        messages,
        config=self.config,
        temperature=0.1
    )
  File "C:\Users\jchowdha\Desktop\g\agent\providers\enterprise_provider.py", line 92, in generate_rag_response
    raise RuntimeError(f"Enterprise LLM unexpected error: {str(e)}")
RuntimeError: Enterprise LLM unexpected error: 'EnterpriseLLMClient' object has no attribute 'generate_response'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\jchowdha\Desktop\g\app\routes.py", line 129, in help_bot_llm
    result = bot.answer(
        query=query,
        chat_history=chat_history,
        portfolio_filter=portfolio_filter,
    )
  File "C:\Users\jchowdha\Desktop\g\agent\chatbot.py", line 105, in answer
    return self.llm_manager.answer_query(
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
         query=query,
         ^^^^^^^^^^^^
    ...<2 lines>...
         sources_used=rag_result.sources_used
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\jchowdha\Desktop\g\agent\llm_manager.py", line 179, in answer_query
    raise RuntimeError(
        f"Enterprise LLM Gateway failed. No fallback available. {str(e)}"
    )
RuntimeError: Enterprise LLM Gateway failed. No fallback available. Enterprise LLM unexpected error: 'EnterpriseLLMClient' object has no attribute 'generate_response'
INFO:     127.0.0.1:59898 - "POST /llm HTTP/1.1" 503 Service Unavailable
