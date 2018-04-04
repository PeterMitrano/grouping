aws mturk create-hit \
  --lifetime-in-seconds=600 \
  --assignment-duration-in-seconds=3600 \
  --description='incidate grouping in short samples of music' \
  --title='Label Groups in Music' \
  --reward='1.50' \
  --max-assignments='10' \
  --question="`cat question.xml`" \
  --auto-approval-delay-in-seconds=14400 \
  --requester-annotation='pilot' \
  --qualification-requirements=??? \
  --endpoint-url="https://mturk-requester-sandbox.us-east-1.amazonaws.com"

