Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

Install the latest PowerShell for new features and improvements! https://aka.ms/PSWindows

PS C:\Users\jchowdha> cd Desktop/g
PS C:\Users\jchowdha\Desktop\g> py -m uvicorn app.routes:app --host 127.0.0.1 --port 8000 --reload
INFO:     Will watch for changes in these directories: ['C:\\Users\\jchowdha\\Desktop\\g']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [44592] using StatReload
INFO:     Started server process [43608]
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
Failed to connect to MongoDB: localhost:27017: [WinError 10061] No connection could be made because the target machine actively refused it (configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms), Timeout: 5.0s, Topology Description: <TopologyDescription id: 6a240fb6a811da8280c75f36, topology_type: Unknown, servers: [<ServerDescription ('localhost', 27017) server_type: Unknown, rtt: None, error=AutoReconnect('localhost:27017: [WinError 10061] No connection could be made because the target machine actively refused it (configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms)')>]>
MongoDB portfolio summary unavailable: localhost:27017: [WinError 10061] No connection could be made because the target machine actively refused it (configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms), Timeout: 5.0s, Topology Description: <TopologyDescription id: 6a240fb6a811da8280c75f36, topology_type: Unknown, servers: [<ServerDescription ('localhost', 27017) server_type: Unknown, rtt: None, error=AutoReconnect('localhost:27017: [WinError 10061] No connection could be made because the target machine actively refused it (configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms)')>]>
'[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1081)' thrown while requesting HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/./modules.json
Retrying in 1s [Retry 1/5].
Failed to load vector store: Cannot send a request, as the client has been closed.

