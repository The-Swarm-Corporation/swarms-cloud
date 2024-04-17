def get_class_attributes(classes):
    class_attributes = {}
    for cls in classes:
        if isinstance(cls, type) and hasattr(cls, "__name__"):
            class_name = cls.__name__
            class_attributes[class_name] = {
                "agent_name": getattr(cls, "agent_name", None),
                "model_name": getattr(cls, "model_name", None),
                "swarm_name": getattr(cls, "swarm_name", None),
                "swarm_id": getattr(cls, "swarm_id", None),
            }
    return class_attributes
