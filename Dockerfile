FROM continuumio/miniconda3:4.6.14

# Updating conda:
RUN conda update -n base -c defaults conda

# Try building the environment:
COPY environment.yml /tmp/environment.yml
RUN conda env create -f /tmp/environment.yml
RUN conda init bash
RUN echo "source activate template_serv" > ~/.bashrc
ENV PATH /opt/conda/envs/template_serv/bin:$PATH

# Copy application files:
COPY . /application/
WORKDIR /application/

# Install custom packages:
RUN pip install .

# Expose port:
EXPOSE 8000

# Create log directory:
RUN mkdir -p logs

# Upon firing up the container, the app starts:
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app","--log-level=debug","--access-logfile=logs/access.log","--error-logfile=logs/error.log"]