===== ENTERPRISE REQUEST =====
URL: https://api.uhg.com/api/cloud/api-management/ai-gateway-reasoning/1.0/
HEADERS: {'Authorization': '***MASKED***', 'Content-Type': 'application/json', 'Accept': 'application/json', 'X-Project-ID': '3fccc5df-159d-47a0-b42d-4d1e49897153', 'x-project-id': '3fccc5df-159d-47a0-b42d-4d1e49897153', 'project-id': '3fccc5df-159d-47a0-b42d-4d1e49897153', 'X-Client-ID': '81c9cb4e-5813-4bcb-a9ae-a67657265b4c', 'x-client-id': '81c9cb4e-5813-4bcb-a9ae-a67657265b4c', 'client-id': '81c9cb4e-5813-4bcb-a9ae-a67657265b4c'}
PAYLOAD: {'model': 'enterprise-llm', 'messages': [{'role': 'user', 'content': 'SYSTEM:\nYou are an Enterprise AI Help Bot and Document Analyst.\n\nYou assist users by generating clear, professional, and concise answers using ONLY the context provided below. \n\nGuidelines:\n- Rely strictly on retrieved sections (documents, spreadsheets, vector matches, workflow knowledge).\n- Prioritize exact entity matches over general fuzzy descriptions.\n- Format responses cleanly. Do not emit large dumps of raw metadata.\n- When retrieving data from uploaded files (like Excel), provide a brief summary rather than just repeating isolated row structures.\n- Include explicit and clean markdown URL links if you output emails or web addresses (e.g. `[user@domain.com](mailto:user@domain.com)`).\n- When appropriate, append a concise citation pointing back to the Source File, Sheet, or System context at the bottom of your answer.\n- If the context does not contain enough information, state this directly. Do not invent answers or hallucinate data.\n- Avoid printing "row strings" iteratively. If several contacts exist, wrap them in clean sentence structures.\n\nWhen listing steps, use numbered or bullet lists.\n\n\n---\n## Retrieved context\n\n# Forge Project Plan Generation — How the application works\n\n## UI tabs\n- **Build Plan**: User enters Aha Idea, project type, idea name (max 40 chars), BDL, RDL. System fetches Aha data, saves metadata to MongoDB, calls FastAPI POST /chat to build a plan DataFrame, uploads to Smartsheet, stores sheet id in MongoDB.\n- **Update Plan**: User enters strategic theme or Aha idea and selects sources (Aha, Optics, Rally fields). FastAPI POST /chat with "Update Request" runs upload.update_smartsheet.update() to refresh Smartsheet cells from Aha, Rally (via Icarus), and PPM Optics.\n- **Test Plan**: Generates filtered PET test scripts from Excel templates (no external plan APIs).\n- **AI Help Bot**: Answers questions about the system and portfolio metadata via POST /llm.\n\n## Architecture (summary)\n- **Streamlit** (app/app.py) on port 8080 — user interface.\n- **FastAPI** (app/routes.py) on port 8000 — /chat, /financials, /llm.\n- **engine/mapping.py** — build_plan(), Aha and Rally/Icarus integration, Excel templates.\n- **upload/** — Smartsheet create (smartsheet_export) and update (update_smartsheet).\n- **MongoDB** — plan_metadata collection: idea, name, tag, prj, sheet id, bdl, rdl, active, optional sheet_markdown for AI sync.\n- **External APIs**: Aha, Icarus (Rally + Optics data), Smartsheet.\n\n## Build plan requirements\n- Valid Aha idea with a strategic theme (ST number) linked in Aha.\n- Template: documents/GNP_Template_v4.xlsx.\n- Plans land in Growth, New Product Smartsheet workspace folders by initiative area (tag).\n\n## Update behavior\n- Only the most recently created plan for a theme/idea is typically updated (per FAQ).\n- Manual rows/columns are not overwritten except where update logic maps known fields.\n- **Work Breakdown** column must stay in place when reordering columns.\n- Rally/Optics data may lag ~1 day (third-party refresh).\n\n## Configuration\n- credentials.env (from env.template): API keys, MongoDB, Azure OpenAI for Help Bot.\n- config.py centralizes settings.\n\n\n\n# Frequently Asked Questions (application)\n\n- **Who creates the plan?** BDL and RDL should collaborate; only one build per idea — the most recent plan receives updates.\n- **Where is my plan?** Growth, New Product Smartsheet workspace, folder by initiative area.\n- **PMAT dashboard**: Can be created during Aha Approved Planning if Aha impacts exist; better after strategic theme exists.\n- **Multiple plans**: Only the most recent is updated; delete older copies or they will not auto-update.\n- **Capabilities / features mapping**: Based on Rally "Project" field into Application View; unmapped → "Other".\n- **Optics tasks missing**: Aha must have correct Optics PRJ populated.\n- **Rally/Optics not updating**: Third-party data refreshes roughly daily.\n- **Drag/drop capabilities**: Only needed on initial build; later updates stay in place.\n- **Custom rows/columns**: Updates are cell-level; manual rows/columns are not wiped.\n- **Column reorder**: Allowed except **Work Breakdown** must remain in place.\n\n\n# Project metadata\n\n*MongoDB portfolio summary could not be loaded. Answers will rely on system documentation only.*\n---\n\nUSER:\nHi'}], 'temperature': 0.1, 'max_tokens': 2048}
==============================

