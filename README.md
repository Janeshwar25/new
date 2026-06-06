Hi Rahil,

I validated the OAuth flow and gateway connectivity successfully.

The gateway now accepts the token/auth headers, but inference requests are failing with:

"Object reference not set to an instance of an object"

This appears to be occurring inside the gateway/model routing layer.

Could you please confirm:

* supported model names
* required payload schema
* whether the project is mapped to an active model deployment
* any additional required headers

Current endpoint:
https://api.uhg.com/api/cloud/api-management/ai-gateway-reasoning/1.0/

Thanks!
