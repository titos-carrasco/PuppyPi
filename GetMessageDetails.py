import roslibpy

ros = roslibpy.Ros(host="192.168.149.1", port=9090)
ros.run()

topic = "/puppy_control/velocity"
msg_type = ros.get_topic_type(topic)
print(msg_type)

details = ros.get_message_details(msg_type)
print(details)

ros.terminate()
