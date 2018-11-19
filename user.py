#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import hashlib
try:
    import bcrypt
except ImportError:
    bcrypt = None
import random
import string

from trytond.model import ModelView, ModelSQL, fields

__all__ = ['User', 'UserParty']


class User(ModelSQL, ModelView):
    "Web User"
    __name__ = 'web.user'

    email = fields.Char('E-mail', required=True, select=True)
    password_hash = fields.Char('Password Hash')
    password = fields.Function(fields.Char('Password'), 'get_password',
        setter='set_password')
    parties = fields.Many2Many('web.user-party.party', 'user', 'party',
        'Parties')
    # TODO validate email

    @classmethod
    def __setup__(cls):
        super(User, cls).__setup__()
        cls._sql_constraints += [
            ('email_unique', 'UNIQUE(email)',
                'E-mail must be unique'),
            ]

    def get_password(self, name):
        return 'x' * 10

    @classmethod
    def set_password(cls, users, name, value):
        if value == 'x' * 10:
            return
        to_write = []
        for user in users:
            to_write.extend([[user], {
                        'password_hash': cls.hash_password(value),
                        }])
        cls.write(*to_write)

    @classmethod
    def copy(cls, users, default=None):
        return []

    @classmethod
    def authenticate(cls, email, password):
        users = cls.search([('email', 'ilike', email)])
        if not users:
            return
        user, = users
        if cls.check_password(password, user.password_hash):
            return user

    @staticmethod
    def hash_method():
        return 'bcrypt' if bcrypt else 'sha1'

    @classmethod
    def hash_password(cls, password):
        '''Hash password in the form
        <hash_method>$<password>$<salt>...'''
        if not password:
            return ''
        return getattr(cls, 'hash_' + cls.hash_method())(password)

    @classmethod
    def check_password(cls, password, hash_):
        if not hash_:
            return False
        hash_method = hash_.split('$', 1)[0]
        return getattr(cls, 'check_' + hash_method)(password, hash_)

    @classmethod
    def hash_sha1(cls, password):
        if isinstance(password, unicode):
            password = password.encode('utf-8')
        salt = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        hash_ = hashlib.sha1(password + salt).hexdigest()
        return '$'.join(['sha1', hash_, salt])

    @classmethod
    def check_sha1(cls, password, hash_):
        if isinstance(password, unicode):
            password = password.encode('utf-8')
        if isinstance(hash_, unicode):
            hash_ = hash_.encode('utf-8')
        hash_method, hash_, salt = hash_.split('$', 2)
        assert hash_method == 'sha1'
        return hash_ == hashlib.sha1(password + salt).hexdigest()

    @classmethod
    def hash_bcrypt(cls, password):
        if isinstance(password, unicode):
            password = password.encode('utf-8')
        hash_ = bcrypt.hashpw(password, bcrypt.gensalt())
        return '$'.join(['bcrypt', hash_])

    @classmethod
    def check_bcrypt(cls, password, hash_):
        if isinstance(password, unicode):
            password = password.encode('utf-8')
        if isinstance(hash_, unicode):
            hash_ = hash_.encode('utf-8')
        hash_method, hash_ = hash_.split('$', 1)
        assert hash_method == 'bcrypt'
        return hash_ == bcrypt.hashpw(password, hash_)

    # TODO create session


class UserParty(ModelSQL):
    'User - Party'
    __name__ = 'web.user-party.party'
    user = fields.Many2One('web.user', 'User', ondelete='CASCADE', select=True,
        required=True)
    party = fields.Many2One('party.party', 'Party', ondelete='CASCADE',
        select=True, required=True)
