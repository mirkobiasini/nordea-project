## Nordea Coding Challenge

This project was developed by Mirko Biasini as a coding challenge for Nordea.
Below, a description of the system architecture, as well as a discussion of the main design chioces.

### Task
Create a RESTful service that can return cut-off1 times for currency pairs on a given date.
Example:
- CZK cannot be traded later than 11.00 today, and
- EUR cannot be traded later than 16.00 today, therefore,
- the cut-off time for today for the currency pair EUR/CZK is 11.00.

Acceptance criteria:
- The service should have a database where cut-off times are stored.
- Support the currencies and cut-off times provided in the table below.
- Expose an endpoint that returns the cut-off time for a currency pair on a particular date; the cut-off time for a currency pair is the earlier deadline.
- Implement the service in Java using Spring Boot.
- API must be documented.

#### Important note
During the first call, I was told by Troels that it's not important if I already know the technology (in this case Java).
We had a discussion about the fact that we, as engineers, are constantly learning, and we need to keep up to date as technology constantly changes.
Considering that I'm currently in very busy period due to the final deadlines of current job, I decided to solve this task in Python.
This choice was made to speed up the development and make sure I could deliver you something good in a reasonable time.
Although I do have experience in Java, Python was chosen as, together with Angular, it's the language I used the most in the last two years.

### System Architecture & Design Choices
The system presents two main components: an SQLite database and an API gateway.
The former is used to store the data for the cut-off time calculation. The latter exposes an API
endpoint that can return the cut-off time for a pair of currencies on a given date.
Additionally, a set of utilities functions was developed.
Finally, a test suite was created to test the API endpoints.

#### Database
For simplicity, SQLite was chosen to create the database. In a real case scenario, this would probably be replace by a PostgreSQL db, which offers better performance and capabilities.
The database comprises one table storing the following columns: iso, country, today, tomorrow, and after_tomorrow.
This tables stores the cut-off times for all supported currencies.

As there is a 1o1 relationship between a currency and a cut-off time, everything is stored in only one table.
However, in a broader scope, this would probably be expanded by storing one table for currencies and one table for cut-off times.
This would improve scalability.

As SQLite does not support a data type for dates, cut-off times are stored as text.
'Never possible' and 'Always possible' are converted to 'n' and 'a', respectively, to speed up computation time when executing checks.
In a real case scenario, where SQLite is replaced by a more powerful db like PostgreSQL, cut-off times would be store as date data type.

A class DB_Manager was created to manage the creation, population, and query of the database. To initialize the database, data were copied in a csv file.
This file is read when the database is populated. 

#### API Gateway
The API gateway was created with FastAPI, see documentation here: https://fastapi.tiangolo.com/.
The gateway comprises a middleware, and three API endpoints.

For the scope of this project, the middleware allows all origins and HTTP methods. This makes our endpoint more vulnerable to attacks.
Similarly, the endpoint is public and does not require authentication. In a real case, this could be improved by implementing a stricter CORS policy,
authentication, and rate limiting (e.g. to avoid DDOS).

There are three available endpoints: '/', '/ping', '/getCutOff'. The first two endpoints are for testing purposes. For example, '/ping' can be used to ping the server and check if it's alive.
'/getCutOff' returns the cut-off time for a currency pair and a date.
Currencies and date are passed via query params.

Input params are validated to make sure they follow the right format.
Currencies must be three upper case letters (e.g. EUR), whereas the date must be in the format YYYY-MM-DD (e.g. 2022-10-31).
If one or more param are missing or do not follow the right format, a 422 error response is returned.
Additionally, if a currency is passed in the right format but it is not supported (it's not in the db), a 404 error response is returned.
Finally, if an invalid date is passed, namely a date in the past, then a 422 error response is returned.

If all params are correct and supported, then a success response containing currencies info and related cut-off time is returned.
Note, a set of classes was created in ./api_schemas/ to define and handle request and response types.

#### Important design choice
Considering the following:
- The number of currencies in the world is limited and relatively small
- Cut-off times are not updated frequently

I decided to keep the cut-off time data in memory. As can be seen in app.py line 15, a dictionary containing all cut-off times is initialized when launching the server.
This is used to calculate the cut-off time for every request. By doing this, we significantly speed up the response time, as we do not need to query the database.

This is trade-off choice, where we are taking response time over memory. This introduces other problems to handle.
For example, if a cut-off time is updated in the database, we need to propagate this change to the dictionary in memory.
There are a bunch of variables to consider when making these choices. In this simple case, I preferred to have a faster response time at the cost of a higher memory usage.
In a case where the cut-off times take a lot of memory, this solution could be changed by having a cache that stores only the currencies that are requested more frequently.

Cut-off times are stored in the dictionary as float. 'Never possible' is converted to -inf, whereas 'Always possible' is converted to +inf.
Doing so, we speed up the calculation of the minimum cut-off time between two currencies.
Indeed, given two cut-off times, we simply need to find the minimum. 
Then, the final cut-off time is converted back to a readable format before returning the response.

#### Utilities
A set of utilities functions where defined in cut_off_times_utils.py.
This file contains helper functions that are used to convert cut-off times in different formats to improve efficiency.

#### Test Suite
A test suite was built to test all API endpoints, see ./test/test_api.py.
The suite tests every case for success and failure. For example, missing parameters, parameter in the wrong format or invalid, etc.

Note, some tests require a valid date (date not in the past) to work properly. Make sure the input the test is valid before executing. 

### How to execute the app
To run the app, execute the following:
- install all the required packages: `pip install -r requirements.txt`
- start the server: `uvicorn app:app --reload`
- the app is served at http://127.0.0.1:8000/
- send request, for example http://127.0.0.1:8000/getCutOff?currency_a=EUR&currency_b=USD&date=2022-10-31

Note, the first time the app is served, the database will be created and populated.