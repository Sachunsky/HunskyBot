from typing import Callable, Optional, Awaitable
from twitchAPI.chat.middleware import BaseCommandMiddleware
from twitchAPI.chat import ChatCommand

# .env
import os
from dotenv import find_dotenv, load_dotenv

# Loading .env file
envPath = find_dotenv()
load_dotenv(envPath)

# Load Environment Variables
TARGET_CHANNEL = os.getenv("CHANNEL")


class ModerationOnly(BaseCommandMiddleware):
   """This middleware is used to restrict command execution to moderators or the streamer only.

   Args:
       BaseCommandMiddleware : The Parent class for command middlewares.
   """
   # it is best practice to add this part of the init function to be compatible with the default middlewares
   # but you can also leave this out should you know you dont need it
   def __init__(self, execute_blocked_handler: Optional[Callable[[ChatCommand], Awaitable[None]]] = None):
     self.execute_blocked_handler = execute_blocked_handler

   async def can_execute(cmd: ChatCommand) -> bool:
      # add your own logic here, return True if the command should execute and False otherwise
      return cmd.user.mod or cmd.user.name == TARGET_CHANNEL

   async def was_executed(cmd: ChatCommand):
      # this will be called whenever a command this Middleware is attached to was executed, use this to update your internal state
      # since this is a basic example, we do nothing here
      pass
     
   
class VIPsOnly(BaseCommandMiddleware):
   """This middleware is used to restrict command execution to VIPs (or higher roles/priviliges) of the target Channel.

   Args:
       BaseCommandMiddleware : The Parent class for command middlewares.
   """
   # it is best practice to add this part of the init function to be compatible with the default middlewares
   # but you can also leave this out should you know you dont need it
   def __init__(self, execute_blocked_handler: Optional[Callable[[ChatCommand], Awaitable[None]]] = None):
     self.execute_blocked_handler = execute_blocked_handler

   async def can_execute(cmd: ChatCommand) -> bool:
      # add your own logic here, return True if the command should execute and False otherwise
      return cmd.user.vip or ModerationOnly.can_execute(cmd)

   async def was_executed(cmd: ChatCommand):
      # this will be called whenever a command this Middleware is attached to was executed, use this to update your internal state
      # since this is a basic example, we do nothing here
      pass
   
   
class SUBsOnly(BaseCommandMiddleware):
   """This middleware is used to restrict command execution to Subscribers (or higher roles/priviliges) of the target Channel.

   Args:
       BaseCommandMiddleware : The Parent class for command middlewares.
   """
   # it is best practice to add this part of the init function to be compatible with the default middlewares
   # but you can also leave this out should you know you dont need it
   def __init__(self, execute_blocked_handler: Optional[Callable[[ChatCommand], Awaitable[None]]] = None):
     self.execute_blocked_handler = execute_blocked_handler

   async def can_execute(cmd: ChatCommand) -> bool:
      # add your own logic here, return True if the command should execute and False otherwise
      return cmd.user.subscriber or VIPsOnly.can_execute(cmd)

   async def was_executed(cmd: ChatCommand):
      # this will be called whenever a command this Middleware is attached to was executed, use this to update your internal state
      # since this is a basic example, we do nothing here
      pass