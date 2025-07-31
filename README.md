# jiocloud-cli

## Installation

```bash
python -m venv venv
```

for linux

```bash
source venv/bin/activate
```

for windows

```bash
venv/Scripts/activate
```

## Usage

### Login

```bash
python jiocloud.py login mobile --number 9876543210
```

### Login via cookie (Safe)

```bash
python jiocloud.py login cookie --value "cookie value from chrome dev tools where cookie name is u and value is a long string of text"

```

### Upload

```bash
python jiocloud.py upload file --path /path/to/file --encryption {true|false} --folder AABBCDEFGHIC
```

## Variables

- Cookie Value:

  - Login to jiocloud via web
  - open chrome dev tools
  - navigate to Application tab
  - Open Cookies and select https://jiocloud.com
  - look for cookie with name 'u' and value will be the long string of characters
  - Copy the whole value and paste it while loggin in via cookie

- Folder:
  - On JioCloud Web - go to `My Files`.
  - You will see the url to be `https://www.jiocloud.com/allfiles/AABBCDEFGHIJ`
  - The ID `AABBCDEFGHIJ` is your folder ID, use it to upload file to specific folder
