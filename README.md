# Strava Frame

A Strava Dashboard I use on my Raspberry Pi frame. This code is not Raspbery Pi specific and I have tested it on Linux Mint and Windows 11 w/ WSL2.

![](./docs/dashboard.png)

## Setup

### 1. Install Python

I recommend **Python 3.11**.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
sudo apt update
sudo apt install python3-tk, python3-pil.imagetk
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

### 4. Grant `read_all` permission

1. Run the following to generate a new refresh token with `read_all` permission

```bash
chmod +x token.sh
./token.sh
```

2. You will be prompted to open a link in your browser. After opening the link, click "Authorize"

3. After clicking "Authorize", you will be redirected to an error page. Copy the value from the `code=` query parameter of the URL in the browser

4. Paste the value into your terminal. Copy the newly generated refresh token and replace the value in your `.env` file.

## Usage

```bash
python3 src/main.py
```

```bash
usage: main.py [-h] [-b] [-f] [-i]

options:
  -h, --help        show this help message and exit
  -b, --black       Use black accent color instead of orange
  -f, --fullscreen  Toggle fullscreen mode
```
