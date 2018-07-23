web_api_conf = {
    "identity_authorization_url": "http://localhost:5000/user_info",
    "authorization_header_key": "Authorization",
    "authorization_header_prefix": "Bearer"
}

cookie_authorization = {
    "TOKEN_KEY": "token"
}


#  the key is the WebSocket topic,
#  the value is a list of RabbitMQ topic information with keys representing RabbitMQ topics,
#  exchange name, exchange type, topic name and the callable hook that recieves input from rabbit topic and
#  its output will be used for the WebSocket topic.
ws_rmq_topics = {
    "alerts": [
        {
            "exchange_name": "notification",
            "exchange_type": "topic",
            "topic": "sphex.notification.warning",
            "hook": lambda data: data,
        },
        {
            "exchange_name": "notification",
            "exchange_type": "topic",
            "topic": "sphex.notification.error",
            "hook": lambda data: data,
        }
    ],
    "activities": [
        {
            "exchange_name": "notification",
            "exchange_type": "topic",
            "topic": "sphex.notification.info",
            "hook": lambda data: data,
        }
    ],
}

# pika.connection.Parameters compatible
rabbitmq_connection = {
    'host': "localhost",
}

rabbitmq_connection_sleep_retry = 30

websocket_url = "ws://localhost:9000/"

server_address = {
    "address": "0.0.0.0",
    "port": 9000
}
