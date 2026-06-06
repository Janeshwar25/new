
>> }
PS C:\Users\jchowdha>
PS C:\Users\jchowdha> $body = @{
>>
>>     model = "enterprise-llm"
>>
>>     messages = @(
>>
>>         @{
>>
>>             role = "user"
>>
>>             content = "hello"
>>
>>         }
>>
>>     )
>>
>> } | ConvertTo-Json -Depth 10
PS C:\Users\jchowdha>
PS C:\Users\jchowdha> Invoke-RestMethod `
>>

cmdlet Invoke-RestMethod at command pipeline position 1
Supply values for the following parameters:
Uri: a
Invoke-RestMethod : The remote name could not be resolved: 'a'
At line:1 char:1
+ Invoke-RestMethod `
+ ~~~~~~~~~~~~~~~~~
    + CategoryInfo          : InvalidOperation: (System.Net.HttpWebRequest:HttpWebRequest) [Invoke-RestMethod], WebExc
   eption
    + FullyQualifiedErrorId : WebCmdletWebResponseException,Microsoft.PowerShell.Commands.InvokeRestMethodCommand

PS C:\Users\jchowdha>     -Method Post `
>>
-Method : The term '-Method' is not recognized as the name of a cmdlet, function, script file, or operable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
At line:1 char:5
+     -Method Post `
+     ~~~~~~~
    + CategoryInfo          : ObjectNotFound: (-Method:String) [], CommandNotFoundException
    + FullyQualifiedErrorId : CommandNotFoundException

PS C:\Users\jchowdha>     -Uri "https://api.uhg.com/api/cloud/api-management/ai-gateway-reasoning/1.0/" `
>>
-Uri : The term '-Uri' is not recognized as the name of a cmdlet, function, script file, or operable program. Check
the spelling of the name, or if a path was included, verify that the path is correct and try again.
At line:1 char:5
+     -Uri "https://api.uhg.com/api/cloud/api-management/ai-gateway-rea ...
+     ~~~~
    + CategoryInfo          : ObjectNotFound: (-Uri:String) [], CommandNotFoundException
    + FullyQualifiedErrorId : CommandNotFoundException

PS C:\Users\jchowdha>     -Headers $headers `
>>
-Headers : The term '-Headers' is not recognized as the name of a cmdlet, function, script file, or operable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
At line:1 char:5
+     -Headers $headers `
+     ~~~~~~~~
    + CategoryInfo          : ObjectNotFound: (-Headers:String) [], CommandNotFoundException
    + FullyQualifiedErrorId : CommandNotFoundException

PS C:\Users\jchowdha>     -Body $body
-Body : The term '-Body' is not recognized as the name of a cmdlet, function, script file, or operable program. Check
the spelling of the name, or if a path was included, verify that the path is correct and try again.
At line:1 char:5
+     -Body $body
+     ~~~~~
    + CategoryInfo          : ObjectNotFound: (-Body:String) [], CommandNotFoundException
    + FullyQualifiedErrorId : CommandNotFoundException

PS C:\Users\jchowdha>
PS C:\Users\jchowdha>
PS C:\Users\jchowdha
