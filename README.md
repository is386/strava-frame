# Strava Frame

A Strava Dashboard displayed on a Raspberry PI connected to an E-Ink display

## Setup

Follow these steps to prepare the project for development.

### 1. Install Python

I recommend **Python 3.11**. Using [pyenv](https://github.com/pyenv/pyenv) is recommended:

```bash
pyenv install 3.11.7
pyenv local 3.11.7
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Waveshare e-Paper Driver

```bash
git clone https://github.com/waveshare/e-Paper.git
cd e-Paper/RaspberryPi_JetsonNano/python
sudo python3 setup.py install
```
