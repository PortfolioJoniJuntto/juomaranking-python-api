FROM public.ecr.aws/lambda/python:3.8

COPY handler.py ${LAMBDA_TASK_ROOT}/handler.py

COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

CMD [ "handler.handler" ]
