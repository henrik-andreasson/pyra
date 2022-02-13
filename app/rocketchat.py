from flask import current_app
from rocketchat_API.rocketchat import RocketChat


class PyraRocketChatClient(object):

    def send_message_to_rocket_chat(self, message, channel=None):

        if channel is None:
            channel = current_app.config['ROCKET_CHANNEL']

        print("rocket sending is: %s" %
              current_app.config['ROCKET_ENABLED'])
        if current_app.config['ROCKET_ENABLED'] == 1:
            print("sending rocket message {} to {}".format(message, channel))
            rocket = RocketChat(current_app.config['ROCKET_USER'],
                                current_app.config['ROCKET_PASS'],
                                server_url=current_app.config['ROCKET_URL'])
            messageresult = rocket.chat_post_message(message,
                                                     channel=channel
                                                     )
            return messageresult

        else:
            return
