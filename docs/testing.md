
# testing

## Mailserver for testing

mailhog is small and all we need

    docker run --name mailtest -p 8025:8025 -p 1025:1025 mailhog/mailhog

## Rocket.Chat

    docker run --name db -d mongo:4.0 --smallfiles --replSet rs0 --oplogSize 128

    docker exec -ti db mongo --eval "printjson(rs.initiate())"

    docker run --name rocketchat -p 3000:3000 --link db --env ROOT_URL=http://localhost --env MONGO_OPLOG_URL=mongodb://db:27017/local -d rocket.chat
