FROM python:3.10-slim 

WORKDIR /workspace 

RUN apt-get update && apt-get install -y tzdata 

RUN pip install --uprade pip 

COPY ./requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt 

COPY ./ ./

CMD ["python", "trade.py", "--sp", "5", "--mp", "8", "--lp", "20", "--t", "15m", "--rsi", "14", "--s", "upbit"]