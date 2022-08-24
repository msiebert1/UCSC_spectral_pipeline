Install
=======

These instructions have been tested for macOS with an intel chip.

Install the Docker desktop app
-------------------------------

The first step is to install the docker desktop application, which can be found
`here <https://docs.docker.com/get-docker/>`_ for mac, windows, and linux.
Running the pipeline with docker means that you won't have to install pipeline
dependencies locally.

Install and configure XQuarts
-----------------------------

You are going to need XQuartx to see IRAF GUI output.

1. Install XQuartz: https://www.xquartz.org/

2. Launch XQuartz. Under the XQuartz menu, select Preferences

3. Go to the security tab and ensure "Allow connections from network clients" is checked.

4. Restart your computer

Running the spectral pipeline
-----------------------------

Clone the pipline repository.

..  code::

    git clone https://github.com/astrophpeter/UCSC_spectral_pipeline

Navigate to docker directory.

.. code:: None

    cd docker/

Enable the docker container to forward to your machine so you can see the
IRAF GUI.

.. code:: None

    xhost +

Run the docker container.

.. code:: None

    docker compose run ucsc_spectral_pipeline_latest

This should bring you into the docker container. Here you can run pipeline tasks
with the required installs present. See :doc:`here <docker>` for details on
using the pipeline container.

Stopping the container
----------------------

It is important when you are finished using the docker container that you stop it
properly. This enables it to be started easily again.

To exit the container run,

.. code:: None

    exit

Then make sure you stop the container running with (whilst you are in the
:code:`docker/`) directory

.. code:: None

    docker compose down

Then make sure that you close your machine to connections with,

.. code:: None

    xhost -







