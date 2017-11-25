

class Archive(object):

    @classmethod
    def of(cls, *pairs):
        buffer = ''
        for path, value in pairs:
            buffer += path
            buffer += ','
            buffer += value.strip()
            buffer += '\n'
        return buffer
