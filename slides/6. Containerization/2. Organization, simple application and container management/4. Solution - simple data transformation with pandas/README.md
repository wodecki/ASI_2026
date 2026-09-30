# README

To:

1. create an image, at the command line type:
   `docker build --tag app1 .`.

2. run the container so that you can view its contents and run programs inside it, at the command line type:
   `docker run -ti app1 bash`.
3. exit the container without stopping it, in its shell type.
    `exit`.
4. identify the running container, at the command line type. 
   `$ docker ps`
5. run the `app1.py` script in the working folder of the running container, at the command line type:
   `$ docker run -ti app1 python3 app1.py`.