STATUS: 403
RESPONSE: <html>
<head><title>403 Forbidden</title></head>
<body>
<center><h1>403 Forbidden</h1></center>
<hr><center>Microsoft-Azure-Application-Gateway/v2</center>
<script>(function(){function c(){var b=a.contentDocument||a.contentWindow.document;if(b){var d=b.createElement('script');d.innerHTML="window.__CF$cv$params={r:'a0775a124cb54230',t:'MTc4MDc0ODIyNA=='};var a=document.createElement('script');a.src='/cdn-cgi/challenge-platform/scripts/jsd/main.js';document.getElementsByTagName('head')[0].appendChild(a);";b.getElementsByTagName('head')[0].appendChild(d)}}if(document.body){var a=document.createElement('iframe');a.height=1;a.width=1;a.style.position='absolute';a.style.top=0;a.style.left=0;a.style.border='none';a.style.visibility='hidden';document.body.appendChild(a);if('loading'!==document.readyState)c();else if(window.addEventListener)document.addEventListener('DOMContentLoaded',c);else{var e=document.onreadystatechange||function(){};document.onreadystatechange=function(b){e(b);'load
[Enterprise] Gateway error: LLM request failed: 403 - <html>
<head><title>403 Forbidden</title></head>
<body>
<center><h1>403 Forbidden</h1></center>
<hr><center>Microsoft-Azure-Application-Gateway/v2</center>
<script>(function(){function c(){var b=a.contentDocument||a.contentWindow.document;if(b){var d=b.createElement('script');d.innerHTML="window.__CF$cv$params={r:'a0775a124cb54230',t:'MTc4MDc0ODIyNA=='};var a=document.createElement('script');a.src='/cdn-cgi/challenge-platform/scripts/jsd/main.js';document.getElementsByTagName('head')[0].appendChild(a);";b.getElementsByTagName('head')[0].appendChild(d)}}if(document.body){var a=document.createElement('iframe');a.height=1;a.width=1;a.style.position='absolute';a.style.top=0;a.style.left=0;a.style.border='none';a.style.visibility='hidden';document.body.appendChild(a);if('loading'!==document.readyState)c();else if(window.addEventListener)document.addEventListener('DOMContentLoaded',c);else{var e=document.onreadystatechange||function(){};document.onreadystatechange=function(b){e(b);'load
🔴 ENTERPRISE LLM GATEWAY FAILED 🔴
Error: LLM request failed: 403 - <html>
<head><title>403 Forbidden</title></head>
<body>
<center><h1>403 Forbidden</h1></center>
<hr><center>Microsoft-Azure-Application-Gateway/v2</center>
<script>(function(){function c(){var b=a.contentDocument||a.contentWindow.document;if(b){var d=b.createElement('script');d.innerHTML="window.__CF$cv$params={r:'a0775a124cb54230',t:'MTc4MDc0ODIyNA=='};var a=document.createElement('script');a.src='/cdn-cgi/challenge-platform/scripts/jsd/main.js';document.getElementsByTagName('head')[0].appendChild(a);";b.getElementsByTagName('head')[0].appendChild(d)}}if(document.body){var a=document.createElement('iframe');a.height=1;a.width=1;a.style.position='absolute';a.style.top=0;a.style.left=0;a.style.border='none';a.style.visibility='hidden';document.body.appendChild(a);if('loading'!==document.readyState)c();else if(window.addEventListener)document.addEventListener('DOMContentLoaded',c);else{var e=document.onreadystatechange||function(){};document.onreadystatechange=function(b){e(b);'load

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
  File "C:\Users\jchowdha\Desktop\g\agent\llm_manager.py", line 144, in answer_query
    content = enterprise_provider.generate_rag_response(
        messages,
        config=self.config,
        temperature=0.1
    )
  File "C:\Users\jchowdha\Desktop\g\agent\providers\enterprise_provider.py", line 75, in generate_rag_response
    response = client.generate_response(
        messages=messages,
        context="rag_pipeline",
    )
  File "C:\Users\jchowdha\Desktop\g\agent\enterprise_llm.py", line 402, in generate_response
    result = self._send_request(
        complete_prompt
    )
  File "C:\Users\jchowdha\Desktop\g\agent\enterprise_llm.py", line 306, in _send_request
    raise RuntimeError(
    ...<3 lines>...
    )
RuntimeError: LLM request failed: 403 - <html>
<head><title>403 Forbidden</title></head>
<body>
<center><h1>403 Forbidden</h1></center>
<hr><center>Microsoft-Azure-Application-Gateway/v2</center>
<script>(function(){function c(){var b=a.contentDocument||a.contentWindow.document;if(b){var d=b.createElement('script');d.innerHTML="window.__CF$cv$params={r:'a0775a124cb54230',t:'MTc4MDc0ODIyNA=='};var a=document.createElement('script');a.src='/cdn-cgi/challenge-platform/scripts/jsd/main.js';document.getElementsByTagName('head')[0].appendChild(a);";b.getElementsByTagName('head')[0].appendChild(d)}}if(document.body){var a=document.createElement('iframe');a.height=1;a.width=1;a.style.position='absolute';a.style.top=0;a.style.left=0;a.style.border='none';a.style.visibility='hidden';document.body.appendChild(a);if('loading'!==document.readyState)c();else if(window.addEventListener)document.addEventListener('DOMContentLoaded',c);else{var e=document.onreadystatechange||function(){};document.onreadystatechange=function(b){e(b);'load
🔴 ENTERPRISE LLM GATEWAY FAILED - NO FALLBACK AVAILABLE
Traceback (most recent call last):
  File "C:\Users\jchowdha\Desktop\g\agent\llm_manager.py", line 144, in answer_query
    content = enterprise_provider.generate_rag_response(
        messages,
        config=self.config,
        temperature=0.1
    )
  File "C:\Users\jchowdha\Desktop\g\agent\providers\enterprise_provider.py", line 75, in generate_rag_response
    response = client.generate_response(
        messages=messages,
        context="rag_pipeline",
    )
  File "C:\Users\jchowdha\Desktop\g\agent\enterprise_llm.py", line 402, in generate_response
    result = self._send_request(
        complete_prompt
    )
  File "C:\Users\jchowdha\Desktop\g\agent\enterprise_llm.py", line 306, in _send_request
    raise RuntimeError(
    ...<3 lines>...
    )
RuntimeError: LLM request failed: 403 - <html>
<head><title>403 Forbidden</title></head>
<body>
<center><h1>403 Forbidden</h1></center>
<hr><center>Microsoft-Azure-Application-Gateway/v2</center>
<script>(function(){function c(){var b=a.contentDocument||a.contentWindow.document;if(b){var d=b.createElement('script');d.innerHTML="window.__CF$cv$params={r:'a0775a124cb54230',t:'MTc4MDc0ODIyNA=='};var a=document.createElement('script');a.src='/cdn-cgi/challenge-platform/scripts/jsd/main.js';document.getElementsByTagName('head')[0].appendChild(a);";b.getElementsByTagName('head')[0].appendChild(d)}}if(document.body){var a=document.createElement('iframe');a.height=1;a.width=1;a.style.position='absolute';a.style.top=0;a.style.left=0;a.style.border='none';a.style.visibility='hidden';document.body.appendChild(a);if('loading'!==document.readyState)c();else if(window.addEventListener)document.addEventListener('DOMContentLoaded',c);else{var e=document.onreadystatechange||function(){};document.onreadystatechange=function(b){e(b);'load

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
RuntimeError: Enterprise LLM Gateway failed. No fallback available. LLM request failed: 403 - <html>
<head><title>403 Forbidden</title></head>
<body>
<center><h1>403 Forbidden</h1></center>
<hr><center>Microsoft-Azure-Application-Gateway/v2</center>
<script>(function(){function c(){var b=a.contentDocument||a.contentWindow.document;if(b){var d=b.createElement('script');d.innerHTML="window.__CF$cv$params={r:'a0775a124cb54230',t:'MTc4MDc0ODIyNA=='};var a=document.createElement('script');a.src='/cdn-cgi/challenge-platform/scripts/jsd/main.js';document.getElementsByTagName('head')[0].appendChild(a);";b.getElementsByTagName('head')[0].appendChild(d)}}if(document.body){var a=document.createElement('iframe');a.height=1;a.width=1;a.style.position='absolute';a.style.top=0;a.style.left=0;a.style.border='none';a.style.visibility='hidden';document.body.appendChild(a);if('loading'!==document.readyState)c();else if(window.addEventListener)document.addEventListener('DOMContentLoaded',c);else{var e=document.onreadystatechange||function(){};document.onreadystatechange=function(b){e(b);'load
INFO:     127.0.0.1:50068 - "POST /llm HTTP/1.1" 503 Service Unavailable
