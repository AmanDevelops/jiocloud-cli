import argparse

from utils.login import user_login_via_cookie, user_login_via_mobile
from utils.upload import upload_file


def main():
    parser = argparse.ArgumentParser(prog="jiocloud")

    subparsers = parser.add_subparsers(description="command", required=True)

    # Login command

    login_parser = subparsers.add_parser("login")
    login_subparsers = login_parser.add_subparsers(dest="subcommand", required=True)

    # Login SubCommands
    mobile_parser = login_subparsers.add_parser("mobile")
    mobile_parser.add_argument("--number", required=True)
    mobile_parser.set_defaults(func=user_login_via_mobile)

    cookie_parser = login_subparsers.add_parser("cookie")
    cookie_parser.add_argument("--value", required=True)
    cookie_parser.set_defaults(func=user_login_via_cookie)


    # Upload Command

    upload_parser = subparsers.add_parser("upload")
    upload_subparsers = upload_parser.add_subparsers(dest="subcommand", required=True)

    file_upload_parser = upload_subparsers.add_parser("file")
    file_upload_parser.add_argument("--path", required=True)
    file_upload_parser.add_argument("--encryption", default='false')
    file_upload_parser.add_argument("--folder", required=True)


    file_upload_parser.set_defaults(func=upload_file)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)


if __name__ == "__main__":
    main()
