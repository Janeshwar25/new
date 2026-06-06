$body = @{
    grant_type    = "client_credentials"
    client_id     = "YOUR_CLIENT_ID"
    client_secret = "YOUR_CLIENT_SECRET"
    scope         = "https://api.uhg.com/.default"
}

Invoke-RestMethod `
    -Method Post `
    -Uri "https://api.uhg.com/oauth2/token" `
    -Body $body `
    -ContentType "application/x-www-form-urlencoded"
