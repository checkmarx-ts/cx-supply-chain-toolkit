
class TestUtil:

    @staticmethod    
    def index_of_begin_path(list, path):
        index = 0
        for entry in list:
            if entry[0:len(path)] == path:
                return index
            index = index + 1

        return -1
