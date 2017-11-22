import codecs
from enum import Enum, auto
import os
import subprocess

from Crypto import Random as _Random
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
import msgpack
from prompt_toolkit import prompt


class PublicKey(object):

    def __init__(self):
        self.path = None
        self.pem_data = None
        self.rsa_key = None
        self.cipher = None

    def encrypt(self, plaintext):
        key, nonce, ciphertext = AESCipher.encrypt(plaintext)
        encrypted_key = self.cipher.encrypt(key)
        return Envelope.of(encrypted_key, nonce, ciphertext).serialize()

    @classmethod
    def load(cls, filesystem_path):
        key = cls()
        with open(filesystem_path) as fd:
            key.pem_data = fd.read()
        key.rsa_key = RSA.importKey(key.pem_data)
        key.cipher = PKCS1_OAEP.new(key.rsa_key)
        return key


class PrivateKey(object):

    class State(Enum):
        SEALED = auto()
        UNSEALED = auto()

    def __init__(self):
        self.path = None
        self.state = self.State.SEALED
        self.pem_data = None
        self.rsa_key = None
        self.cipher = None

    def decrypt(self, binary_message):
        if self.state == self.State.SEALED:
            raise Exception('Private key is sealed and cannot perform decryption')
        envelope = Envelope.parse(binary_message)
        aes_key = self.cipher.decrypt(envelope.encrypted_key)
        plaintext = AESCipher.decrypt(aes_key, envelope.nonce, envelope.ciphertext)
        return plaintext

    def unseal(self):
        display = 'passphrase for ' + self.path + ': '
        passphrase = prompt(display, is_password=True)
        self.rsa_key = RSA.importKey(self.pem_data, passphrase)
        self.cipher = PKCS1_OAEP.new(self.rsa_key)
        self.state = self.State.UNSEALED
        return self

    @classmethod
    def create(cls, folder, filename):
        filesystem_path = os.path.join(folder, filename)
        subprocess.call(['ssh-keygen', '-trsa', '-b4096', '-f{}'.format(filesystem_path)])
        key = cls()
        key.path = filesystem_path
        return key

    @classmethod
    def load(cls, filesytem_path):
        key = cls()
        key.path = filesytem_path
        with open(filesytem_path) as fd:
            key.pem_data = fd.read()
        return key


class AESCipher:

    BLOCK_SIZE = 16

    @classmethod
    def encrypt(cls, plaintext):
        raw = cls.pad(plaintext)
        key = cls.random_bytes(32)
        nonce = cls.random_bytes(16)
        cipher = AES.new(key, AES.MODE_CBC, nonce)
        ciphertext = cipher.encrypt(raw)
        return key, nonce, ciphertext

    @classmethod
    def decrypt(cls, key, nonce, ciphertext):
        cipher = AES.new(key, AES.MODE_CBC, nonce)
        plaintext = cipher.decrypt(ciphertext)
        return cls.unpad(plaintext)

    @classmethod
    def random_bytes(cls, n):
        return _Random.get_random_bytes(n)

    @classmethod
    def pad(cls, s):
        bs = cls.BLOCK_SIZE
        return (s + (bs - len(s) % bs) * chr(bs - len(s) % bs)).encode('utf-8')

    @classmethod
    def unpad(cls, s):
        s = s.decode('utf-8')
        return s[0:-ord(s[-1])]


class Envelope(object):

    def __init__(self):
        self.encrypted_key = None
        self.nonce = None
        self.ciphertext = None

    @classmethod
    def of(cls, encrypted_key, nonce, ciphertext):
        envelope = cls()
        envelope.encrypted_key = encrypted_key
        envelope.nonce = nonce
        envelope.ciphertext = ciphertext
        return envelope

    def serialize(self):
        msg = (self.encrypted_key, self.nonce, self.ciphertext)
        binary = msgpack.packb(msg)
        b64 = codecs.encode(binary, 'base64')
        return b64.decode('utf-8')

    @classmethod
    def parse(cls, utf8_base64_encoded_binary_message):
        base64 = codecs.encode(utf8_base64_encoded_binary_message, 'utf8')
        binary_message = codecs.decode(base64, 'base64')
        return Envelope.of(*msgpack.unpackb(binary_message))
