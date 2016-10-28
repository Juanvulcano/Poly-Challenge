# Poly-Challenge
Instructions:

1. Clone this repository

Script accepts two commands: --rebuild and --render int.
To render we need to have a database first. 

To create it:
2. python categories.py --rebuild

What happens if we try to build it again?
3. python categories.py --rebuild

Now let's render some data
4. python categories.py --render int

To see the output run:
python3 -m http.server

Go to localhost:port/int.html in your browser
