# Strava Frame

A Strava Dashboard displayed on a Raspberry PI connected to an E-Ink display

![](./docs/dashboard_preview.png)

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

### 4. Generate Strava API tokens

1. Go to [Strava API Settings](https://www.strava.com/settings/api).
2. Create a new application if you haven’t already.
3. Copy the following values for your app:
   - **Client ID**
   - **Client Secret**
   - **Refresh Token**
4. Copy `.env-example` to `.env` and add your credentials

```bash
cp .env.example .env
```

```
STRAVA_CLIENT_ID=your_client_id
STRAVA_CLIENT_SECRET=your_client_secret
STRAVA_REFRESH_TOKEN=your_refresh_token
```

## Usage

```python
python3 src/main.py
```
