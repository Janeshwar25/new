$headers = @{
    Authorization = "Bearer $token"
    access_token  = $token
    "x-access-token" = $token
    "Content-Type" = "application/json"
    "X-Project-ID" = "3fccc5df-159d-47a0-b42d-4d1e49897153"
}
$body = @{
    model = "enterprise-llm"
    messages = @(
        @{
            role = "user"
            content = "hello"
        }
    )
} | ConvertTo-Json -Depth 10
Invoke-RestMethod -Method Post `
-Uri "https://api.uhg.com/api/cloud/api-management/ai-gateway-reasoning/1.0/" `
-Headers $headers `
-Body $body
