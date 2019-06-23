AVAILABLE_JOBS = ["DummyJob4", "DummyJob5", "DummyJob6"]

class Repository:

    def __init__(self):
        pass

    @staticmethod
    def fields_request():
        field_list = []
        field_list.append(dict(name="name", label="Repository name", type="string"))
        field_list.append(dict(name="test1", label="Test field", type="int"))
        field_list.append(dict(name="test2", label="Test field select", type="select", values=[("test1", "Test 1"), ("test2", "Test 2"), ("test3", "Test 3")]))
        return field_list

    def create_repo(self, field_list):
        pass