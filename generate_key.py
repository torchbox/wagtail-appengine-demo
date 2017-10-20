import random
''.join([random.SystemRandom().choice(
  'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
  ) for i in range(50)])
