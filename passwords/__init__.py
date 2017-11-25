import os

from . import db
from . import crypto
from . import ui


class PasswordRepository(object):

    FILESYSTEM_NAME  = '.passwords'
    PRIVATE_KEY_NAME = 'master.pem'
    PUBLIC_KEY_NAME  = 'master.pem.pub'
    DATABASE_NAME    = 'repository.sqlite'

    def __init__(self):
        self.directory = None
        self.database = None
        self.public_key = None
        self.private_key = None

    @classmethod
    def load(cls, directory):
        repo = cls()
        repo.directory   = os.path.join(directory, repo.FILESYSTEM_NAME)
        if not os.path.exists(repo.directory):
            raise Exception('No password repository exists at {}'.format(repo.directory))
        repo.private_key = crypto.PrivateKey.load(os.path.join(repo.directory, repo.PRIVATE_KEY_NAME))
        repo.public_key  = crypto.PublicKey.load(os.path.join(repo.directory, repo.PUBLIC_KEY_NAME))
        repo.database    = db.init(os.path.join(repo.directory, repo.DATABASE_NAME))
        return repo

    @classmethod
    def new(cls, filesystem_path):
        repository_path = os.path.join(filesystem_path, cls.FILESYSTEM_NAME)
        if os.path.exists(repository_path):
            raise Exception('Repository already exists at {}'.format(repository_path))
        os.mkdir(repository_path)
        repo = cls()
        repo.directory   = repository_path
        repo.private_key = crypto.PrivateKey.create(folder=repo.directory, filename=repo.PRIVATE_KEY_NAME)
        repo.public_key  = crypto.PublicKey.load(os.path.join(repo.directory, repo.PUBLIC_KEY_NAME))
        repo.database    = db.init(os.path.join(repo.directory, repo.DATABASE_NAME))
        db.Metadata.create_all(db.Model.Session.bind)
        return repo

    def save(self, path, value):
        exists = db.PasswordModel.query.get(path)
        if exists:
            raise Exception('Path {} already present in repository'.format(path))
        ciphertext = self.public_key.encrypt(value)
        record = db.PasswordModel.save(path, ciphertext)
        return record

    def show(self, path):
        records = db.PasswordModel.query.filter(db.PasswordModel.path.ilike('{}%'.format(path))).all()
        self.private_key.unseal()
        tree = ui.Node()
        for record in records:
            tree.add_value_by_path(record.path, self.private_key.decrypt(record.value))
        return tree.str()

    def list(self, path):
        records = db.PasswordModel.query.filter(db.PasswordModel.path.ilike('{}%'.format(path))).all()
        tree = ui.Node()
        if records:
            for record in records:
                tree.add_value_by_path(record.path, '*****')
            return tree.str()
        return ''

    def get(self, path):
        record = db.PasswordModel.query.get(path)
        if not record:
            raise Exception("Path {} doesn't exist in repository".format(path))
        self.private_key.unseal()
        return self.private_key.decrypt(record.value)

    def drop(self, path):
        record = db.PasswordModel.query.get(path)
        if not record:
            raise Exception("Path {} doesn't exist in repository".format(path))
        record.delete()

    def importPasswords(self, data):
        pass

    def exportPasswords(self, public_key_material):
        pass
