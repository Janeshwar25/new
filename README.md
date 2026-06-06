Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

Install the latest PowerShell for new features and improvements! https://aka.ms/PSWindows

PS C:\Users\jchowdha> cd Desktop/g
PS C:\Users\jchowdha\Desktop\g> py -m uvicorn app.routes:app --host 127.0.0.1 --port 8000 --reload
INFO:     Will watch for changes in these directories: ['C:\\Users\\jchowdha\\Desktop\\g']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [45028] using StatReload
INFO:     Started server process [34036]
INFO:     Waiting for application startup.
[KB] Indexing failed: 'Config' object has no attribute 'CIRRUS_AZU_OPENAI_CLIENT_ID'
Traceback (most recent call last):
  File "C:\Users\jchowdha\Desktop\g\agent\knowledge_base_indexer.py", line 144, in ensure_knowledge_base_index
    ok = add_documents_to_store(all_chunks, cfg)
  File "C:\Users\jchowdha\Desktop\g\agent\vector_store.py", line 35, in add_documents_to_store
    embeddings = get_embedding_model(config)
  File "C:\Users\jchowdha\Desktop\g\agent\embedding_service.py", line 16, in get_embedding_model
    if is_azure_configured(config):
       ~~~~~~~~~~~~~~~~~~~^^^^^^^^
  File "C:\Users\jchowdha\Desktop\g\agent\local_fallback.py", line 35, in is_azure_configured
    cfg.CIRRUS_AZU_OPENAI_CLIENT_ID,
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'Config' object has no attribute 'CIRRUS_AZU_OPENAI_CLIENT_ID'
INFO:     Application startup complete.
Failed to connect to MongoDB: localhost:27017: [WinError 10061] No connection could be made because the target machine actively refused it (configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms), Timeout: 5.0s, Topology Description: <TopologyDescription id: 6a23a20e1a8409bd1a2a716a, topology_type: Unknown, servers: [<ServerDescription ('localhost', 27017) server_type: Unknown, rtt: None, error=AutoReconnect('localhost:27017: [WinError 10061] No connection could be made because the target machine actively refused it (configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms)')>]>
MongoDB portfolio summary unavailable: localhost:27017: [WinError 10061] No connection could be made because the target machine actively refused it (configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms), Timeout: 5.0s, Topology Description: <TopologyDescription id: 6a23a20e1a8409bd1a2a716a, topology_type: Unknown, servers: [<ServerDescription ('localhost', 27017) server_type: Unknown, rtt: None, error=AutoReconnect('localhost:27017: [WinError 10061] No connection could be made because the target machine actively refused it (configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms)')>]>
Failed to load vector store: 'Config' object has no attribute 'CIRRUS_AZU_OPENAI_CLIENT_ID'
🔴 ENTERPRISE GATEWAY CLIENT ERROR: 🔴 LLM request failed: 404 - {"detail":"Not Found"}
[Enterprise] Gateway error: 🔴 LLM request failed: 404 - {"detail":"Not Found"}
🔴 ENTERPRISE LLM GATEWAY FAILED 🔴
Error: 🔴 LLM request failed: 404 - {"detail":"Not Found"}

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
  File "C:\Users\jchowdha\Desktop\g\agent\enterprise_llm.py", line 415, in generate_response
    result = self._send_request(complete_prompt)
  File "C:\Users\jchowdha\Desktop\g\agent\enterprise_llm.py", line 298, in _send_request
    raise RuntimeError(error_msg)
RuntimeError: 🔴 LLM request failed: 404 - {"detail":"Not Found"}
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
  File "C:\Users\jchowdha\Desktop\g\agent\enterprise_llm.py", line 415, in generate_response
    result = self._send_request(complete_prompt)
  File "C:\Users\jchowdha\Desktop\g\agent\enterprise_llm.py", line 298, in _send_request
    raise RuntimeError(error_msg)
RuntimeError: 🔴 LLM request failed: 404 - {"detail":"Not Found"}

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
RuntimeError: Enterprise LLM Gateway failed. No fallback available. 🔴 LLM request failed: 404 - {"detail":"Not Found"}
INFO:     127.0.0.1:51465 - "POST /llm HTTP/1.1" 503 Service Unavailable
