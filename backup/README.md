# Backup and restore

## Mongodb dump
```bash
BACKUP_FILE="backup/game_database-$(date +\%F-\%T).gz"
mongodump --uri="mongodb://root:vimmlair@localhost:27017/game_database?directConnection=true&authSource=admin" --gzip --archive=$BACKUP_FILE
```

## Mongodb restore
```bash
mongorestore --uri="mongodb://root:vimmlair@localhost:27017/game_database?directConnection=true&authSource=admin" --gzip --archive=$BACKUP_FILE
```