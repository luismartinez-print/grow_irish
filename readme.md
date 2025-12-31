# Itenerary Optimization ND Athletics


# Project Objective

The project consists of creating a prototype app where Notre Athletics
could optimize their traveling schedules via a dynamic programming
algorithm, also known as the Traveling Salesman problem.

It is known that traveling has a impact, often negative on athletes
performance, therefore it is in the backend management a optimized
traveling schedule with the minimum stress.

# Prototype Design

The framework used for the project was Streamlit, since it is easier to
deploy in your local computer and able to deploy in the cloud easily.

The programming style was Object Oriented Programming utilizing methods
for `Team` as a object manager of the objects `Travel` and `Player`
where individual travels where recorded.

Then in **app.py** the calls for the methods and all the UI presented in
the Streamlit app is shown.

# Google Cloud API

For the distances in the optimization problem, googlemaps and GeoCoding
was used to find quickly and on-demand for the user.
