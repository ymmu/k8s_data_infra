import os, json
import pandas as pd

df = pd.DataFrame({"test":[1,2,3]})  
print(df)
from kafka import KafkaProducer
producer = KafkaProducer(
    acks=1,
    value_serializer=lambda x: x.encode("utf-8"),
    key_serializer=None,
    bootstrap_servers="localhost:9094")

for _, value in df.iterrows():
    val = value.to_json()
    # print(val)
    response = producer.send(topic="test-akhq", value=val).get()
    print(response)