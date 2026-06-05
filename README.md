INFO:     Application startup complete.
Failed to connect to MongoDB: localhost:27017: [WinError 10061] No connection could be made because the target machine actively refused it (configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms), Timeout: 5.0s, Topology Description: <TopologyDescription id: 6a2326d476b06c24f3e941eb, topology_type: Unknown, servers: [<ServerDescription ('localhost', 27017) server_type: Unknown, rtt: None, error=AutoReconnect('localhost:27017: [WinError 10061] No connection could be made because the target machine actively refused it (configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms)')>]>
MongoDB portfolio summary unavailable: localhost:27017: [WinError 10061] No connection could be made because the target machine actively refused it (configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms), Timeout: 5.0s, Topology Description: <TopologyDescription id: 6a2326d476b06c24f3e941eb, topology_type: Unknown, servers: [<ServerDescription ('localhost', 27017) server_type: Unknown, rtt: None, error=AutoReconnect('localhost:27017: [WinError 10061] No connection could be made because the target machine actively refused it (configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms)')>]>
Failed to load vector store: 'Config' object has no attribute 'CIRRUS_AZU_OPENAI_CLIENT_ID'
🔴 ENTERPRISE GATEWAY CLIENT ERROR: 🔴 LLM request failed: 403 - <html>
<head><title>403 Forbidden</title></head>
<body>
<center><h1>403 Forbidden</h1></center>
<hr><center>Microsoft-Azure-Application-Gateway/v2</center>
<script>(function(){function c(){var b=
[Enterprise] Gateway error: 🔴 LLM request failed: 403 - <html>
<head><title>403 Forbidden</title></head>
<body>
<center><h1>403 Forbidden</h1></center>
<hr><center>Microsoft-Azure-Application-Gateway/v2</center>
<script>(function(){function c(){var b=
🔴 ENTERPRISE LLM GATEWAY FAILED 🔴
Error: 🔴 LLM request failed: 403 - <html>
<head><title>403 Forbidden</title></head>
<body>
<center><h1>403 Forbidden</h1></center>
<hr><center>Microsoft-Azure-Application-Gateway/v2</center>
<script>(function(){function c(){var b=

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
RuntimeError: 🔴 LLM request failed: 403 - <html>
<head><title>403 Forbidden</title></head>
<body>
<center><h1>403 Forbidden</h1></center>
<hr><center>Microsoft-Azure-Application-Gateway/v2</center>
<script>(function(){function c(){var b=
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
RuntimeError: 🔴 LLM request failed: 403 - <html>
<head><title>403 Forbidden</title></head>
<body>
<center><h1>403 Forbidden</h1></center>
<hr><center>Microsoft-Azure-Application-Gateway/v2</center>
<script>(function(){function c(){var b=

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
RuntimeError: Enterprise LLM Gateway failed. No fallback available. 🔴 LLM request failed: 403 - <html>
<head><title>403 Forbidden</title></head>
<body>
<center><h1>403 Forbidden</h1></center>
<hr><center>Microsoft-Azure-Application-Gateway/v2</center>
<script>(function(){function c(){var b=
INFO:     127.0.0.1:54433 - "POST /llm HTTP/1.1" 503 Service Unavailable
