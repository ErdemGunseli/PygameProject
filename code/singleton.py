def singleton(class_used):
    instances = {}

    def get_instance():
        if class_used not in instances:
            instances[class_used] = class_used()
        return instances[class_used]
    return get_instance
