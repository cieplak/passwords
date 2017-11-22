# passwords

Command line tool for storing passwords

## Usage

Create a password repository in the current directory:
```
passwords init
```

Save a password
```
passwords save namespace.scoped.by.periods.key1
```

Look up a password by path
```
passwords show namespace
```

## Development

Pre-requisites:
- python 3
- virtualenv
- pip
- ssh-keygen

```
virtualenv -p python3 ~/.virtualenvs/passwords
source ~/.virtualenvs/passwords/bin/activate
git clone https://github.com/cieplak/passwords.git
cd passwords
python setup.py develop
```
