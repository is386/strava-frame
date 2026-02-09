# Strava Frame

A Strava Dashboard displayed on a Raspberry PI connected to a display

![](./docs/dashboard.png)

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

### 3. Generate Strava API tokens

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

Then fill in these values:
```
STRAVA_CLIENT_ID=your_client_id
STRAVA_CLIENT_SECRET=your_client_secret
STRAVA_REFRESH_TOKEN=your_refresh_token
```

## Usage

```bash
usage: main.py [-h] [-p] [-b] [-i]

options:
  -h, --help     show this help message and exit
  -p, --preview  Generate preview image
  -b, --black    Use black accent color instead of orange
  -i, --ink      Render dashboard for E-Ink displays
```
