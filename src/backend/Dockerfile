# Use the official Python image as the base image
FROM python

# Set the working directory in the container to /app
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .
RUN apt-get update
#RUN apt-get install -y libgl1 ffmpeg flac
# Install the dependencies listed in the requirements file
RUN pip3 install --no-cache-dir -r requirements.txt
#RUN pip3 install torch --index-url https://download.pytorch.org/whl/cpu


# Copy the application code into the container
COPY . .

# Expose the port that the application will listen on
EXPOSE 8000

# Run the command to start the development server when the container launches
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8000", "--reload"]
