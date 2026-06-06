$token = "PASTE_ACCESS_TOKEN"

$headers = @{
    Authorization = "Bearer $token"
    "Content-Type" = "application/json"
    "X-Project-ID" = "YOUR_PROJECT_ID"
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

Invoke-RestMethod `
    -Method Post `
    -Uri "https://api.uhg.com/api/cloud/api-management/ai-gateway-reasoning/1.0/" `
    -Headers $headers `
    -Body $body
