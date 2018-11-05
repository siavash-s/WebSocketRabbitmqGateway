## Client Usage guide
##### In the project, It is assumed that there is a service validating JWT tokens from clients. 
1. a client should include a valid JWT token in HTTP upgrade request cookie. the cookie should have a name/value like this:  
    token=valid-jwt-token
    The server reply a 400 bad request HTTP response if no cookie presented in the request.
    The server reply a 400 bad request HTTP response also in case of an empty value or the token key absence.
    a 401 HTTP response code indicates the token value is not valid.
2. After a successful connection a client may subscribe on a topic in order to receive messages.
    The subscription request should have a valid json body in the following format:
    ```javascript
        {"token": "some-valid-token", "topic": "topic-name"}
    ```
    Any subscription request should include a valid JWT token, if the client does not have the permission to subscribe  
    the server would send a False state result with 'token access denied' detail.  
    A server response to the subscription request is a json in the following format:  
    ```javascript
        {"result": true, "detail": "optional"}  // successful subscription
        {"result": false, "detail": "the reason"}  // unsuccessful subscription
    ```  
    ##### note that all messages are not binary
3. after a successful subscription the server may send messages to subscribed clients.
    the subscribed messages are in the following format:
    ```javascript
    {"topic": "topic-name", "payload": {}}
    ```  
---
Examples of using WebSocket: [click](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_client_applications)
---
## Available topics:
* __alerts__:  
Alerts from the core system.
#### format:
```javascript
{"ticket_id": "'|' splitted string", "msg": "blah blah blah", "history_id": 54}
```
* __activities__:  
Activities reports from the core system.
#### format:
```javascript
{"ticket_id": "'|' splitted string", "msg": "blah blah blah", "history_id": 54}
```
---
### Run:  
##### Available configurations via environment variables:
* RABBITMQ_HOST
* RABBITMQ_PORT
* RABBITMQ_USER
* RABBITMQ_PASSWORD
* AUTHORIZATION_URL
* LOG_LEVEL
* LOG_PREFIX
---
##### Example:
```bash
sudo docker run -p9000:9000 -e RABBITMQ_HOST=192.168.101.101\
 -e AUTHORIZATION_URL='http://192.168.101.101:5000/user_info' docker-image-name
``` 
