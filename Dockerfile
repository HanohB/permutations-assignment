FROM python:3

WORKDIR /usr/src/app

RUN pip install pandas
RUN pip install numpy
RUN pip install requests
RUN pip install openpyxl

COPY . .

CMD ["cars.py", "CarsData.xlsx"]

ENTRYPOINT ["python3"]