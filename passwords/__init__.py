import os

from prompt_toolkit import prompt

from . import db
from . import crypto
from . import ui


class Passwords(object):

    def __init__(self):
        self.repo = Repository.at(os.getcwd())

    @classmethod
    def init(cls):
        Repository.create(os.getcwd())

    def save(self, path):
        exists = PasswordModel.query.get(path)
        if exists:
            raise Exception('Path {} already present in repository'.format(path))
        plaintext = prompt('enter secret: ', is_password=True)
        ciphertext = self.repo.public_key.encrypt(plaintext)
        record = PasswordModel.save(path, ciphertext)
        return record

    def show(self, path):
        records = PasswordModel.query.filter(PasswordModel.path.ilike('{}%'.format(path))).all()
        self.repo.private_key.unseal()
        tree = ui.Node()
        for record in records:
            tree.add_value_by_path(record.path, self.repo.private_key.decrypt(record.value))
        return tree.str()


class PasswordModel(db.Model):

    __table__ = db.Table(
        'registry', db.Metadata,
        db.Column('path',  db.Unicode, primary_key=True),
        db.Column('value', db.Unicode))

    @classmethod
    def save(cls, path, ciphertext):
        record = cls(
            path=path,
            value=ciphertext)
        cls.Session.add(record)
        cls.Session.commit()
        return record


class Repository(object):

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
    def at(cls, directory):
        repo = cls()
        repo.directory   = os.path.join(directory, repo.FILESYSTEM_NAME)
        if not os.path.exists(repo.directory):
            raise Exception('No password repository exists at {}'.format(repo.directory))
        repo.private_key = crypto.PrivateKey.load(os.path.join(repo.directory, repo.PRIVATE_KEY_NAME))
        repo.public_key  = crypto.PublicKey.load(os.path.join(repo.directory, repo.PUBLIC_KEY_NAME))
        repo.database    = db.init(os.path.join(repo.directory, repo.DATABASE_NAME))
        return repo

    @classmethod
    def create(cls, filesystem_path):
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
