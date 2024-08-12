from kafka.errors import TopicAlreadyExistsError
from fastapi import HTTPException

# def create_kafka_topic(kafka_factory, topic_name: str, num_partitions: int = 1, replication_factor: int = 1):
#     try:
#         result = kafka_factory.create_topic(topic_name, num_partitions, replication_factor)
#         return {"message": result}
#     except TopicAlreadyExistsError:
#         raise HTTPException(status_code=400, detail=f"Topic '{topic_name}' already exists.")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))